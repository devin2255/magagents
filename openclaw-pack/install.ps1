# MAGAgents · OpenClaw 一键注册 (Windows PowerShell)
# 安全：已存在的 agent 会跳过。
$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..")     # 项目根目录
$Root = Join-Path (Get-Location) "openclaw-pack\agents"

if (-not (Get-Command openclaw -ErrorAction SilentlyContinue)) {
    Write-Host "❌ 未找到 openclaw，请先安装 OpenClaw 并运行 'openclaw onboard'。"
    exit 1
}

$agents = @(
    @{ id = "intake";          model = "" },
    @{ id = "trump_president"; model = "anthropic/claude-sonnet-4-6" },
    @{ id = "scotus";          model = "anthropic/claude-sonnet-4-6" },
    @{ id = "congress_senate"; model = "qwen/qwen-plus" },
    @{ id = "congress_house";  model = "qwen/qwen-flash" },
    @{ id = "doge_musk";       model = "" },
    @{ id = "state_dept";      model = "" },
    @{ id = "treasury";        model = "" },
    @{ id = "defense";         model = "" },
    @{ id = "commerce";        model = "" },
    @{ id = "energy";          model = "" },
    @{ id = "justice";         model = "" }
)

foreach ($a in $agents) {
    $ws = Join-Path $Root $a.id
    $argList = @("agents", "add", $a.id, "--workspace", $ws, "--description", "MAGAgents: $($a.id)")
    if ($a.model) { $argList += @("--model", $a.model) }
    Write-Host "➤ 注册 $($a.id) $($a.model)"
    try { & openclaw @argList } catch { Write-Host "  (已存在或失败，跳过) $($a.id)" }
}

Write-Host ""
Write-Host "✅ 12 个 agent 注册完成。下一步见 openclaw-pack\INSTALL.md"
