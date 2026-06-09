#!/usr/bin/env python3
"""MAGAgents · DOGE MCP tool (optional).

Lets the native OpenClaw agents keep MAGAgents' REAL efficiency audit & firing
by reusing the existing DOGEAuditor / FiringMechanism engine. Without this the
doge_musk agent can only judge qualitatively from its prompt.

Run by OpenClaw via openclaw.json -> mcpServers.doge. Requires: pip install mcp
(and the project's data/ dir, shared across calls for persistent state).

Tools exposed:
  - record_usage(agent_id, tokens, success, response_time=60)
  - audit(agent_id)            -> efficiency + verdict (pass/fire)
  - fire(agent_id, reason)     -> firing certificate
  - report()                   -> waste / fired / warned (read-only)
"""

import sys
from pathlib import Path

# 复用主项目引擎
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from doge_auditor import DOGEAuditor          # noqa: E402
from firing_mechanism import FiringMechanism  # noqa: E402

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    sys.stderr.write("需要 mcp SDK：pip install mcp\n")
    raise

DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
doge = DOGEAuditor(DATA)
firing = FiringMechanism(DATA)

mcp = FastMCP("doge")


@mcp.tool()
def record_usage(agent_id: str, tokens: int, success: bool = True,
                 response_time: float = 60.0, cost: float = 0.0) -> dict:
    """内阁部门执行任务后上报真实用量，喂给 DOGE 审计库。"""
    doge.record_task_completion(agent_id, int(tokens), float(cost),
                                float(response_time), bool(success))
    perf = doge.agent_history.get(agent_id)
    return {"agent_id": agent_id,
            "efficiency": perf.efficiency_score if perf else 100.0}


@mcp.tool()
def audit(agent_id: str) -> dict:
    """基于真实记录返回该 agent 的效率与裁决 (pass/fire)。"""
    perf = doge.agent_history.get(agent_id)
    eff = perf.efficiency_score if perf else 100.0
    verdict = "fire" if eff < 30 else "pass"
    return {"agent_id": agent_id, "efficiency": eff, "verdict": verdict,
            "violations": (perf.violations if perf else [])}


@mcp.tool()
def fire(agent_id: str, reason: str = "INEFFICIENCY") -> dict:
    """解雇低效 agent，生成解雇证书。"""
    perf = doge.agent_history.get(agent_id)
    eff = perf.efficiency_score if perf else 0.0
    cert = firing.fire_agent(agent_id, reason, "doge_musk", eff,
                             perf.violations if perf else [])
    return {"fired": bool(cert),
            "certificate_id": getattr(cert, "certificate_id", None),
            "message": getattr(cert, "message", "")}


@mcp.tool()
def report() -> dict:
    """只读：当前浪费/解雇/警告汇总（不污染历史）。"""
    r = doge.compute_report()
    return {"waste": r.total_waste, "agents_fired": r.agents_fired,
            "agents_warned": r.agents_warned}


if __name__ == "__main__":
    mcp.run()
