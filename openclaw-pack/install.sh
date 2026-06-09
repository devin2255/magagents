#!/usr/bin/env bash
# MAGAgents · OpenClaw 一键注册 (Linux/macOS)
# 安全：已存在的 agent 会跳过，不覆盖你现有的主 agent。
set -e

cd "$(dirname "${BASH_SOURCE[0]}")/.."     # 项目根目录
ROOT="$(pwd)/openclaw-pack/agents"

command -v openclaw >/dev/null 2>&1 || {
  echo "❌ 未找到 openclaw，请先安装 OpenClaw 并运行 'openclaw onboard'。"; exit 1; }

# id|model（留空走 defaults）
AGENTS=(
  "chief_of_staff|"
  "trump_president|anthropic/claude-sonnet-4-6"
  "scotus|anthropic/claude-sonnet-4-6"
  "congress_senate|qwen/qwen-plus"
  "congress_house|qwen/qwen-flash"
  "doge_musk|"
  "state_dept|"
  "treasury|"
  "defense|"
  "commerce|"
  "energy|"
  "justice|"
)

for entry in "${AGENTS[@]}"; do
  id="${entry%%|*}"; model="${entry##*|}"
  args=(agents add "$id" --workspace "$ROOT/$id" --description "MAGAgents: $id")
  [ -n "$model" ] && args+=(--model "$model")
  echo "➤ 注册 $id ${model:+($model)}"
  openclaw "${args[@]}" || echo "  (已存在或失败，跳过) $id"
done

echo
echo "✅ 12 个 agent 注册完成。下一步："
echo "  1) 把 openclaw-pack/openclaw.json 的 bindings / mcpServers 合并进你的主配置"
echo "  2) 配置飞书/Discord 频道凭据"
echo "  3) openclaw gateway start  → 群里 @白宫办公厅主任 下命令"
echo "  详见 openclaw-pack/INSTALL.md"
