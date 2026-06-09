# MAGAgents · OpenClaw 原生包 — 安装指南

把 MAGAgents 作为**纯 OpenClaw agent 包**运行：12 个政府角色都是 OpenClaw 原生
agent，群里 @ 白宫办公厅主任 即可下令，三权分立流程由 agent 间消息流转完成。

> ⚠️ OpenClaw 是外部运行时，需在你本机安装。本包提供全部 agent / 配置 / 脚本；
> 具体 CLI 与 `openclaw.json` 键名以你安装的 OpenClaw 版本官方文档为准。

---

## 前置
- 已安装 [OpenClaw](https://docs.openclaw.ai) 并完成 `openclaw onboard`
- 至少一个 LLM 提供商的 API Key（推荐 DeepSeek；总统/最高法院默认用 Claude，
  也可在 `agents.yaml` 改成 deepseek/qwen 省钱）

---

## 步骤

### 1. 配置模型 API Key
按 OpenClaw 文档把各提供商 key 配好（DeepSeek / Anthropic / Qwen…）。
若启用 DOGE 真实审计工具，确保运行 OpenClaw 的环境也能读到这些 key。

### 2. 一键注册 12 个 agent
```bash
# Linux / macOS
bash openclaw-pack/install.sh
# Windows PowerShell
powershell -ExecutionPolicy Bypass -File openclaw-pack\install.ps1
```
脚本会 `openclaw agents add` 注册 chief_of_staff + 11 个角色（已存在则跳过，不覆盖你现有 agent）。
`openclaw agents list` 应能看到这 12 个。

### 3. 合并 bindings / mcpServers 到主配置
把 `openclaw-pack/openclaw.json` 里的 `bindings`（频道路由到 chief_of_staff）和
`mcpServers.doge`（可选 DOGE 工具）合并进你的 `~/.openclaw/openclaw.json`。
（手动合并，或用 `jq` 安全 merge，**不要整体覆盖**你的主配置。）

### 4. 配置聊天频道
按 OpenClaw 文档接入一个频道（最快是 Discord Bot Token；国内用飞书 App ID/Secret）。
`bindings` 已把该频道的入站消息默认路由到 `chief_of_staff`。

### 5. 启动
```bash
openclaw gateway start
```
在群里：`@白宫办公厅主任 写一篇公众号推文宣传 MAGAgents，面向开发者`
→ chief_of_staff 会依次咨询 参议院→总统→内阁→DOGE，最后把完整推文回复到群里。

---

## 可选：找回真实 DOGE 审计/解雇数据
默认 `doge_musk` 仅凭 prompt 定性点评。要恢复 MAGAgents 的**真实 token 审计与解雇**：
```bash
pip install mcp                       # 安装 MCP SDK
```
确保 `openclaw.json` 的 `mcpServers.doge` 指向 `openclaw-pack/tools/doge_mcp.py`。
内阁 agent 执行后调 `doge.record_usage`，`doge_musk` 调 `doge.audit` / `doge.fire`，
数据写入项目 `data/`（与独立 Python 版共享）。

---

## 自定义
- **改某角色模型**：编辑 `agents.yaml` / `openclaw.json` 的对应 `model`，重跑 install 或
  `openclaw agents update <id> --model ...`。
- **改人格/职责**：编辑 `openclaw-pack/agents/<id>/SOUL.md`（保持 <500 字）。
- **加新部门**：在 `agents/` 加目录 + SOUL.md，并在 `openclaw.json` 的 `agents.list` 登记。

---

## 与独立 Python 版的关系
本包是"方案 A：全量原生迁移"。项目根目录的 `orchestrator.py / chat.py / dashboard/`
是独立 Python 版（不依赖 OpenClaw），两者可并存：
- 想要**聊天平台 + 纯 OpenClaw 框架** → 用本包
- 想要**确定性流水线 + 看板 + 真实审计（无需 OpenClaw）** → 用独立 Python 版

详见 [docs/OPENCLAW_NATIVE_PLAN.md](../docs/OPENCLAW_NATIVE_PLAN.md)。
