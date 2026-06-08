# MAGAgents 🇺🇸

**让 AI 智能体再次伟大！(Make AI Agents Great Again!)**

一个川普风格、以美国政府体制为灵感的 AI 多智能体系统，特性包括：
- 三权分立：立法、行政、司法
- DOGE（政府效率部）监督
- “你被解雇了！(You're Fired!)”机制
- Truth Social 社交媒体风格的消息播报
- 基于关税的资源谈判

![Progress](https://img.shields.io/badge/Progress-100%25-brightgreen)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)

> 🌐 Language / 语言：**简体中文** | [English](README.md)

> ⚠️ 这是一个用于学习目的的**戏仿 / 讽刺**项目，与任何政治竞选或政府机构无关。

## 🎩 功能特性

### 🇺🇸 政府三权分立

| 分支 | 智能体 | 职责 |
|------|--------|------|
| **行政（Executive）** | trump_president, state_dept, treasury, defense, commerce, energy, justice | 任务执行、最终决策 |
| **立法（Legislative）** | congress_senate, congress_house | 立法、预算审批 |
| **司法（Judicial）** | scotus | 争议裁决、合宪性审查 |
| **监督（Oversight）** | doge_musk | 效率审计、浪费检测 |

### 🔥 核心功能

1. **🐕 DOGE 效率审计**
   - 每日浪费报告
   - 智能体绩效跟踪
   - 自动效率评分
   - 解雇建议

2. **🔥 “你被解雇了！”机制**
   - 解雇表现不佳的智能体
   - 生成解雇证书
   - 24 小时冷静期
   - 社交分享集成

3. **📱 Truth Social 集成**
   - 所有决策公开发布
   - 川普风格的消息格式化
   - 实时信息流
   - #MAGA 话题标签

4. **💰 基于关税的资源谈判**
   - 智能体之间用关税进行谈判
   - 基于绩效的税率（5% - 75%）
   - 贸易战模拟
   - 公平贸易执行

5. **⚖️ 三权制衡**
   - 国会起草并审批
   - 总统签署或否决
   - 最高法院审查
   - DOGE 全程审计

## 📚 致谢与参考

本项目受以下开源项目启发并有所参考：

### [edict](https://github.com/cft0808/edict) by @cft0808
“三省六部”多智能体系统。MAGAgents 参考了其架构设计，包括：
- 基于状态机的任务流转管理
- 智能体通信的权限矩阵
- 自动化任务派发系统
- 进度跟踪与审计机制

### [boluobobo-ai-court-tutorial](https://github.com/wanikua/boluobobo-ai-court-tutorial) by @wanikua
AI 法庭 /“当皇上”多智能体系统。MAGAgents 受其启发：
- 基于角色的智能体人格设计（SOUL.md）
- 层级化的政府结构隐喻
- 实时看板（Dashboard）理念
- 多渠道集成模式

这两个项目都是将古代/帝制治理结构应用于 AI 多智能体系统的优秀范例。MAGAgents 将这些理念改造为美国政府体制，并加入川普风格的讽刺。

## 🚀 快速开始

### 方式一：Docker（推荐）

```bash
# 克隆并使用 Docker Compose 运行
git clone <repository-url>
cd trumptopia-ai
docker-compose up -d

# 访问看板
open http://localhost:7892
```

### 方式二：手动安装

```bash
# 克隆仓库
git clone <repository-url>
cd trumptopia-ai

# 安装依赖（核心功能仅依赖 Python 标准库）
pip install -r requirements.txt

# 运行测试
python3 tests/test_magagents.py

# 启动看板与调度器
bash scripts/run_loop.sh

# 或分别启动各组件
python3 dashboard/server.py --static  # 仅看板
python3 -c "from orchestrator import MAGAgentsOrchestrator; MAGAgentsOrchestrator(enable_scheduler=True)"  # 仅调度器
```

### 使用示例

```python
from orchestrator import MAGAgentsOrchestrator, AgentState

# 初始化
orch = MAGAgentsOrchestrator()

# 创建任务
task = orch.create_task(
    title="构建新 API",
    description="创建 REST API 接口",
    priority="high"
)

# 走政府流程
orch.transition_state(task.id, AgentState.CONGRESS)
orch.transition_state(task.id, AgentState.POTUS)
orch.approve_task(task.id)  # 总统批准

# 记录进度
orch.record_task_progress(
    task.id, "defense",
    tokens=1000,
    cost=0.01,
    success=True,
    response_time=60.0
)

# 查看 DOGE 报告
doge_report = orch.get_doge_report()
print(f"发现浪费：${doge_report['total_waste']}")

# 解雇低效智能体
if doge_report['agents_fired'] > 0:
    cert = orch.fire_agent("bad_agent", "INEFFICIENCY")
    print(f"已解雇！证书：{cert.certificate_id}")
```

## 🖥️ 看板（Dashboard）

**椭圆形办公室看板（Oval Office Dashboard）** 提供实时可视化：

```bash
# 启动看板
python3 dashboard/server.py --static

# 打开浏览器
http://localhost:7892
```

**功能：**
- 📋 **任务板**：所有任务的看板视图
- 📊 **监控**：统计数据与图表
- 🏛️ **国会**：投票与法案状态
- 🐕 **DOGE**：效率报告
- 📱 **Truth Social**：实时消息流

## 🛠️ 命令行工具

### 看板 CLI

从命令行管理任务：

```bash
# 更新任务状态
python3 scripts/kanban_update.py state TRUMP-001 doing

# 添加进度与待办项
python3 scripts/kanban_update.py progress TRUMP-001 "完成 50%" \
    "设计:completed|编码:in-progress|测试:pending"

# 标记任务完成
python3 scripts/kanban_update.py done TRUMP-001 \
    "https://github.com/..." "API 已实现"

# 列出所有任务
python3 scripts/kanban_update.py list

# 显示任务详情
python3 scripts/kanban_update.py show TRUMP-001
```

## 📊 项目结构

```
trumptopia-ai/
├── agents/                    # 智能体人格设定
│   ├── trump_president/SOUL.md
│   ├── doge_musk/SOUL.md
│   ├── congress_senate/SOUL.md
│   ├── congress_house/SOUL.md
│   ├── scotus/SOUL.md
│   ├── state_dept/SOUL.md
│   ├── treasury/SOUL.md
│   ├── defense/SOUL.md
│   ├── commerce/SOUL.md
│   ├── energy/SOUL.md
│   └── justice/SOUL.md
├── dashboard/                 # Web 界面
│   ├── dashboard.html
│   ├── css/dashboard.css
│   ├── js/dashboard.js
│   └── server.py
├── scripts/                   # 命令行工具
│   ├── kanban_update.py       # 任务管理 CLI
│   ├── run_loop.sh            # 启动脚本
│   └── file_lock.py           # 并发控制
├── docs/                      # 文档
│   ├── ARCHITECTURE.md        # 详细架构
│   └── API.yaml               # API 规格
├── tests/                     # 测试套件
│   └── test_magagents.py
├── data/                      # 运行时数据
├── reports/                   # 进度报告
├── trump_style.py             # 消息格式化
├── doge_auditor.py            # 效率审计
├── firing_mechanism.py        # 解雇系统
├── tariff_negotiator.py       # 资源交易
├── orchestrator.py            # 主编排器
├── scheduler.py               # 自动调度器
├── progress_reporter.py       # 进度跟踪
├── Dockerfile                 # Docker 镜像
├── docker-compose.yml         # Docker Compose
├── README.md                  # 英文说明
└── README.zh-CN.md            # 本文件
```

## 🤖 真实 LLM 模式（可选、可插拔）

默认情况下 MAGAgents 跑在**离线模板模式**（无 AI、无需 key、结果确定）。
你可以选择接入**真实大模型**，而且**每个角色能用不同的模型**
（比如总统用 Claude、DOGE 用 DeepSeek、国会用 Qwen）。

```bash
# 1. 安装可选依赖
pip install -r requirements-llm.txt

# 2. 配置 key（只填你要用的）
cp .env.example .env        # 然后编辑 .env
export DEEPSEEK_API_KEY=sk-...

# 3. 运行 —— 角色现在用真模型说话/决策
python demo.py
```

- **每角色模型**：改 `config/models.yaml` 的 `agents:` 段；没列的角色走 `default`。
- **支持厂商**：DeepSeek、OpenAI、通义千问 Qwen(DashScope)、Kimi、OpenRouter、本地
  (Ollama/vLLM) 走 OpenAI 兼容适配器；Claude 走 Anthropic 适配器。
- **临时覆盖**：`MAGAGENTS_AGENT_TRUMP_PRESIDENT_MODEL=claude-sonnet-4-5`
- **强制离线**：`MAGAGENTS_LLM_ENABLED=off`
- **优雅降级**：没配 key（或没装依赖）时自动回退模板模式 —— `demo.py` 和测试永远能跑。
- 真实 token 用量会进入系统摘要（`llm_usage`）并喂给 DOGE 审计。

> 🔒 API Key 只从环境变量读取，绝不提交（`.env` 已加入 .gitignore）。

## 🧪 测试

运行完整测试套件：

```bash
# 运行所有测试
python3 tests/test_magagents.py

# 详细输出
python3 tests/test_magagents.py -v
```

测试覆盖：
- ✅ 川普风格消息格式化
- ✅ DOGE 效率审计
- ✅ 解雇机制
- ✅ 关税谈判
- ✅ 状态编排
- ✅ 集成工作流

## ⏰ 自动进度报告

使用 cron 设置每 10 分钟一次的进度报告：

```bash
# 编辑 crontab
crontab -e

# 添加以下一行，每 10 分钟执行一次
# （cron_progress.sh 会自动根据脚本所在位置推导项目目录）
*/10 * * * * /path/to/trumptopia-ai/cron_progress.sh

# 或先运行一次进行测试
bash /path/to/trumptopia-ai/cron_progress.sh
```

报告会带时间戳保存到 `reports/` 目录。

## 🎭 智能体人格

### 唐纳德·川普（总统 / POTUS）
- **风格**：全大写、感叹号、TREMENDOUS（了不起）
- **权力**：最终决策、否决、解雇
- **口头禅**：“你被解雇了！(You're FIRED!!!)”

### 埃隆·马斯克（DOGE）
- **风格**：技术化、数据驱动、梗文化
- **权力**：审计一切、提出解雇建议
- **口头禅**：“🐕 满满的效率，满满的节省。”

### 国会（Congress）
- **参议院（Senate）**：审议型，重大决策需 2/3 多数
- **众议院（House）**：高效，聚焦预算，掌握弹劾权

### 最高法院（Supreme Court）
- **风格**：正式、重视先例
- **权力**：最终仲裁、合宪性审查

## 💰 关税系统

| 绩效 | 关税率 | 说明 |
|------|--------|------|
| 卓越（>80%） | 5% | 优惠税率 |
| 良好（60-80%） | 10% | 正常税率 |
| 警告（30-60%） | 25% | 高关税 |
| 危急（<30%） | 50% | 紧急税率 |
| 即将解雇 | 75% | 惩罚性税率 |

## 📈 进度跟踪

查看项目进度：

```bash
# 生成报告
python3 progress_reporter.py

# 查看最新报告
cat reports/latest_progress.json | python3 -m json.tool
```

进度内容包括：
- 代码行数
- 测试状态
- 智能体配置
- 核心模块完成度
- 川普式鼓励语

## 🎩 交互示例

### 创建任务
```
用户：创建 API 接口
总统：TREMENDOUS 的主意！让 @commerce 来处理！
      没人的 API 比我们更好！！！#MAGA
```

### DOGE 审计
```
DOGE：🐕 今天发现 $247.32 的浪费！
      @commerce 效率：23% —— 解雇！
      @defense 效率：94% —— 堪称典范！
```

### 解雇智能体
```
总统：@commerce 你被解雇了！！！
      彻头彻尾的灾难！浪费美国的 Token！！！
      太可悲了！#MAGA
```

### 贸易谈判
```
财政部：需要从国防部调 5000 Token
国防部：25% 关税 = 共 6250
财政部：太高了！还价：10%
国防部：成交！5500 Token
```

## 🤝 贡献

1. Fork 本仓库
2. 创建特性分支
3. 为新功能添加测试
4. 提交 Pull Request

## 📜 许可证

MIT License —— 让 AI 智能体再次伟大！

---

**免责声明**：这是一个用于教育目的的戏仿 / 讽刺项目，与任何政治竞选或政府机构无关。

*“没人的 AI 智能体比我们更好。相信我！”* —— 川普总统（大概吧）
