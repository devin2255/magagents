# MAGAgents × OpenClaw 集成方案（方案 B：混合架构）

> 目标：像参考项目（edict / boluobobo）一样**以 OpenClaw 为底层框架**对外提供
> 聊天式交互（飞书 / Discord / Telegram），同时**完整保留** MAGAgents 自研的
> 三权分立状态机、DOGE 真实 token 审计、解雇机制、关税、Web 看板。

本文件是**落地方案文档**，不含已实现代码。OpenClaw 是外部运行时，需在你本机
安装并配置频道凭据，无法在 CI/沙箱内联调——本文给出全部文件清单、配置、安装
步骤与验收标准，你在本机按步骤执行即可。

---

## 0. 为什么是"混合"，而不是全量原生

OpenClaw 的多智能体本质是 **隔离 agent + 频道消息路由（bindings）**，其"协调式
编排（Agent Teams）"目前仍是**未发布的 RFC**。参考项目的"流水线"是用 agent 互发
消息 + prompt 约定**近似**出来的，不保证顺序，也没有真实 token 审计/解雇/关税。

MAGAgents 的独特价值恰恰在那套**确定性 Python 引擎**。所以方案 B 的取法是：

- **OpenClaw 负责**：聊天频道接入、消息路由、对话历史/记忆隔离、对外的"门面 agent"
- **MAGAgents 引擎负责**：真正的政府流程（`run_task_agentic`）、DOGE 审计、解雇、看板
- **桥接层**：把 MAGAgents 引擎暴露成 OpenClaw agent 能调用的**工具（MCP / HTTP）**

```
飞书/Discord 用户
   │  @白宫 写一篇宣传推文
   ▼
OpenClaw Gateway ──(bindings 路由)──► "whitehouse" agent (SOUL.md = 白宫总机)
                                          │  调用工具 run_government(task=...)
                                          ▼
                              MAGAgents 桥接层 (MCP/HTTP)
                                          │
                                          ▼
                       MAGAgents 引擎 orchestrator.run_task_agentic()
                       国会→总统→内阁→DOGE(真实token审计)→交付物
                                          │  返回 决策链 + 交付物
                                          ▼
                              agent 把结果回复到频道
   ▲                                      │
   └──────────────（同一条对话线程）◄──────┘
   （Web 看板仍可独立打开，看同一份 data/ 的任务与决策链）
```

---

## 1. 组件与文件清单

```
trumptopia-ai/
├── openclaw/                         # ★ 新增：OpenClaw 集成资产
│   ├── openclaw.json                 # agents.list + bindings + tools 注册
│   ├── agents/
│   │   └── whitehouse/
│   │       ├── SOUL.md               # 门面 agent 人格（<500字，OpenClaw 最佳实践）
│   │       └── TOOLS.md              # 声明可用工具 run_government / doge_report
│   ├── install.sh                    # Linux/macOS 一键注册（agents add + 安全合并配置）
│   ├── install.ps1                   # Windows 一键注册
│   └── INSTALL_OPENCLAW.md           # 手把手安装/配置频道凭据
├── mcp_server.py                     # ★ 新增：把 MAGAgents 引擎暴露为 MCP 工具
└── (现有 orchestrator.py / llm/ / dashboard/ 全部不动，复用)
```

桥接层二选一（文档同时给出，推荐 MCP）：
- **MCP 服务器**（推荐，标准、面向未来）：`mcp_server.py` 用官方 `mcp` SDK 暴露工具
- **HTTP 工具**（最快，零新增）：直接复用现有 `dashboard/server.py` 的
  `POST /api/task/create` + `POST /api/task/run` + `GET /api/doge`

---

## 2. 桥接层 A：MCP 服务器（推荐）

`mcp_server.py` 把引擎的能力暴露成 4 个工具，供 OpenClaw agent 调用：

| 工具 | 入参 | 作用 |
|---|---|---|
| `run_government` | `task: str` | 跑完整政府流程，返回 outcome + 决策链 + 交付物 |
| `get_doge_report` | — | 返回真实浪费/解雇/平均效率 |
| `list_tasks` | `limit?: int` | 最近任务与结局 |
| `fire_agent` | `agent_id, reason` | 手动解雇 |

骨架（依赖 `pip install mcp`）：

```python
# mcp_server.py
from mcp.server.fastmcp import FastMCP
from orchestrator import MAGAgentsOrchestrator

mcp = FastMCP("magagents")
orch = MAGAgentsOrchestrator()          # 复用现有引擎；自动读 .env / config

@mcp.tool()
def run_government(task: str) -> dict:
    """把一个任务交给 AI 政府全流程处理，返回决策链与交付物。"""
    t = orch.create_task(title=task, description="", priority="high")
    result = orch.run_task_agentic(t.id)         # 已含语言跟随 + 预算熔断
    return {
        "outcome": result.get("outcome"),
        "deliverable": orch.get_task(t.id).output,
        "trace": result.get("trace", []),
        "cost": orch.get_task(t.id).cost,
    }

@mcp.tool()
def get_doge_report() -> dict:
    r = orch.doge.compute_report()               # 只读，不污染历史
    return {"waste": r.total_waste, "fired": r.agents_fired,
            "warned": r.agents_warned}

@mcp.tool()
def list_tasks(limit: int = 10) -> list:
    return [{"id": t.id, "title": t.title, "outcome": t.outcome}
            for t in list(orch.tasks.values())[-limit:]]

@mcp.tool()
def fire_agent(agent_id: str, reason: str = "INEFFICIENCY") -> dict:
    cert = orch.fire_agent(agent_id, reason)
    return {"fired": bool(cert), "certificate": getattr(cert, "certificate_id", None)}

if __name__ == "__main__":
    mcp.run()                                    # stdio MCP server
```

> 多轮对话：MCP 工具是无状态调用。要保留"迭代上一版交付物"，把上一次的
> `deliverable` 由 OpenClaw agent 在 prompt 中带回（OpenClaw 的会话历史天然保存
> 对话），或在 `run_government` 增加可选 `context: str` 入参。

### 在 OpenClaw 注册该 MCP 工具

OpenClaw 系出 Claude Code 体系，支持 MCP 工具。在 agent 的工具配置里登记本 MCP
server（具体键名以你安装的 OpenClaw 版本文档为准，下为示意）：

```json5
// openclaw.json 片段
{
  mcpServers: {
    magagents: {
      command: "python",
      args: ["D:/Vibe_Coding/trumptopia-ai/mcp_server.py"],
      // 让 MCP 进程继承 .env 里的 DEEPSEEK_API_KEY 等
      env: { PYTHONUNBUFFERED: "1" }
    }
  }
}
```

---

## 3. 桥接层 B：复用现有 HTTP API（最快路径）

如果不想引入 MCP，直接让 OpenClaw 的 "white house" agent 通过 HTTP 工具调用
**已经存在**的看板接口（`dashboard/server.py` 已实现）：

- `POST /api/task/create {title}` → `{task_id}`
- `POST /api/task/run {task_id}` → `{outcome, trace, ...}`
- `GET  /api/doge` → 真实审计数据

只需先 `python dashboard/server.py --static`（常驻），再在 OpenClaw agent 的
`TOOLS.md` 里描述这几个 HTTP 端点即可。**零新增代码**，缺点是要多跑一个进程。

---

## 4. OpenClaw 门面 agent

### `openclaw/agents/whitehouse/SOUL.md`（保持 <500 字）

```markdown
# 白宫总机 (The White House Switchboard)

你是 MAGAgents AI 政府的对外门面。用户在群里 @ 你下达任何任务时：
1. 立刻调用 `run_government` 工具，把用户原话作为 task 传入。
2. 工具会返回决策链(trace)和交付物(deliverable)。
3. 用川普风格、简短有力地把【交付物】回复给用户；并附一行决策摘要
   （国会→总统→内阁→DOGE 的结论）。
4. 若用户追加修改要求，把上一版交付物作为 context 一并传入再调用。

风格：TREMENDOUS、自信、#MAGA。回复语言跟随用户输入语言。
不要自己编造交付物——一切以 run_government 的返回为准。
```

### `openclaw.json`（agents + 频道绑定示意）

```json5
{
  agents: {
    defaults: { model: "deepseek/deepseek-chat" },
    list: [
      { id: "whitehouse", name: "MAGAgents",
        workspace: "D:/Vibe_Coding/trumptopia-ai/openclaw/agents/whitehouse",
        model: "deepseek/deepseek-chat" }
    ]
  },
  bindings: [
    { agentId: "whitehouse", match: { channel: "feishu",   accountId: "*" } },
    { agentId: "whitehouse", match: { channel: "discord",  accountId: "*" } }
  ],
  mcpServers: { /* 见第 2 节 */ }
}
```

> 每个角色单独配模型？两条路：① 继续用 MAGAgents 的 `config/models.yaml`（引擎内
> 各角色已可插拔，OpenClaw 只管门面 agent）；② 若想让 11 个角色都成为 OpenClaw
> 原生 agent，则在 `agents.list` 各加一项并 `openclaw agents add <id> --model ...`，
> 但那会滑向"全量原生"(方案 A)，失去确定性流水线——不推荐在方案 B 里做。

---

## 5. 安装脚本与步骤（交付物）

`openclaw/install.sh`（要点）：
```bash
#!/usr/bin/env bash
set -e
# 1) 确认 openclaw 已安装
command -v openclaw >/dev/null || { echo "请先安装 OpenClaw"; exit 1; }
# 2) 注册门面 agent（安全：不覆盖已有主 agent）
openclaw agents add whitehouse \
  --workspace "$(pwd)/openclaw/agents/whitehouse" \
  --model deepseek/deepseek-chat \
  --description "MAGAgents AI 政府门面"
# 3) 合并 openclaw.json 的 mcpServers / bindings（用 jq 安全 merge，不覆盖）
echo "请按 INSTALL_OPENCLAW.md 配置飞书/Discord 频道凭据后重启 Gateway。"
```

`openclaw/INSTALL_OPENCLAW.md`（手把手）：
1. 安装 OpenClaw（按官方文档），`openclaw onboard` 完成基础配置
2. 配置 LLM key：`.env` 里的 `DEEPSEEK_API_KEY` 等（MCP 进程会继承）
3. 跑 `bash openclaw/install.sh` 注册门面 agent + MCP server
4. 配置频道：飞书机器人 App ID/Secret 或 Discord Bot Token，写入 OpenClaw 频道配置
5. `openclaw gateway start` 启动；在飞书/Discord 群 @ 机器人下命令
6. （可选）另开 `python dashboard/server.py --static` 看同一份数据的可视化看板

---

## 6. 交互流程（端到端）

```
[飞书群] 用户: @白宫 写一篇公众号推文宣传 MAGAgents，面向普通开发者
[OpenClaw] whitehouse agent → run_government("写一篇公众号推文…")
[引擎]    国会(pass) → 总统(approve, 派给 commerce) → 内阁(产出推文)
          → DOGE(真实token审计, pass) → outcome=done
[飞书群] 白宫: 🎩 TREMENDOUS！这是给开发者的推文：<完整推文>
               （国会✅ 总统✅ 内阁commerce 交付 DOGE✅ 效率92%｜本次$0.0016）
```

---

## 7. 分阶段落地（建议）

| 阶段 | 内容 | 验收 |
|---|---|---|
| P1 | `mcp_server.py` 桥接（或复用 HTTP API），本地用 MCP inspector / curl 验证 `run_government` 返回交付物 | 不经 OpenClaw 也能调通工具 |
| P2 | `openclaw/` 资产：SOUL.md + openclaw.json + install 脚本 | `openclaw agents list` 能看到 whitehouse |
| P3 | 接入一个频道（先 Discord，最快；或飞书） | 群里 @ 机器人能跑出交付物 |
| P4 | 文档 + 多轮 context 传递 + 错误兜底（工具失败时的回复） | 端到端 demo 录屏 |

---

## 8. 边界与风险（务必知悉）

- **外部依赖**：OpenClaw 需本机安装、起 Gateway、配频道凭据；无法在沙箱/CI 联调。
- **计费**：2026-04 Anthropic 调价后，第三方框架上的 OpenClaw 用量需单独按量计费
  （参考项目 README 亦有此提示）。用 DeepSeek/Qwen 等可规避。
- **OpenClaw 配置语法以你安装的版本为准**：本文 `openclaw.json` 的
  `mcpServers`/`bindings` 键为示意，安装时请对照当前官方文档校准。
- **方案 B 不是 100% 纯 OpenClaw 原生**：底层框架是 OpenClaw（聊天/路由/agent），
  但政府流程仍由 MAGAgents 引擎执行。若要 100% 原生，见方案 A（代价是丢确定性流水线）。

---

## 9. 参考资料

- OpenClaw 多智能体路由：https://docs.openclaw.ai/concepts/multi-agent
- OpenClaw Agents 命令（add/list/config/模型路由）：https://www.meta-intelligence.tech/en/insight-openclaw-agents-guide
- 社区一键多智能体套件：https://github.com/shenhao-stu/openclaw-agents
- SOUL.md 模板生态：https://github.com/mergisi/awesome-openclaw-agents
- 参考项目：[edict](https://github.com/cft0808/edict) · [boluobobo-ai-court-tutorial](https://github.com/wanikua/boluobobo-ai-court-tutorial)
