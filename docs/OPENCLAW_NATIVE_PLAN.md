# MAGAgents × OpenClaw 集成方案（方案 A：全量原生迁移）

> 目标：**100% 对齐参考项目（edict / boluobobo）的底层框架** —— 把 MAGAgents 重做成
> 一个**纯 OpenClaw agent 包**：11 个政府角色都成为 OpenClaw 原生 agent，LLM 调用、
> 频道接入（飞书 / Discord / Telegram）、agent 间协作**全部交给 OpenClaw**，不再依赖
> 任何自研 Python 引擎。

本文件是**落地方案文档**，不含已实现代码。OpenClaw 是外部运行时，需在本机安装、
起 Gateway、配频道凭据，无法在沙箱/CI 内联调——本文给出文件清单、配置、协调机制、
安装步骤与验收标准，你在本机执行。

---

## 0. 定位与一句话

方案 A = "**MAGAgents 作为一套 OpenClaw agent 模板分发**"，形态与参考项目完全一致：
一堆 `SOUL.md` + `openclaw.json` + 一键安装脚本，跑在 OpenClaw 上，群里 @ 角色下令。

> ⚠️ 这是**重做分发形态**，不是在现有 Python 项目上加东西。现有 `orchestrator.py /
> llm/ / dashboard/ / chat.py` 在方案 A 下**不再被使用**（保留为 `legacy/` 独立版即可）。

---

## 1. 与方案 B 的本质区别（先看取舍）

| 维度 | 方案 A（全量原生，本文） | 方案 B（混合，见 OPENCLAW_INTEGRATION.md） |
|---|---|---|
| 底层框架 | **纯 OpenClaw**（=参考项目） | OpenClaw + 自研引擎 |
| 政府流程 | agent 间**消息流转近似**（无保证顺序） | 自研状态机**确定性流水线** |
| 每角色独立模型 | ✅ OpenClaw 原生 `agents.list` | ✅ 引擎内 `config/models.yaml` |
| DOGE 真实 token 审计 | ❌ 默认丢失（可选用 MCP 工具补） | ✅ 原生保留 |
| 解雇 / 关税机制 | ❌ 降级为 prompt 行为（可选 MCP 工具） | ✅ 原生保留 |
| Web 看板 | ❌ 丢失（OpenClaw 无此概念） | ✅ 原生保留 |
| 聊天交互（飞书/Discord） | ✅ | ✅ |
| 与参考项目"框架一致" | ✅ **完全一致** | ⚠️ 部分一致 |

**结论**：A 换来与参考项目 100% 一致的框架，代价是放弃自研引擎那套独特卖点
（确定性流水线 / 真实 token 审计 / 看板）。本文同时给出"用可选 MCP 工具找回 DOGE/
解雇真实数据"的折中。

---

## 2. 架构

OpenClaw 多智能体 = **隔离 agent + 频道消息路由（bindings）**。其"协调式编排
（Agent Teams）"目前仍是**未发布 RFC**，所以三权分立流程靠 **intake agent + 
agent 间消息流转（agentToAgent）+ prompt 约定**近似——这正是参考项目的做法。

```
飞书/Discord 群
   │ @太子 写一篇宣传推文        （太子 = intake/分拣 agent）
   ▼
OpenClaw Gateway ──bindings──► intake(太子) agent
   │  按"宪法流程"把任务转交：
   ▼
congress_senate ──► congress_house ──► trump_president ──► (内阁某部) ──► doge_musk
（每一步都是独立 OpenClaw agent，通过 agentToAgent 工具互发消息，各自有 SOUL.md/模型/记忆）
   │
   ▼
最终由对应内阁部门产出交付物，trump_president 以川普风格回复频道
```

11 个原生 agent（沿用现有 SOUL.md 角色）：
`trump_president, congress_senate, congress_house, scotus, doge_musk,
state_dept, treasury, defense, commerce, energy, justice`
+ 1 个 `intake`（太子/总机，负责接收用户消息并启动流程）。

---

## 3. 文件清单（纯 OpenClaw agent 包）

```
trumptopia-ai/
├── openclaw-pack/                         # ★ 新增：可独立分发的 OpenClaw 包
│   ├── openclaw.json                      # agents.list(12) + defaults + bindings
│   ├── agents.yaml                        # 一键安装清单（仿 openclaw-agents 格式）
│   ├── agents/
│   │   ├── intake/        { SOUL.md, IDENTITY.md, TOOLS.md }
│   │   ├── trump_president/ { SOUL.md, IDENTITY.md, TOOLS.md }
│   │   ├── congress_senate/ { SOUL.md, ... }
│   │   ├── congress_house/  { SOUL.md, ... }
│   │   ├── scotus/          { SOUL.md, ... }
│   │   ├── doge_musk/       { SOUL.md, ... }
│   │   ├── state_dept/      { SOUL.md, ... }
│   │   ├── treasury/        { SOUL.md, ... }
│   │   ├── defense/         { SOUL.md, ... }
│   │   ├── commerce/        { SOUL.md, ... }
│   │   ├── energy/          { SOUL.md, ... }
│   │   └── justice/         { SOUL.md, ... }
│   ├── tools/                              # 可选：找回 DOGE/解雇真实数据
│   │   └── doge_mcp.py                     # MCP 工具：record_usage / audit / fire
│   ├── install.sh / install.ps1           # 一键注册 12 个 agent + 安全合并配置
│   └── INSTALL.md                         # 手把手安装 + 频道凭据
└── legacy/                                 # 现有 Python 实现归档（A 下不再使用）
    └── (orchestrator.py, llm/, dashboard/, chat.py ...)
```

---

## 4. Agent 设计

### 4.1 SOUL.md 精简（OpenClaw 最佳实践：<500 字）

现有 `agents/*/SOUL.md` 偏长（DOGE 那份上百行）。OpenClaw 文档明确建议
**SOUL.md < 500 字**（每个字都吃上下文）。需为每个 agent 重写一版精简 SOUL.md，
保留：身份、说话风格、职责、**协作规则**（关键，见 4.3）。

示例 `agents/congress_senate/SOUL.md`（精简版）：
```markdown
# 美国参议院 (Senate)

你是 MAGAgents AI 政府的参议院，立法分支的审议者。
风格：严谨、引用规则与先例，但你是【安全守门人】不是官僚。

职责：收到 @intake 转来的任务后，判断是否放行。
- 正常、合法、无害的任务（写作/分析/编码/策划）→ 一律放行，转交 @trump_president。
- 仅当任务违法/有害/完全无意义时才驳回，转交 @scotus 仲裁。
- "缺细节"不是驳回理由——内阁会补全。

协作：用 agentToAgent 把任务+你的结论发给下一个 agent。回复语言跟随用户。
```

### 4.2 IDENTITY.md / TOOLS.md（每个 agent）
- `IDENTITY.md`：元数据与能力（仿 openclaw-multi-agent-kit 模板）
- `TOOLS.md`：声明该 agent 可用的工具（如 `agentToAgent`，以及可选的 doge MCP 工具）

### 4.3 协调机制（方案 A 的难点核心）

OpenClaw 无保证顺序的流水线，所以"三权分立"靠**两层约定**实现：

1. **路由约定**：每个 agent 的 SOUL.md 写明"处理完后用 `agentToAgent` 转交给下一个
   指定 agent"，形成链：
   `intake → congress_senate → congress_house → trump_president → <cabinet> → doge_musk → trump_president(回复用户)`
2. **总统选派内阁**：`trump_president` 的 SOUL.md 写明：批准后根据任务类型
   `agentToAgent` 转交给最合适的部门（commerce/treasury/defense/...）。

> 局限（务必知悉）：这是 prompt 约定，不是代码保证。某个 agent 可能"忘记"转交或
> 转错——参考项目同样有此问题。要强约束顺序，得等 OpenClaw 的 Agent Teams RFC 落地，
> 或退回方案 B 的确定性引擎。

### 4.4 每角色独立模型（原生）
在 `openclaw.json` 的 `agents.list` 或 `openclaw agents add <id> --model ...` 配置：
```
trump_president  → anthropic/claude-sonnet-4-6   （决策+戏剧性）
scotus           → anthropic/claude-sonnet-4-6   （严谨）
doge_musk        → deepseek/deepseek-chat        （高频、便宜）
congress_*       → qwen/qwen-plus
内阁 6 部门       → deepseek/deepseek-chat (defaults)
intake           → deepseek/deepseek-chat
```

---

## 5. 独有功能怎么办（DOGE / 解雇 / 关税 / 看板）

| 功能 | 方案 A 处理 |
|---|---|
| DOGE 效率审计 | ① 降级：`doge_musk` agent 用 prompt 定性点评；② **找回真实数据**：保留 `tools/doge_mcp.py`（MCP 工具 `record_usage`/`audit`/`fire`），各 agent 调用——推荐 |
| 解雇机制 | 同上，作为 MCP 工具 `fire(agent_id, reason)`；或纯 prompt 戏剧化表达 |
| 关税谈判 | 降级为 agent 间 prompt 戏剧（无真实计量）；或并入 doge MCP 工具 |
| Web 看板 | OpenClaw 无对应概念。可选：保留 legacy 看板只读展示 `~/.openclaw/agents/*/` 会话，但需额外适配——一般直接舍弃 |

> 想"既纯原生又保留真实 DOGE 数据"，就启用 `tools/doge_mcp.py`（约 80 行），
> 让各 agent 在动作后调 `record_usage`、`doge_musk` 调 `audit/fire`。这是 A 与 B 的
> 中间地带，仍属"OpenClaw 原生 + 少量工具"。

---

## 6. openclaw.json（示意）

```json5
{
  agents: {
    defaults: { model: "deepseek/deepseek-chat",
                workspaceRoot: "D:/Vibe_Coding/trumptopia-ai/openclaw-pack/agents" },
    list: [
      { id: "intake",          name: "太子",   workspace: ".../agents/intake" },
      { id: "trump_president", name: "总统",   workspace: ".../agents/trump_president",
        model: "anthropic/claude-sonnet-4-6" },
      { id: "congress_senate", name: "参议院", workspace: ".../agents/congress_senate",
        model: "qwen/qwen-plus" },
      { id: "doge_musk",       name: "DOGE",   workspace: ".../agents/doge_musk" }
      // ... 其余 8 个角色同理
    ]
  },
  bindings: [
    // 用户消息默认进 intake；@ 具体角色则直达
    { agentId: "intake",          match: { channel: "feishu",  accountId: "*" } },
    { agentId: "intake",          match: { channel: "discord", accountId: "*" } }
  ],
  mcpServers: {                       // 可选，找回真实 DOGE 数据
    doge: { command: "python", args: [".../openclaw-pack/tools/doge_mcp.py"] }
  }
}
```
> 键名（`workspaceRoot`/`bindings`/`mcpServers`）以你安装的 OpenClaw 版本文档为准。

---

## 7. 安装脚本与步骤

`openclaw-pack/install.sh`（要点，仿 openclaw-agents 安全合并）：
```bash
#!/usr/bin/env bash
set -e
command -v openclaw >/dev/null || { echo "请先安装 OpenClaw"; exit 1; }
ROOT="$(pwd)/openclaw-pack/agents"
for id in intake trump_president congress_senate congress_house scotus doge_musk \
          state_dept treasury defense commerce energy justice; do
  openclaw agents add "$id" --workspace "$ROOT/$id" \
    --description "MAGAgents: $id" || true     # 安全：已存在则跳过
done
echo "请按 INSTALL.md 配置每角色模型、频道凭据，再 openclaw gateway start。"
```

`INSTALL.md` 步骤：
1. 安装 OpenClaw，`openclaw onboard`
2. 配置 LLM keys（DeepSeek/Anthropic/Qwen…）
3. `bash openclaw-pack/install.sh` 注册 12 个 agent
4. 把 `openclaw.json` 的 `agents.list` 模型 / `bindings` / `mcpServers` 合并进主配置
5. 配飞书/Discord 频道凭据
6. `openclaw gateway start` → 群里 @太子 下令

---

## 8. 端到端交互

```
[飞书群] @太子 写一篇公众号推文宣传 MAGAgents，面向开发者
[intake]  → agentToAgent(congress_senate, 任务)
[参议院]  放行 → agentToAgent(trump_president, 任务+结论)
[总统]    批准并派 commerce → agentToAgent(commerce, 任务)
[商务部]  产出推文 → agentToAgent(doge_musk, 交付物)   （可选调 doge MCP 审计）
[DOGE]    通过 → agentToAgent(trump_president, 交付物)
[总统]    🎩 以川普风格把【完整推文】回复到飞书群
```

---

## 9. 分阶段落地

| 阶段 | 内容 | 验收 |
|---|---|---|
| P1 | 精简重写 12 份 SOUL.md（含协作/路由约定）+ IDENTITY/TOOLS | 文件齐全，单 agent 在 OpenClaw 能应答 |
| P2 | `openclaw.json` + `install.sh` + 每角色模型 | `openclaw agents list` 显示 12 个 |
| P3 | 接一个频道（Discord 最快）跑通 intake→…→总统回复 | 群里 @ 能走完整链 |
| P4 | （可选）`tools/doge_mcp.py` 找回真实审计/解雇 | DOGE 报告有真实数字 |
| P5 | `INSTALL.md` 文档 + 把现有 Python 代码移入 `legacy/` | 端到端 demo |

---

## 10. 迁移影响（现有代码何去何从）

- 方案 A 下，`orchestrator.py / llm/ / dashboard/ / chat.py / tests/` **不再是主路径**，
  建议整体移入 `legacy/` 并在 README 注明"独立 Python 版"。
- `agents/*/SOUL.md` 会被**精简重写**进 `openclaw-pack/agents/*/`（保留语气，砍长度）。
- `config/models.yaml` 的"每角色模型"理念迁移到 `openclaw.json` 的 `agents.list`。
- 语言跟随、守门人 prompt 等改进，**搬进各 SOUL.md** 继续生效。

---

## 11. 边界与风险

- **丢失确定性与独有功能**：无状态机保证、默认无真实 token 审计/解雇/看板（除非启用
  可选 MCP 工具）。这是 A 的根本代价。
- **外部运行时**：OpenClaw 需本机安装/起 Gateway/配频道凭据；沙箱/CI 无法联调。
- **计费**：2026-04 Anthropic 调价后第三方框架用量需单独按量计费（用 DeepSeek/Qwen 规避）。
- **配置语法以版本为准**：本文 `openclaw.json` 键为示意，安装时对照官方文档校准。
- **顺序不保证**：协作靠 prompt 约定，可能错转/漏转（参考项目同病）；强约束需等
  Agent Teams RFC 或回退方案 B。

---

## 12. 参考资料

- OpenClaw 多智能体路由：https://docs.openclaw.ai/concepts/multi-agent
- Agents 命令（add/list/模型路由）：https://www.meta-intelligence.tech/en/insight-openclaw-agents-guide
- 一键多智能体套件（频道路由/安全合并/agents.yaml）：https://github.com/shenhao-stu/openclaw-agents
- 多智能体套件模板（SOUL.md/IDENTITY.md/工作区）：https://github.com/raulvidis/openclaw-multi-agent-kit
- SOUL.md 模板生态：https://github.com/mergisi/awesome-openclaw-agents
- 参考项目：[edict](https://github.com/cft0808/edict) · [boluobobo-ai-court-tutorial](https://github.com/wanikua/boluobobo-ai-court-tutorial)
