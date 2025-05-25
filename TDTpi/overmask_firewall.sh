#!/data/data/com.termux/files/usr/bin/bash
# TGDK :: OVERMASK FIREWALL v1.1
# BFE-TGDK-OVERMASK-001 :: Trideotaxis DNS Blocker + MAC Monitor + OliviaAI Sync

BLOCKLIST="$HOME/.overmask/overmask.block"
HOSTSFILE="$HOME/.overmask/hosts.override"
REALHOSTS="/data/data/com.termux/files/usr/etc/hosts"
LOGFILE="$HOME/.overmask/overmask.log"
TRIFILE="$HOME/.overmask/overmask.trideotaxis"
DNS_SERVER="127.0.0.1"

mkdir -p "$HOME/.overmask"

function log_event() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOGFILE"
}

function phi_dex_fold() {
  domain=$1
  sum=0
  for (( i=0; i<${#domain}; i++ )); do
    c=$(printf "%d" "'${domain:$i:1}")
    sum=$((sum + c))
  done
  phi=$((sum % 5))
  dex=$(( (sum * phi + 3) % 6 ))
  echo "Φ${phi}-Δ${dex}"
}

function init_blocklist() {
  log_event "Initializing Overmask blocklist with Trideotaxis codes..."
  cat > "$BLOCKLIST" <<EOF
facebook.com
instagram.com
tiktok.com
doubleclick.net
ads.google.com
api.segment.io
graph.facebook.com
EOF
  > "$TRIFILE"
  while read domain; do
    code=$(phi_dex_fold "$domain")
    echo "$domain :: $code" >> "$TRIFILE"
  done < "$BLOCKLIST"
  log_event "Trideotaxis entropy analysis complete."
}

function generate_hosts_override() {
  log_event "Generating custom hosts override..."
  echo "127.0.0.1 localhost" > "$HOSTSFILE"
  while read domain; do
    echo "127.0.0.1 $domain" >> "$HOSTSFILE"
    echo "::1 $domain" >> "$HOSTSFILE"
  done < "$BLOCKLIST"
}

function apply_hosts() {
  log_event "Applying hosts override..."
  cp "$HOSTSFILE" "$REALHOSTS"
  log_event "Overmask firewall ACTIVE. DNS rerouted."
}

function update_blocklist_olivia() {
  log_event "Querying OliviaAI for dynamic threat list..."
  OLIVIA_URL="https://olivia-tgdk.com/api/firewall/blocklist"
  curl -s "$OLIVIA_URL" > "$BLOCKLIST"
  log_event "Blocklist synced. Recalculating entropy..."
  > "$TRIFILE"
  while read domain; do
    code=$(phi_dex_fold "$domain")
    echo "$domain :: $code" >> "$TRIFILE"
  done < "$BLOCKLIST"
  generate_hosts_override
  apply_hosts
}

function watch_dns() {
  log_event "Watching DNS activity..."
  termux-wifi-connectioninfo | tee -a "$LOGFILE"
  lsof -i | grep :53 | tee -a "$LOGFILE"
}

function check_mac_behavior() {
  log_event "Scanning MAC interfaces..."
  ip addr show | grep "ether" | tee -a "$LOGFILE"
}

function overmask_loop() {
  log_event "Overmask Guardian Loop Initiated :: Trideotaxis Enabled"
  while true; do
    watch_dns
    check_mac_behavior
    sleep 120
  done
}

function show_help() {
  echo "Usage: ./overmask_firewall.sh [--init | --loop | --update]"
  echo "  --init    :: Initialize and apply firewall with Trideotaxis"
  echo "  --loop    :: Run Overmask scan loop"
  echo "  --update  :: Sync blocklist and re-fold entropy codes"
}

case "$1" in
  --init)
    init_blocklist
    generate_hosts_override
    apply_hosts
    ;;
  --loop)
    overmask_loop
    ;;
  --update)
    update_blocklist_olivia
    ;;
  *)
    show_help
    ;;
esac