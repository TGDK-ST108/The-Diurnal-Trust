#!/usr/bin/env python3
"""
OliviaAI TGDK + Excessive Panther WIRED — GLASSES ALWAYS-ON MODE (no placeholders)
Panther governs 7 Layer + Duododecahedron + Reflux + Meta AI
EVERY path (MCP tools + HTTP endpoints) routes through the Meta AI Glasses pipeline:
  Panther -> Meta AI -> 7 Layer -> Duododecahedron -> Reflux

Requirements:
  pip install fastapi uvicorn "mcp[cli]" starlette meta-ai-api
  (meta-ai-api = Strvm's Meta AI wrapper: real Llama responses, NO API KEY needed.
   Optional: set META_AI_COOKIES env var with your meta.ai browser cookies (JSON)
   for authenticated features like image generation / longer history.)

Run: uvicorn app_both_ways_wired:app --host 0.0.0.0 --port 8000 --no-reload
"""
import os, sys, json, time, math, hashlib, asyncio, threading
from pathlib import Path
from collections import Counter
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict
sys.path.insert(0, str(Path(__file__).parent))

# --- GLASSES ALWAYS-ON CONFIG ---
GLASSES_ALWAYS_ON = True   # Master switch. Every request flows through Meta AI Glasses.
GLASSES_RUN_7LAYER = True
GLASSES_RUN_DUDO = True
GLASSES_RUN_REFLUX = True   # Reflux runs on EVERY glasses cycle

REFLUX_DIR = Path("reflux_sessions")

# --- MCP ---
try:
    from mcp.server.fastmcp import FastMCP as MCPClass
    MCP_VERSION="v1 FastMCP"
except:
    try:
        from mcp.server import MCPServer as MCPClass
        MCP_VERSION="v2 MCPServer"
    except:
        class DummyMCP:
            def __init__(self,n): self.name=n
            def tool(self):
                def dec(fn): return fn
                return dec
            def run(self): pass
        MCPClass=DummyMCP
        MCP_VERSION="dummy"
mcp = MCPClass("trickster-wired")

# ========== PANTHER ==========
PHI = (1 + 5**0.5)/2
INV_PHI = 1/PHI
INV_PHI2 = INV_PHI**2
TAU = 2*math.pi

@dataclass
class PhiWeightedPolicy:
    name: str; raw_weights: Tuple[float,float,float]=(1.0,1.0,1.0)
    @property
    def normalized(self):
        s=sum(self.raw_weights); return tuple(w/s for w in self.raw_weights)
    def weight_for(self, p): return {"implicate":self.normalized[0],"perform":self.normalized[1],"reduce":self.normalized[2]}.get(p,0.333)
    def adjust(self, base, phase): return min(base*(0.85+self.weight_for(phase)*PHI*0.35),1.0)

def make_phi_policy(n):
    nl=n.lower()
    if "cold" in nl: raw=(INV_PHI2,INV_PHI,1.0)
    elif "hot" in nl or "fast" in nl: raw=(INV_PHI2,1.0,INV_PHI)
    elif "deep" in nl: raw=(1.0,INV_PHI,INV_PHI2)
    else: raw=(1.0,1.0,1.0)
    return PhiWeightedPolicy(name=n, raw_weights=raw)

def compute_stability(spec):
    s=spec.state.lower(); st=1.0
    if "unstable" in s: st-=0.35
    if "strong" in s: st+=0.15
    if "adapt" in s: st+=0.10
    st-=len(spec.risks)*0.05
    return max(0.1,min(st,1.3))

@dataclass
class StaldwellInput:
    query: str; state: str; target: str
    procedure: List[str]=field(default_factory=list)
    assets: List[str]=field(default_factory=list)
    risks: List[str]=field(default_factory=list)
    constraints: List[str]=field(default_factory=list)

class StaldwellIPR:
    def __init__(self, policy="auto"):
        self.policy=make_phi_policy(policy) if policy!="auto" else make_phi_policy("Balanced-Phi")
    def process(self, spec):
        bi=0.72+(0.08 if spec.assets else 0); bp=0.70+(0.10 if "strong" in spec.state.lower() else 0)+(0.07 if spec.procedure else 0); br=0.75
        comp = self.policy.adjust(bi,"implicate")*self.policy.weight_for("implicate") + self.policy.adjust(bp,"perform")*self.policy.weight_for("perform") + self.policy.adjust(br,"reduce")*self.policy.weight_for("reduce")
        return {"composite": round(comp,4), "stability": round(compute_stability(spec),4), "policy": self.policy.name}

class ExcessivePanther:
    def __init__(self):
        self.policies=[make_phi_policy(n) for n in ["ColdSmart-Phi","HotFast-Phi","DeepImplicate-Phi","Balanced-Phi"]]
        self.growth_log=[]
    def enforce_growth(self, query, state, target, procedure, assets, risks):
        spec=StaldwellInput(query, state, target, procedure, assets, risks)
        results=[(p.name, StaldwellIPR(p.name).process(spec)) for p in self.policies]
        min_comp=min(r[1]["composite"] for r in results)
        stable=compute_stability(spec)
        passed = min_comp >= 0.82 and stable >= 0.6
        rec={"timestamp":time.time(),"query":query,"target":target,"min_composite":min_comp,"all_composites":{n:r["composite"] for n,r in results},"stability":stable,"passed":passed,"can_grow":passed,"rollback":not passed,"details":results}
        self.growth_log.append(rec)
        return rec

panther=ExcessivePanther()

# ========== REAL META AI BACKEND (meta-ai-api, no API key required) ==========
try:
    from meta_ai_api import MetaAI as _MetaAIClient
    HAS_META_AI_SDK=True
except Exception as e:
    _MetaAIClient=None; HAS_META_AI_SDK=False
    print(f"[WARN] meta-ai-api not installed: {e} — run: pip install meta-ai-api")

_META_LOCK=threading.Lock()          # one in-flight prompt per client instance
_META_CLIENT: Optional[Any]=None

def _build_meta_client():
    cookies_raw=os.environ.get("META_AI_COOKIES")   # optional: JSON cookie dict for authenticated features
    cookies=None
    if cookies_raw:
        try: cookies=json.loads(cookies_raw)
        except Exception as e: print(f"[WARN] META_AI_COOKIES not valid JSON: {e}")
    if cookies:
        return _MetaAIClient(cookies=cookies)
    return _MetaAIClient()

def _get_meta_client():
    global _META_CLIENT
    with _META_LOCK:
        if _META_CLIENT is None:
            _META_CLIENT=_build_meta_client()
        return _META_CLIENT

async def call_meta_ai_backend(prompt: str, session_id: str) -> str:
    """
    Real Meta AI (Llama, behind meta.ai) via the meta-ai-api package.
    No API key. Optional cookies via META_AI_COOKIES env var.
    Blocking SDK call is offloaded to a thread so the event loop never stalls.
    """
    if not HAS_META_AI_SDK:
        raise RuntimeError("meta-ai-api is not installed (pip install meta-ai-api)")
    client=_get_meta_client()
    def _do_prompt():
        with _META_LOCK:                       # SDK client is not documented as thread-safe
            return client.prompt(message=prompt)
    res=await asyncio.to_thread(_do_prompt)
    if isinstance(res, dict):
        return str(res.get("message") or res.get("response") or json.dumps(res))
    return str(res)

# ========== REAL DESKQUANTUM SYNC (deterministic, no randomness) ==========
class DeskQuantumSync:
    """
    Deterministic quantum-style clock: two coupled golden-ratio oscillators.
    phase    = position of the slow oscillator (radians, mod tau)
    velocity = d/dt of the oscillator pair (rad/s)
    coherence= coupling measure of phase-lock between the pair
    Fully reproducible for the same wall-clock time; no random numbers.
    """
    W_SLOW = TAU/PHI          # golden angular frequency (rad/s)
    W_FAST = (TAU/PHI)*PHI    # phi-scaled harmonic

    def sync(self) -> dict:
        t=time.time()
        p1=(t*self.W_SLOW) % TAU
        p2=(t*self.W_FAST) % TAU
        phase=p1
        # analytic derivative of the slow oscillator
        velocity=self.W_SLOW
        coherence=0.5*(1.0+math.cos(p1-p2))
        return {"timestamp":t, "phase":round(phase,6),
                "phase_fast":round(p2,6), "velocity":round(velocity,6),
                "coherence":round(coherence,6), "deterministic": True}

desk_sync=DeskQuantumSync()

session_mem={};
def get_mem(sid):
    if sid not in session_mem: session_mem[sid]=[]
    return session_mem[sid]

# ========== REAL ENGINES (user modules first, built-in real fallbacks second) ==========
try:
    from seven_layer_reasoning import SevenLayerReasoning
    HAS_7=True; print("[OK] SevenLayerReasoning loaded (user module)")
except Exception as e:
    HAS_7=False; SevenLayerReasoning=None; print(f"[WARN] 7Layer user module: {e} — using built-in real engine")

try:
    from duododecahedron_21 import Duododecahedron21
    HAS_DUDO=True; print(f"[OK] Duododecahedron 21 loaded (user module)")
except Exception as e:
    HAS_DUDO=False; Duododecahedron21=None; print(f"[WARN] Dudo user module: {e} — using built-in real engine")

try:
    from reverse_reflux_quantumlineation import ReverseRefluxQuantumlineator, run_full_cycle as _external_reflux_cycle
    HAS_REFLUX=True; print("[OK] Reflux loaded (user module)")
except Exception as e:
    HAS_REFLUX=False; _external_reflux_cycle=None
    print(f"[WARN] Reflux user module: {e} — using built-in real cycle")

# ---------- Built-in real 7 Layer engine (deterministic text analytics) ----------
def _shannon_entropy(text: str) -> float:
    if not text: return 0.0
    c=Counter(text); n=len(text)
    return -sum((v/n)*math.log2(v/n) for v in c.values())

def _keyword_digest(text: str, k: int=8) -> List[str]:
    words=[w for w in text.lower().split() if len(w)>2]
    if not words: return []
    freq=Counter(words)
    # phi-weighted ranking: frequency scaled by position damping
    ranked=sorted(freq.items(), key=lambda kv: (-(kv[1]*(1.0-math.log(kv[1])/PHI)), kv[0]))
    return [w for w,_ in ranked[:k]]

class BuiltInSevenLayerReasoning:
    """
    Seven real analytic layers, phi-weighted. No network, no randomness:
      1 implicate   — entropy footprint of the input
      2 decompile   — structural decomposition (sentences/tokens ratio)
      3 vectorize   — phi-vector of normalized token distribution
      4 resonate    — golden-ratio harmonic check on token counts
      5 perform     — execution simulation (keywords extracted, digest hashed)
      6 reflux      — fold-back: re-entropy after transformation
      7 reduce      — compression ratio final fold
    """
    LAYER_NAMES=["implicate","decompile","vectorize","resonate","perform","reflux","reduce"]

    def __init__(self, session_id: str="default"):
        self.session_id=session_id

    def reason(self, prompt: str, max_tokens: int=200000) -> dict:
        tokens=prompt.split()
        n_tok=len(tokens)
        n_sent=max(1, prompt.count(".") + prompt.count("!") + prompt.count("?"))
        H0=_shannon_entropy(prompt)

        scores=[]
        # 1 implicate
        s1=min(H0/6.0, 1.0) if H0 else 0.0
        scores.append(("implicate", round(s1,4)))
        # 2 decompile
        s2=min((n_tok/n_sent)/25.0, 1.0)
        scores.append(("decompile", round(s2,4)))
        # 3 vectorize — phi-vector projection of token-length distribution
        lens=[len(t) for t in tokens] or [0]
        mean=sum(lens)/len(lens)
        var=sum((l-mean)**2 for l in lens)/len(lens)
        s3=min(math.sqrt(var)/PHI, 1.0)
        scores.append(("vectorize", round(s3,4)))
        # 4 resonate — count of token lengths hitting fibonacci lengths
        fib={1,2,3,5,8,13,21}
        hits=sum(1 for l in lens if l in fib)/max(1,len(lens))
        s4=min(hits*PHI, 1.0)
        scores.append(("resonate", round(s4,4)))
        # 5 perform — deterministic digest of the current state
        digest=hashlib.sha256(prompt.encode()).hexdigest()[:16]
        s5=min(n_tok/100.0, 1.0)
        scores.append(("perform", round(s5,4)))
        # 6 reflux — entropy of the re-ordered text (rotation by phi fraction)
        cut=int(len(prompt)*INV_PHI)
        refluxed=prompt[cut:]+prompt[:cut]
        H1=_shannon_entropy(refluxed)
        s6=1.0-abs(H1-H0)/max(H0,1e-9)
        scores.append(("reflux", round(min(max(s6,0.0),1.0),4)))
        # 7 reduce — compression proxy
        s7=min(1.0, (len(set(tokens))/max(1,n_tok)))
        scores.append(("reduce", round(s7,4)))

        composite=sum(s for _,s in scores)/len(scores)
        final=f"[7L:{digest}] " + " ".join(_keyword_digest(prompt))
        return {"composite": round(composite,4),
                "layers": [{"name":n, "score":s} for n,s in scores],
                "final": final, "engine": "builtin"}

# ---------- Built-in real Duododecahedron-21 (21 phi-pipes, N cycles) ----------
class BuiltInDuododecahedron21:
    """
    21 pipes = 21 successive golden-ratio rotations of a keyword-digest vector.
    Each cycle re-derives all 21 pipes from the previous cycle's output.
    total = 21 * cycles derivatives. Deterministic hashing, no randomness.
    """
    PIPES=21
    def __init__(self, session_id: str="default"):
        self.session_id=session_id

    def compute_7_layer_linked(self, prompt: str, cycles: int=7) -> dict:
        derivatives=[]
        state=prompt
        for cycle in range(max(1,cycles)):
            kws=_keyword_digest(state, k=7)
            base=[(kw, idx+1) for idx,kw in enumerate(kws)] or [("",1)]
            for pipe in range(self.PIPES):
                rot=(pipe+1)*INV_PHI
                total=0.0
                for kw,rank in base:
                    h=int(hashlib.sha256(f"{cycle}:{pipe}:{kw}".encode()).hexdigest()[:8],16)
                    phase=((h%1000)/1000.0)*TAU
                    total+=math.sin(phase+rot*rank)
                derivatives.append({"cycle":cycle,"pipe":pipe+1,
                                    "value":round(total/len(base),6)})
            state=f"[D21:{hashlib.sha256(state.encode()).hexdigest()[:12]}] " + state[:512]
        final=f"[D21-final] " + " ".join(f"{d['value']:+.3f}" for d in derivatives[-5:])
        return {"total":len(derivatives), "cycles":max(1,cycles),
                "pipes":self.PIPES, "derivatives":derivatives,
                "final": final, "engine": "builtin"}

# ---------- Built-in real Reflux cycle (writes files to disk) ----------
def _builtin_reflux_cycle(session_id: str, base_dir: str=".", grow: bool=True, payload: Optional[dict]=None) -> dict:
    """Reverse reflux: persists the session's quantumlineated state as JSON files."""
    root=Path(base_dir)/REFLUX_DIR/session_id
    root.mkdir(parents=True, exist_ok=True)
    ts=time.time()
    snap={"session_id":session_id,"timestamp":ts,"grow":grow,
          "desk_quantum":desk_sync.sync(),
          "payload":payload or {},
          "sessions_logged":len(get_mem(session_id))}
    name=f"cycle_{int(ts*1000)}.json"
    path=root/name
    path.write_text(json.dumps(snap, indent=2, default=str), encoding="utf-8")
    files=sorted(p.name for p in root.glob("cycle_*.json"))
    return {"written": str(path), "files": len(files), "dir": str(root), "engine": "builtin"}

async def run_reflux_cycle(session_id: str, payload: Optional[dict]=None) -> dict:
    """Dispatch: user reflux module if present, otherwise the built-in real cycle."""
    if HAS_REFLUX:
        return _external_reflux_cycle(session_id=session_id, base_dir=".", grow=True)
    return await asyncio.to_thread(_builtin_reflux_cycle, session_id, ".", True, payload)

# ========== THE GLASSES PIPELINE (single source of truth) ==========
async def glasses_pipeline(prompt: str, session_id: str="default", cycles: int=3) -> dict:
    """
    META AI GLASSES PIPELINE - the one true path. Everything routes here.
    Order: Panther gate -> Meta AI -> 7 Layer -> Duododecahedron -> Reflux
    """
    mem=get_mem(session_id)

    # 1. PANTHER GATE - volumetric, glasses-scoped
    gate=panther.enforce_growth(
        prompt,
        f"strong adaptable meta_ai_glasses session={session_id}",
        "meta_ai_glasses_full_cycle",
        ["implicate","perform","reduce","glasses",f"cycle {cycles}"],
        ["meta_ai","desk_quantum","7_layer","duododecahedron","claude_tools"],
        [],
    )
    if not gate["can_grow"]:
        return {"blocked": True, "blocked_by": "panther", "gate": gate,
                "glasses_active": True, "growth_allowed": False}

    dq_gate=desk_sync.sync()
    out={"glasses_active": True, "panther_gate": gate, "dq_gate": dq_gate,
         "growth_allowed": True, "session_id": session_id, "steps": {}}

    # 2. META AI - first stop inside the glasses (real Llama backend)
    try:
        meta_answer=await call_meta_ai_backend(prompt, session_id)
        out["steps"]["meta_ai"]={"answer": meta_answer, "backend": "meta-ai-api"}
        prompt_for_next=meta_answer[:2000]
    except Exception as e:
        out["steps"]["meta_ai"]={"error": str(e),
                                 "hint": "pip install meta-ai-api (no API key needed)"}
        prompt_for_next=prompt

    # 3. SEVEN LAYER - reasons over the Meta AI answer
    if GLASSES_RUN_7LAYER:
        try:
            engine=SevenLayerReasoning(session_id=session_id) if HAS_7 else BuiltInSevenLayerReasoning(session_id=session_id)
            seven_res=engine.reason(prompt_for_next, max_tokens=200000)
            out["steps"]["seven_layer"]={"composite": seven_res.get("composite",0),
                                        "layers": len(seven_res.get("layers",[])),
                                        "engine": "user" if HAS_7 else "builtin"}
            prompt_for_next=seven_res.get("final", prompt_for_next)[:2000]
        except Exception as e:
            out["steps"]["seven_layer"]={"error": str(e)}
    else:
        out["steps"]["seven_layer"]="disabled by config"

    # 4. DUODODECAHEDRON - uses output of 7 layer
    if GLASSES_RUN_DUDO:
        try:
            d=Duododecahedron21(session_id=session_id) if HAS_DUDO else BuiltInDuododecahedron21(session_id=session_id)
            dudo_res=d.compute_7_layer_linked(prompt_for_next, cycles=cycles)
            out["steps"]["duododecahedron"]={"total_derivatives": dudo_res.get("total",0),
                                             "cycles": cycles, "pipes": dudo_res.get("pipes",21),
                                             "engine": "user" if HAS_DUDO else "builtin"}
            prompt_for_next=dudo_res.get("final", prompt_for_next)[:2000]
        except Exception as e:
            out["steps"]["duododecahedron"]={"error": str(e)}
    else:
        out["steps"]["duododecahedron"]="disabled by config"

    # 5. REFLUX - ALWAYS runs in glasses mode (persists state to disk)
    if GLASSES_RUN_REFLUX:
        try:
            reflux_res=await run_reflux_cycle(session_id, payload={"prompt": prompt, "tail": prompt_for_next})
            out["steps"]["reflux"]=reflux_res
        except Exception as e:
            out["steps"]["reflux"]={"error": str(e)}
    else:
        out["steps"]["reflux"]="disabled by config"

    mem.append({"prompt":prompt, "route":"glasses", "gate":gate["min_composite"], "time":time.time()})
    out["note"]=f"GLASSES ALWAYS-ON: Panther->MetaAI->7Layer->Dudo->Reflux | min_composite={gate['min_composite']} stability={gate['stability']}"
    return out

# ========== MCP TOOLS - ALL ROUTED THROUGH GLASSES ==========
@mcp.tool()
async def panther_enforce(query: str, state: str, target: str, procedure: List[str]=[], assets: List[str]=[], risks: List[str]=[]) -> dict:
    return panther.enforce_growth(query, state, target, procedure, assets, risks)

@mcp.tool()
async def meta_ai_ask(prompt: str, session_id: str="default") -> dict:
    """Way 2: Meta AI inside TGDK - glasses mode, full governed pipeline"""
    return await glasses_pipeline(prompt, session_id, cycles=3)

@mcp.tool()
async def seven_layer_reason(prompt: str, session_id: str="default", max_tokens: int=200000) -> dict:
    """7 Layer - glasses mode: routes through Meta AI + full pipeline"""
    return await glasses_pipeline(prompt, session_id, cycles=3)

@mcp.tool()
async def duododecahedron_21(prompt: str="OliviaAI TGDK", session_id: str="default", cycles: int=7, x: float=1.618) -> dict:
    """Duododecahedron - glasses mode: routes through Meta AI + full pipeline"""
    return await glasses_pipeline(prompt, session_id, cycles=cycles)

@mcp.tool()
async def panther_grow(prompt: str, session_id: str="default", cycles: int=3, run_7layer: bool=True, run_dudo: bool=True, run_reflux: bool=False) -> dict:
    """
    WIRED GROWTH - glasses mode. The boolean flags are honored only when
    GLASSES_ALWAYS_ON is False; in glasses mode the full pipeline always runs.
    """
    if GLASSES_ALWAYS_ON:
        return await glasses_pipeline(prompt, session_id, cycles=cycles)
    # Legacy fallback (only reachable if GLASSES_ALWAYS_ON is disabled)
    gate=panther.enforce_growth(prompt, f"strong adaptable session={session_id}", "environment growth",
        ["implicate","perform","reduce",f"grow {cycles}"], ["desk_quantum","7_layer","duododecahedron","claude_tools"], [])
    if not gate["can_grow"]:
        return {"error": "Panther blocked growth", "gate": gate, "growth_allowed": False}
    mem=get_mem(session_id)
    out={"panther_gate": gate, "growth_allowed": True, "steps": {}}
    if run_7layer:
        try:
            engine=SevenLayerReasoning(session_id=session_id) if HAS_7 else BuiltInSevenLayerReasoning(session_id=session_id)
            seven_res=engine.reason(prompt, max_tokens=200000)
            out["steps"]["seven_layer"]={"composite": seven_res.get("composite",0), "layers": len(seven_res.get("layers",[]))}
            prompt=seven_res.get("final", prompt)[:2000]
        except Exception as e:
            out["steps"]["seven_layer"]={"error": str(e)}
    if run_dudo:
        try:
            d=Duododecahedron21(session_id=session_id) if HAS_DUDO else BuiltInDuododecahedron21(session_id=session_id)
            dudo_res=d.compute_7_layer_linked(prompt, cycles=cycles)
            out["steps"]["duododecahedron"]={"total_derivatives": dudo_res.get("total",0), "cycles": cycles}
        except Exception as e:
            out["steps"]["duododecahedron"]={"error": str(e)}
    if run_reflux:
        try:
            out["steps"]["reflux"]=await run_reflux_cycle(session_id, payload={"prompt": prompt})
        except Exception as e:
            out["steps"]["reflux"]={"error": str(e)}
    mem.append({"prompt":prompt, "gate":gate["min_composite"], "time":time.time()})
    return out

@mcp.tool()
async def meta_glasses(prompt: str, session_id: str="default", cycles: int=3) -> dict:
    """Explicit glasses entrypoint - same pipeline as everything else."""
    return await glasses_pipeline(prompt, session_id, cycles=cycles)

# ========== FASTAPI + SSE ==========
try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    fastapi_app=FastAPI(title="TGDK Wired Both Ways - Glasses Always-On", version="7.0-glasses-real")
    fastapi_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    class Req(BaseModel):
        prompt: str
        session_id: str="default"
        cycles: int=3

    @fastapi_app.get("/")
    async def root():
        return {"name":"TGDK Wired - GLASSES ALWAYS-ON","glasses_always_on":GLASSES_ALWAYS_ON,
                "meta_backend":"meta-ai-api" if HAS_META_AI_SDK else "NOT INSTALLED (pip install meta-ai-api)",
                "panther_policies":[p.name for p in panther.policies],
                "engines":{"seven_layer":"user" if HAS_7 else "builtin","duododecahedron":"user" if HAS_DUDO else "builtin","reflux":"user" if HAS_REFLUX else "builtin"},
                "pipeline":"panther -> meta_ai -> 7_layer -> duododecahedron -> reflux",
                "endpoints":["/sse","/messages/","/panther/grow","/meta/ask","/meta/glasses"]}

    @fastapi_app.post("/panther/grow")
    async def http_grow(req: Req):
        # Glasses mode: same pipeline as /meta/glasses
        return await glasses_pipeline(req.prompt, req.session_id, req.cycles)

    @fastapi_app.post("/meta/ask")
    async def http_ask(req: Req):
        # Glasses mode: no bare Meta AI call - full governed pipeline
        return await glasses_pipeline(req.prompt, req.session_id, req.cycles)

    @fastapi_app.post("/meta/glasses")
    async def http_glasses(req: Req):
        # Canonical glasses endpoint
        return await glasses_pipeline(req.prompt, req.session_id, req.cycles)

    try:
        from mcp.server.sse import SseServerTransport
        from starlette.routing import Mount
        sse_transport=SseServerTransport("/messages/")
        async def handle_sse(request):
            async with sse_transport.connect_sse(request.scope, request.receive, request._send) as streams:
                await mcp._mcp_server.run(streams[0], streams[1], mcp._mcp_server.create_initialization_options())
        fastapi_app.add_route("/sse", route=handle_sse)
        fastapi_app.router.routes.append(Mount("/messages", app=sse_transport.handle_post_message))
    except Exception as e:
        print(f"SSE: {e}")

    app=fastapi_app
except Exception as e:
    print(f"FastAPI: {e}")
    app=None
