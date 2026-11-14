#!/usr/bin/env python3
"""
olivian.xerox.py — Olivian: blockchain data analysis, monitoring &
outsider-lockout daemon for a private/test network.

Components
----------
1. ChainMonitor       — polls a private/test network RPC endpoint, tracks
                        new blocks & transactions, and flags anomalous flows
                        (value spikes, unusual sender/receiver concentration,
                        sudden gas anomalies).
2. ReverseRpcProxy    — a local JSON-RPC proxy in front of your node.
                        Enforces:
                          * API-key allowlist          (X-API-Key header)
                          * IP allowlist / blocklist
                          * Per-client rate limiting
                          * Automatic ban on abuse (too many 4xx/429s)
                        Outsiders are locked out; only allowlisted clients pass.
3. Alerter            — sends email and/or webhook alerts when anomalies or
                        lockouts occur.

Config lives in `OLIVIAN_CONFIG` below, or set OLIVIAN_CONFIG_JSON to point
to a JSON config file. Standard library only — no third-party deps.

Run:
    python3 olivian.xerox.py            # start proxy + monitor daemon
    python3 olivian.xerox.py --once     # single monitoring pass, no proxy
    python3 olivian.xerox.py --test     # self-test with synthetic blocks
"""

from __future__ import annotations

import argparse
import json
import logging
import signal
import statistics
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import defaultdict, deque
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Optional

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

DEFAULT_CONFIG: dict[str, Any] = {
    # RPC node of your private/test network
    "upstream_rpc_url": "http://127.0.0.1:8545",
    # Where the protective proxy listens
    "proxy_host": "127.0.0.1",
    "proxy_port": 8546,
    # API keys allowed through (empty => key check disabled)
    "api_keys": ["change-me"],
    # IP allowlist (empty => all allowed), then blocklist applied on top
    "ip_allowlist": [],
    "ip_blocklist": [],
    # Rate limiting
    "rate_limit_per_minute": 600,
    "ban_threshold_429_per_5min": 3,      # 3 rate-limit hits in 5 min => ban
    "ban_seconds": 3600,
    # Monitoring
    "poll_interval_seconds": 5,
    "confirmations": 3,
    # Anomaly detection
    "value_spike_zscore": 4.0,            # tx value far above rolling mean
    "gas_spike_zscore": 4.0,
    "min_history": 20,                    # blocks of history before alerting
    "max_tx_per_block": 5000,             # block flooding alert
    # Alerts
    "alert_log_file": "olivian.log",
    "webhook_url": "",                    # POSTs JSON alert; empty = off
    "email": {
        "enabled": False,
        "smtp_host": "smtp.example.com",
        "smtp_port": 587,
        "username": "",
        "password": "",                   # use env: OLIVIAN_SMTP_PASSWORD
        "from_addr": "olivian@example.com",
        "to_addrs": ["you@example.com"],
    },
}


def load_config() -> dict[str, Any]:
    cfg = dict(DEFAULT_CONFIG)
    import os

    path = os.environ.get("OLIVIAN_CONFIG_JSON")
    if path:
        with open(path, "r", encoding="utf-8") as fh:
            cfg.update(json.load(fh))
    pw = os.environ.get("OLIVIAN_SMTP_PASSWORD")
    if pw:
        cfg["email"]["password"] = pw
    return cfg


# --------------------------------------------------------------------------
# Logging & alerts
# --------------------------------------------------------------------------

class Alerter:
    """Central alert fan-out: log file, console, webhook, email."""

    def __init__(self, cfg: dict[str, Any], logger: logging.Logger) -> None:
        self.cfg = cfg
        self.log = logger
        self._seen_recent: deque[tuple[str, float]] = deque(maxlen=200)

    def alert(self, kind: str, message: str, data: Optional[dict] = None) -> None:
        """Deduplicate repeats within 60s, then fan out."""
        now = time.time()
        key = f"{kind}:{message}"
        if any(k == key and now - t < 60 for k, t in self._seen_recent):
            return
        self._seen_recent.append((key, now))

        payload = {"kind": kind, "message": message,
                   "data": data or {}, "ts": now}
        self.log.warning("ALERT [%s] %s %s", kind, message, data or "")
        if self.cfg.get("webhook_url"):
            threading.Thread(target=self._post_webhook, args=(payload,),
                            daemon=True).start()
        if self.cfg.get("email", {}).get("enabled"):
            threading.Thread(target=self._send_email, args=(kind, message),
                            daemon=True).start()

    def _post_webhook(self, payload: dict) -> None:
        try:
            req = urllib.request.Request(
                self.cfg["webhook_url"],
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(req, timeout=10)
        except Exception as exc:  # noqa: BLE001
            self.log.error("webhook failed: %s", exc)

    def _send_email(self, kind: str, message: str) -> None:
        e = self.cfg["email"]
        try:
            import smtplib
            from email.message import EmailMessage

            msg = EmailMessage()
            msg["Subject"] = f"[Olivian] {kind}: {message}"
            msg["From"] = e["from_addr"]
            msg["To"] = ", ".join(e["to_addrs"])
            msg.set_content(f"Olivian alert\n\n{kind}: {message}\n")
            with smtplib.SMTP(e["smtp_host"], e["smtp_port"], timeout=15) as s:
                s.starttls()
                s.login(e["username"], e["password"])
                s.send_message(msg)
        except Exception as exc:  # noqa: BLE001
            self.log.error("email failed: %s", exc)


# --------------------------------------------------------------------------
# RPC client
# --------------------------------------------------------------------------

class RpcClient:
    def __init__(self, url: str, logger: logging.Logger) -> None:
        self.url = url
        self.log = logger
        self._id = 0

    def call(self, method: str, params: list[Any] = None) -> Any:
        self._id += 1
        body = json.dumps({"jsonrpc": "2.0", "id": self._id,
                           "method": method, "params": params or []}).encode()
        req = urllib.request.Request(self.url, data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            out = json.loads(resp.read())
        if "error" in out:
            raise RuntimeError(f"RPC error: {out['error']}")
        return out.get("result")

    def latest_block_number(self) -> int:
        return int(self.call("eth_blockNumber"), 16)

    def block_by_number(self, n: int, full: bool = True) -> Optional[dict]:
        return self.call("eth_getBlockByNumber", [hex(n), full])


def wei_to_eth(wei: Any) -> float:
    try:
        return int(wei) / 1e18
    except (TypeError, ValueError):
        return 0.0


# --------------------------------------------------------------------------
# Anomaly detection
# --------------------------------------------------------------------------

@dataclass
class BlockStats:
    number: int
    n_tx: int
    total_value_eth: float
    mean_value_eth: float
    gas_used: int
    gas_limit: int
    top_senders: list[tuple[str, int]]
    top_receivers: list[tuple[str, int]]


class AnomalyDetector:
    """Statistical anomaly detection over rolling block history."""

    def __init__(self, cfg: dict[str, Any]) -> None:
        self.cfg = cfg
        self.history: deque[BlockStats] = deque(maxlen=256)
        self.addr_window: deque[set[str]] = deque(maxlen=20)

    def stats_for(self, block: dict) -> BlockStats:
        txs = block.get("transactions", []) or []
        values = [wei_to_eth(t.get("value", 0)) for t in txs
                  if isinstance(t, dict)]
        senders: dict[str, int] = defaultdict(int)
        receivers: dict[str, int] = defaultdict(int)
        for t in txs:
            if isinstance(t, dict):
                senders[t.get("from", "?")] += 1
                receivers[t.get("to", "?")] += 1
        return BlockStats(
            number=int(block["number"], 16),
            n_tx=len(txs),
            total_value_eth=sum(values),
            mean_value_eth=statistics.fmean(values) if values else 0.0,
            gas_used=int(block.get("gasUsed", "0x0"), 16),
            gas_limit=int(block.get("gasLimit", "0x0"), 16),
            top_senders=sorted(senders.items(), key=lambda kv: -kv[1])[:5],
            top_receivers=sorted(receivers.items(), key=lambda kv: -kv[1])[:5],
        )

    def _z(self, value: float, hist: list[float]) -> float:
        if len(hist) < 2:
            return 0.0
        sd = statistics.pstdev(hist)
        if sd == 0:
            return 0.0
        return (value - statistics.fmean(hist)) / sd

    def check(self, stats: BlockStats, alerter: Alerter) -> list[str]:
        """Run all checks; returns list of anomaly descriptions found."""
        anomalies: list[str] = []
        cfg = self.cfg
        self.history.append(stats)
        if len(self.history) < cfg["min_history"]:
            return anomalies  # warming up

        hist = list(self.history)
        prev = hist[:-1]

        # 1. Block-level value spike
        z = self._z(stats.total_value_eth, [h.total_value_eth for h in prev])
        if z >= cfg["value_spike_zscore"]:
            msg = f"Block {stats.number}: total value spike (z={z:.1f}, {stats.total_value_eth:.4f} ETH)"
            anomalies.append(msg)
            alerter.alert("value_spike", msg,
                          {"block": stats.number, "z": round(z, 2),
                           "total_eth": stats.total_value_eth})

        # 2. Gas usage anomaly / near-full blocks
        z = self._z(stats.gas_used, [h.gas_used for h in prev])
        if z >= cfg["gas_spike_zscore"]:
            msg = f"Block {stats.number}: gas usage spike (z={z:.1f})"
            anomalies.append(msg)
            alerter.alert("gas_spike", msg,
                          {"block": stats.number, "z": round(z, 2),
                           "gas_used": stats.gas_used})

        # 3. Transaction flooding
        if stats.n_tx > cfg["max_tx_per_block"]:
            msg = f"Block {stats.number}: tx flooding ({stats.n_tx} txs)"
            anomalies.append(msg)
            alerter.alert("tx_flood", msg, {"block": stats.number,
                                             "n_tx": stats.n_tx})

        # 4. Address concentration: same sender dominating recent blocks
        self.addr_window.append({a for a, _ in stats.top_senders})
        if len(self.addr_window) >= 10:
            counts: dict[str, int] = defaultdict(int)
            for s in self.addr_window:
                for a in s:
                    counts[a] += 1
            for addr, n in counts.items():
                if n >= 8:  # in top senders for 8 of last 10 blocks
                    msg = f"Address {addr} dominates recent blocks ({n}/10)"
                    anomalies.append(msg)
                    alerter.alert("addr_concentration", msg,
                                  {"address": addr, "window": n})

        # 5. Zero-value spam burst (many txs, near-zero total value)
        if stats.n_tx > 3 * statistics.fmean([h.n_tx for h in prev]) and \
           stats.total_value_eth < 1e-9 and stats.n_tx > 10:
            msg = f"Block {stats.number}: zero-value spam burst ({stats.n_tx} txs)"
            anomalies.append(msg)
            alerter.alert("spam_burst", msg,
                          {"block": stats.number, "n_tx": stats.n_tx})

        return anomalies


# --------------------------------------------------------------------------
# Chain monitor
# --------------------------------------------------------------------------

class ChainMonitor:
    def __init__(self, cfg: dict[str, Any], alerter: Alerter,
                 logger: logging.Logger) -> None:
        self.cfg = cfg
        self.alerter = alerter
        self.log = logger
        self.rpc = RpcClient(cfg["upstream_rpc_url"], logger)
        self.detector = AnomalyDetector(cfg)
        self.last_processed = -1
        self.running = False

    def poll_once(self) -> list[str]:
        """Fetch new blocks up to latest-minus-confirmations, analyze them."""
        found: list[str] = []
        latest = self.rpc.latest_block_number()
        safe = latest - self.cfg["confirmations"]
        if safe <= self.last_processed:
            return found
        start = max(self.last_processed + 1, safe - self.detector.history.maxlen // 2)
        for n in range(start, safe + 1):
            block = self.rpc.block_by_number(n, full=True)
            if block is None:
                continue
            stats = self.detector.stats_for(block)
            found.extend(self.detector.check(stats, self.alerter))
            self.last_processed = n
        self.log.info("processed up to block %d (latest %d)",
                      self.last_processed, latest)
        return found

    def run(self) -> None:
        self.running = True
        while self.running:
            try:
                self.poll_once()
            except Exception as exc:  # noqa: BLE001
                self.log.error("monitor error: %s", exc)
                self.alerter.alert("monitor_error", str(exc))
            time.sleep(self.cfg["poll_interval_seconds"])

    def stop(self) -> None:
        self.running = False

    def feed_synthetic(self, block: dict) -> list[str]:
        """Test hook: analyze a synthetic block without a live node."""
        stats = self.detector.stats_for(block)
        return self.detector.check(stats, self.alerter)


def synthetic_block(number: int, n_tx: int, value_wei_each: int = 0) -> dict:
    return {
        "number": hex(number),
        "gasUsed": hex(30_000 * max(n_tx, 1)),
        "gasLimit": hex(30_000_000),
        "transactions": [
            {"from": f"0x{'a' * 39}{i:x}", "to": f"0x{'b' * 39}{i:x}",
             "value": value_wei_each}
            for i in range(n_tx)
        ],
    }


# --------------------------------------------------------------------------
# Protective RPC proxy (outsider lockout)
# --------------------------------------------------------------------------

@dataclass
class ClientState:
    hits: deque = field(default_factory=lambda: deque(maxlen=600))
    rate_429: deque = field(default_factory=deque)
    banned_until: float = 0.0


class AccessController:
    """API-key allowlist, IP allow/blocklists, rate limit, auto-ban."""

    def __init__(self, cfg: dict[str, Any]) -> None:
        self.cfg = cfg
        self.clients: dict[str, ClientState] = defaultdict(ClientState)
        self._lock = threading.Lock()

    def check(self, ip: str, api_key: str) -> tuple[bool, int, str]:
        """Return (allowed, http_status, reason)."""
        cfg = self.cfg
        with self._lock:
            st = self.clients[ip]

            if cfg["ip_allowlist"] and ip not in cfg["ip_allowlist"]:
                return False, 403, "ip not allowlisted"
            if ip in cfg["ip_blocklist"]:
                return False, 403, "ip blocklisted"
            if cfg["api_keys"] and api_key not in cfg["api_keys"]:
                return False, 401, "invalid api key"
            if time.time() < st.banned_until:
                return False, 403, "banned"

            # Rate limit (sliding window)
            now = time.time()
            while st.hits and now - st.hits[0] > 60:
                st.hits.popleft()
            if len(st.hits) >= cfg["rate_limit_per_minute"]:
                st.rate_429.append(now)
                window = cfg["ban_threshold_429_per_5min"]
                while st.rate_429 and now - st.rate_429[0] > 300:
                    st.rate_429.popleft()
                if len(st.rate_429) >= window:
                    st.banned_until = now + cfg["ban_seconds"]
                    return False, 403, "banned: abuse threshold exceeded"
                return False, 429, "rate limit exceeded"
            st.hits.append(now)
        return True, 200, "ok"


class ReverseRpcProxy:
    def __init__(self, cfg: dict[str, Any], alerter: Alerter,
                 logger: logging.Logger) -> None:
        self.cfg = cfg
        self.alerter = alerter
        self.log = logger
        self.access = AccessController(cfg)
        upstream = cfg["upstream_rpc_url"]
        proxy = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:  # noqa: N802
                key = self.headers.get("X-API-Key", "")
                ip = self.client_address[0]
                allowed, status, reason = proxy.access.check(ip, key)
                if not allowed:
                    proxy.log.info("LOCKOUT %s -> %s (%s)", ip, status, reason)
                    proxy.alerter.alert("lockout", f"{ip} locked out ({reason})",
                                        {"ip": ip, "status": status})
                    self.send_error(status, reason)
                    return
                try:
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length)
                    req = urllib.request.Request(
                        upstream, data=body,
                        headers={"Content-Type": "application/json"})
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        payload = resp.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(payload)))
                    self.end_headers()
                    self.wfile.write(payload)
                except Exception as exc:  # noqa: BLE001
                    proxy.log.error("upstream error: %s", exc)
                    self.send_error(502, "upstream error")

            def log_message(self, fmt: str, *args: Any) -> None:
                proxy.log.debug("http: " + fmt, *args)

        self.server = ThreadingHTTPServer((cfg["proxy_host"], cfg["proxy_port"]),
                                          Handler)

    def serve_forever(self) -> None:
        self.log.info("proxy listening on %s:%d (upstream %s)",
                      self.cfg["proxy_host"], self.cfg["proxy_port"],
                      self.cfg["upstream_rpc_url"])
        self.server.serve_forever()

    def shutdown(self) -> None:
        self.server.shutdown()


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def setup_logging(cfg: dict[str, Any]) -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(cfg["alert_log_file"]),
        ],
    )
    return logging.getLogger("olivian")


def self_test(cfg: dict[str, Any]) -> None:
    logger = setup_logging(cfg)
    alerter = Alerter(cfg, logger)
    mon = ChainMonitor(cfg, alerter, logger)
    # Warm up history with calm blocks, then send one wild block.
    for i in range(cfg["min_history"] + 2):
        mon.feed_synthetic(synthetic_block(i, 10, value_wei_each=10**15))
    anomalies = mon.feed_synthetic(
        synthetic_block(cfg["min_history"] + 2, 9999, value_wei_each=10**18))
    print("Warm-up done. Anomalies detected in final block:")
    for a in anomalies:
        print("  -", a)
    if not anomalies:
        print("  (none — thresholds may need tuning)")
    # Access controller checks
    ac = AccessController(cfg)
    ok, s, _ = ac.check("10.0.0.1", cfg["api_keys"][0])
    print(f"\nAccess check (good key): allowed={ok} status={s}")
    ok, s, r = ac.check("10.0.0.1", "bad-key")
    print(f"Access check (bad key):  allowed={ok} status={s} ({r})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Olivian daemon")
    parser.add_argument("--once", action="store_true",
                        help="single monitoring pass, no proxy")
    parser.add_argument("--test", action="store_true",
                        help="run offline self-test with synthetic blocks")
    args = parser.parse_args()

    cfg = load_config()
    logger = setup_logging(cfg)

    if args.test:
        self_test(cfg)
        return

    alerter = Alerter(cfg, logger)
    monitor = ChainMonitor(cfg, alerter, logger)

    if args.once:
        anomalies = monitor.poll_once()
        for a in anomalies:
            print("  -", a)
        return

    proxy = ReverseRpcProxy(cfg, alerter, logger)
    threading.Thread(target=proxy.serve_forever, daemon=True).start()

    def on_sig(_sig: int, _frm: Any) -> None:
        logger.info("shutting down")
        monitor.stop()
        proxy.shutdown()

    signal.signal(signal.SIGINT, on_sig)
    signal.signal(signal.SIGTERM, on_sig)

    logger.info("Olivian daemon started")
    monitor.run()


if __name__ == "__main__":
    main()
