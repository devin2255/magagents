#!/usr/bin/env python3
"""
MAGAgents - 对话式命令行 (Conversational CLI)

像聊天一样给 AI 政府派活：输入一句话 -> 国会/总统/内阁/DOGE 逐步实时决策
-> 打印交付物。回复语言跟随你的输入语言。

用法:
    python chat.py            # 进入对话模式
    python chat.py "写一条推文"  # 跑单个任务后退出

命令: /help /tasks /doge /feed /quit
"""

import sys
from pathlib import Path

# 让 emoji / 中文在所有平台正常输出 (Windows GBK)
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
from orchestrator import MAGAgentsOrchestrator  # noqa: E402

# ---- ANSI 颜色 (Windows 10+ 终端支持) ----
class C:
    R = "\033[0m"; B = "\033[1m"; DIM = "\033[2m"
    RED = "\033[31m"; GREEN = "\033[32m"; YELLOW = "\033[33m"
    BLUE = "\033[34m"; MAGENTA = "\033[35m"; CYAN = "\033[36m"; GOLD = "\033[93m"

STAGE = {
    "congress": ("🏛️", "国会 / Congress", C.CYAN),
    "scotus":   ("⚖️", "最高法院 / SCOTUS", C.MAGENTA),
    "potus":    ("🎩", "总统 / POTUS", C.GOLD),
    "cabinet":  ("🏢", "内阁 / Cabinet", C.BLUE),
    "doge":     ("🐕", "DOGE 审计", C.YELLOW),
}
OUTCOME = {
    "done": (C.GREEN, "✅ 完成 DONE"),
    "fired": (C.RED, "🔥 已解雇 FIRED"),
    "vetoed": (C.RED, "❌ 已否决 VETOED"),
    "blocked": (C.YELLOW, "🚫 已驳回 BLOCKED"),
    "over_budget": (C.YELLOW, "💸 超预算 OVER BUDGET"),
}


def print_step(step):
    """run_task_agentic 的逐步回调：实时打印每个角色的决策。"""
    icon, label, color = STAGE.get(step.get("stage"), ("•", step.get("stage", "?"), C.R))
    verdict = (step.get("vote") or step.get("decision") or step.get("ruling")
               or step.get("verdict") or ("已执行" if step.get("output_preview") else ""))
    reason = step.get("reason") or step.get("output_preview") or ""
    eff = f"  ({step['efficiency']:.0f}% 效率)" if step.get("efficiency") is not None else ""
    print(f"  {icon} {color}{C.B}{label}{C.R} "
          f"{C.B}{verdict}{C.R}{C.DIM}{eff}{C.R}")
    if reason:
        print(f"     {C.DIM}{reason}{C.R}")


def run_one(orch, text, session=None):
    enabled = orch.llm_enabled
    print(f"\n{C.DIM}📋 任务：{text}{C.R}")
    if not enabled:
        print(f"{C.YELLOW}⚠️  当前离线模式（未配 API key），将自动放行并输出占位结果。{C.R}")

    # 多轮上下文：把上一版交付物带上，让内阁迭代而非从零开始
    description = ""
    if session and session.get("last_output"):
        print(f"{C.DIM}🔗 已带上上一轮上下文（迭代模式，输入 /new 可重新开始）{C.R}")
        description = (
            f"【这是一次多轮对话的延续】\n"
            f"上一个任务：{session.get('last_title', '')}\n"
            f"上一版交付物：\n{session['last_output']}\n\n"
            f"用户本轮的补充/修改要求：{text}\n"
            f"请基于以上上下文，产出更新后的【完整】交付物，而不是从头重来。"
        )
    print(f"{C.DIM}🏛️  政府流程运行中…{C.R}\n")

    task = orch.create_task(title=text, description=description, priority="high")
    before = dict(orch.llm_usage)
    result = orch.run_task_agentic(task.id, on_step=print_step)

    color, label = OUTCOME.get(result.get("outcome"), (C.R, result.get("outcome", "?")))
    print(f"\n  {color}{C.B}🏁 {label}{C.R}")

    t = orch.get_task(task.id)
    if t and t.output:
        print(f"\n{C.GREEN}{C.B}📄 交付物：{C.R}")
        for line in t.output.splitlines():
            print(f"  {line}")
        # 记住本轮交付物，供下一轮迭代
        if session is not None and result.get("outcome") == "done":
            session["last_title"] = text
            session["last_output"] = t.output

    di = orch.llm_usage["input_tokens"] - before["input_tokens"]
    do = orch.llm_usage["output_tokens"] - before["output_tokens"]
    dc = orch.llm_usage["cost"] - before["cost"]
    if di or do:
        print(f"\n{C.DIM}💸 本次用量：{di}+{do} tokens · ${dc:.5f}{C.R}")


def cmd_tasks(orch):
    if not orch.tasks:
        print(f"{C.DIM}还没有任务。{C.R}"); return
    for t in list(orch.tasks.values())[-10:]:
        oc = OUTCOME.get(t.outcome, (C.R, t.outcome or t.state.value))[1]
        print(f"  {C.DIM}{t.id}{C.R}  {t.title[:40]}  [{oc}]")


def cmd_doge(orch):
    r = orch.doge.compute_report()
    print(f"  🐕 浪费：{C.YELLOW}${r.total_waste:.4f}{C.R}  "
          f"解雇：{r.agents_fired}  警告：{r.agents_warned}")
    for a, p in orch.doge.agent_history.items():
        print(f"     {a}: {p.efficiency_score:.0f}% 效率, {p.total_tokens} tokens")


def cmd_feed(orch):
    for p in orch.truth_social.get_feed(8):
        print(f"  {C.CYAN}@{p['agent_id']}{C.R}: {p['message'][:90]}")


HELP = f"""{C.B}MAGAgents 对话模式{C.R}
  直接输入任务（任意语言，回复跟随你的语言），例如：
    写一条庆祝贸易协议的推文
  多轮：直接追加要求即可迭代上一版交付物；{C.CYAN}/new{C.R} 开始新会话。
  命令：
    {C.CYAN}/tasks{C.R}  最近任务      {C.CYAN}/doge{C.R}   DOGE 审计数据
    {C.CYAN}/feed{C.R}   Truth Social  {C.CYAN}/new{C.R}    清空上下文
    {C.CYAN}/help{C.R}   帮助          {C.CYAN}/quit{C.R}   退出"""


def main():
    orch = MAGAgentsOrchestrator()
    mode = f"{C.GREEN}真实模型{C.R}" if orch.llm_enabled else f"{C.YELLOW}离线模拟{C.R}"

    # 单次模式
    if len(sys.argv) > 1:
        run_one(orch, " ".join(sys.argv[1:]))
        return

    print(f"\n{C.GOLD}{C.B}🏛️  MAGAgents · AI 政府对话终端{C.R}   [AI 模式：{mode}]")
    print(HELP)
    session = {"last_title": None, "last_output": None}
    while True:
        try:
            text = input(f"\n{C.B}你 ▸ {C.R}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{C.DIM}再见！#MAGA{C.R}"); break
        if not text:
            continue
        if text in ("/quit", "/exit", "/q"):
            print(f"{C.DIM}再见！#MAGA{C.R}"); break
        elif text in ("/help", "/h"):
            print(HELP)
        elif text in ("/new", "/reset"):
            session = {"last_title": None, "last_output": None}
            print(f"{C.DIM}🆕 已开始新会话（清空上下文）。{C.R}")
        elif text == "/tasks":
            cmd_tasks(orch)
        elif text == "/doge":
            cmd_doge(orch)
        elif text == "/feed":
            cmd_feed(orch)
        elif text.startswith("/"):
            print(f"{C.DIM}未知命令，输入 /help 查看。{C.R}")
        else:
            run_one(orch, text, session)


if __name__ == "__main__":
    main()
