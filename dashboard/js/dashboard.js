// MAGAgents 看板 — 椭圆形办公室指挥中心

const PRIORITY_CN = { critical: '紧急', high: '高', normal: '普通', low: '低' };
const STAGE_CN = { congress: '国会', scotus: '最高法院', potus: '总统', cabinet: '内阁', doge: 'DOGE' };
const STAGE_ICON = { congress: '🏛️', scotus: '⚖️', potus: '🎩', cabinet: '🏢', doge: '🐕' };
const OUTCOME_CN = { done: '已完成', fired: '已解雇', vetoed: '已否决', blocked: '已驳回', over_budget: '超预算' };

class MAGAgentsDashboard {
    constructor() {
        this.tasks = [];
        this.agents = [];
        this.posts = [];
        this.currentTab = 'kanban';
        this.currentTask = null;
        this.init();
    }

    init() {
        this.setupTabs();
        this.setupModal();
        this.setupCreateBar();
        this.loadData();
        this.startAutoRefresh();
    }

    setupTabs() {
        const tabBtns = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                tabBtns.forEach(b => b.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));
                btn.classList.add('active');
                document.getElementById(btn.dataset.tab).classList.add('active');
                this.currentTab = btn.dataset.tab;
                this.refreshCurrentTab();
            });
        });
    }

    setupModal() {
        const modal = document.getElementById('taskModal');
        modal.querySelector('.close').addEventListener('click', () => modal.classList.remove('active'));
        window.addEventListener('click', e => { if (e.target === modal) modal.classList.remove('active'); });
        modal.querySelector('.btn-approve').addEventListener('click', () => this.approveTask());
        modal.querySelector('.btn-veto').addEventListener('click', () => this.vetoTask());
        modal.querySelector('.btn-fire').addEventListener('click', () => this.fireAgent());
    }

    setupCreateBar() {
        const btn = document.getElementById('createTaskBtn');
        const input = document.getElementById('newTaskTitle');
        if (btn) btn.addEventListener('click', () => this.createTask());
        if (input) input.addEventListener('keydown', e => { if (e.key === 'Enter') this.createTask(); });
    }

    // ===== 数据 =====
    async loadData() {
        await Promise.all([
            this.fetchInto('/api/tasks', d => this.tasks = d),
            this.fetchInto('/api/agents', d => this.agents = d),
            this.fetchInto('/api/posts', d => this.posts = d),
            this.fetchInto('/api/doge', d => this.doge = d),
        ]);
        await this.fetchInto('/api/stats', d => {
            const el = document.getElementById('llmMode');
            if (el) el.textContent = d.llm_enabled ? '真实模型' : '离线模拟';
        });
        if (!this.tasks.length && !this.agents.length) this.loadMockData();
        this.renderAll();
    }

    async fetchInto(url, setter) {
        try {
            const r = await fetch(url);
            if (r.ok) setter(await r.json());
        } catch (e) { /* offline / static */ }
    }

    loadMockData() {
        this.tasks = [
            { id: 'TRUMP-001', title: '建设边境墙 API', state: 'pending', priority: 'critical', agent: 'defense' },
            { id: 'TRUMP-002', title: 'DOGE 效率审计', state: 'congress', priority: 'high', agent: 'doge_musk' },
            { id: 'TRUMP-003', title: '税改法案', state: 'potus', priority: 'high', agent: 'treasury' },
            { id: 'TRUMP-004', title: '安全审查', state: 'cabinet', priority: 'normal', agent: 'defense' },
            { id: 'TRUMP-005', title: '贸易谈判', state: 'doing', priority: 'critical', agent: 'commerce' },
            { id: 'TRUMP-006', title: '基建计划', state: 'done', priority: 'normal', agent: 'energy' }
        ];
        this.agents = [
            { id: 'trump_president', efficiency: 95, status: 'active' },
            { id: 'doge_musk', efficiency: 88, status: 'active' },
            { id: 'defense', efficiency: 94, status: 'active' },
            { id: 'commerce', efficiency: 45, status: 'warning' },
            { id: 'treasury', efficiency: 87, status: 'active' }
        ];
        this.posts = [
            { agent_id: 'trump_president', content: '边境墙 API 进展 TREMENDOUS！没人比我们造得更好！#MAGA', timestamp: new Date().toISOString() },
            { agent_id: 'doge_musk', content: '🐕 今天发现 $247.32 浪费！解雇 3 个低效智能体！排干沼泽！', timestamp: new Date().toISOString() }
        ];
    }

    // ===== 渲染 =====
    renderAll() {
        this.renderKanban();
        this.renderMonitor();
        this.renderCongress();
        this.renderDOGE();
        this.renderTruthSocial();
    }

    renderKanban() {
        const states = ['pending', 'congress', 'potus', 'cabinet', 'doing', 'done'];
        states.forEach(state => {
            const container = document.getElementById(`${state}Tasks`);
            if (!container) return;
            const stateTasks = this.tasks.filter(t => t.state === state);
            container.innerHTML = stateTasks.length
                ? stateTasks.map(t => this.createTaskCard(t)).join('')
                : '<div class="task-empty">暂无任务</div>';
            container.querySelectorAll('.task-card').forEach(card => {
                card.addEventListener('click', () => this.showTaskDetail(card.dataset.taskId));
            });
        });
    }

    createTaskCard(task) {
        const cls = task.priority === 'critical' ? 'critical' : task.priority === 'high' ? 'high-priority' : '';
        const agent = task.agent || task.assigned_agent || '未指派';
        return `
            <div class="task-card ${cls}" data-task-id="${task.id}">
                <div class="task-title">${this.escape(task.title)}</div>
                <div class="task-meta">
                    <span>👤 ${this.escape(agent)}</span>
                    <span>${PRIORITY_CN[task.priority] || task.priority}</span>
                </div>
            </div>`;
    }

    renderMonitor() {
        const total = this.tasks.length;
        const active = this.tasks.filter(t => !['done', 'vetoed', 'fired'].includes(t.state)).length;
        const completed = this.tasks.filter(t => t.state === 'done').length;
        const fired = this.agents.filter(a => a.status === 'fired').length;
        document.getElementById('totalTasks').textContent = total;
        document.getElementById('activeTasks').textContent = active;
        document.getElementById('completedTasks').textContent = completed;
        document.getElementById('firedAgents').textContent = fired;
        this.renderTaskChart();
    }

    renderTaskChart() {
        const canvas = document.getElementById('taskChart');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        canvas.width = canvas.offsetWidth; canvas.height = 240;
        const labels = ['待处理', '国会', '总统', '内阁', '执行', '完成'];
        const states = ['pending', 'congress', 'potus', 'cabinet', 'doing', 'done'];
        const counts = states.map(s => this.tasks.filter(t => t.state === s).length);
        const maxCount = Math.max(...counts, 1);
        const barWidth = canvas.width / states.length - 16;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        states.forEach((s, i) => {
            const h = (counts[i] / maxCount) * (canvas.height - 50);
            const x = i * (barWidth + 16) + 8;
            const y = canvas.height - h - 26;
            const grad = ctx.createLinearGradient(0, y, 0, y + h);
            grad.addColorStop(0, '#e0b13a'); grad.addColorStop(1, '#b8860b');
            ctx.fillStyle = grad;
            ctx.beginPath(); ctx.roundRect(x, y, barWidth, h, 6); ctx.fill();
            ctx.fillStyle = '#9aa6c0'; ctx.font = '12px sans-serif'; ctx.textAlign = 'center';
            ctx.fillText(labels[i], x + barWidth / 2, canvas.height - 6);
            ctx.fillStyle = '#e8edf7';
            ctx.fillText(counts[i], x + barWidth / 2, y - 6);
        });
    }

    renderCongress() {
        const bills = this.tasks.filter(t => t.state === 'congress');
        const html = bills.length ? bills.map(t => `
            <div class="bill-item"><span>${this.escape(t.title)}</span>
            <span class="vote-status">🗳️ 表决中</span></div>`).join('')
            : '<div class="task-empty">国会无待审法案</div>';
        document.getElementById('senateBills').innerHTML = html;
        document.getElementById('houseBills').innerHTML = bills.length ? bills.map(t => `
            <div class="bill-item"><span>${this.escape(t.title)}</span>
            <span class="vote-status">⏳ 排队中</span></div>`).join('')
            : '<div class="task-empty">众议院无待审法案</div>';
    }

    renderDOGE() {
        const agents = this.agents.length ? this.agents : [];
        // Real numbers from /api/doge (computed from actual recorded token usage).
        const doge = this.doge || {};
        const fired = (doge.agents_fired != null) ? doge.agents_fired
            : agents.filter(a => a.status === 'fired').length;
        const waste = (doge.waste != null) ? doge.waste : 0;
        const avgEff = (doge.avg_efficiency != null) ? doge.avg_efficiency
            : (agents.length ? agents.reduce((s, a) => s + (a.efficiency || 0), 0) / agents.length : 0);
        document.getElementById('wasteAmount').textContent = `$${Number(waste).toFixed(4)}`;
        document.getElementById('dogeFired').textContent = fired;
        document.getElementById('efficiencyGain').textContent = `${Math.round(avgEff)}%`;
        const tbody = document.querySelector('#leaderboardTable tbody');
        const statusCn = { active: '在岗', warning: '警告', fired: '已解雇' };
        const sorted = [...agents].sort((a, b) => (b.efficiency || 0) - (a.efficiency || 0));
        tbody.innerHTML = sorted.length ? sorted.map(a => `
            <tr>
                <td>${this.escape(a.id || a.name || '?')}</td>
                <td>${Math.round(a.efficiency || 0)}%</td>
                <td><span class="status-${a.status}">${statusCn[a.status] || a.status}</span></td>
            </tr>`).join('') : '<tr><td colspan="3" class="task-empty">暂无数据，先派个任务吧</td></tr>';
    }

    renderTruthSocial() {
        const avatars = { trump_president: '🎩', doge_musk: '🐕', scotus: '⚖️', congress_senate: '🏛️', congress_house: '🏛️' };
        const container = document.getElementById('truthPosts');
        container.innerHTML = this.posts.length ? this.posts.map(p => `
            <div class="post">
                <div class="post-header">
                    <div class="post-avatar">${avatars[p.agent_id] || '🏢'}</div>
                    <div>
                        <div class="post-author">@${this.escape(p.agent_id)}</div>
                        <div class="post-time">${this.timeAgo(p.timestamp)}</div>
                    </div>
                </div>
                <div class="post-content">${this.escape(p.content)}</div>
                <div class="post-hashtags">#MAGA #Winning</div>
            </div>`).join('') : '<div class="task-empty">还没有动态，派个任务看智能体发言</div>';
    }

    // ===== 任务详情 =====
    showTaskDetail(taskId) {
        const task = this.tasks.find(t => t.id === taskId);
        if (!task) return;
        this.currentTask = task;
        const agent = task.agent || task.assigned_agent || '未指派';
        const cost = (task.cost != null) ? `$${Number(task.cost).toFixed(5)}` : '$0';
        const tokens = task.tokens_used || 0;

        const trace = task.decision_trace || [];
        let traceHtml = '';
        if (trace.length) {
            const rows = trace.map(s => {
                const verdict = s.vote || s.decision || s.ruling || s.verdict || (s.output_preview ? '已执行' : '');
                const detail = s.reason || s.output_preview || '';
                const eff = (s.efficiency != null) ? ` · 效率 ${Number(s.efficiency).toFixed(0)}%` : '';
                return `<div class="trace-step">
                    <span class="trace-stage">${STAGE_ICON[s.stage] || '•'} ${STAGE_CN[s.stage] || (s.stage || '')}</span>
                    <span class="trace-agent">@${this.escape(s.agent || '?')}</span>
                    <span class="trace-verdict">${this.escape(verdict)}${eff}</span>
                    <div class="trace-detail">${this.escape(detail)}</div>
                </div>`;
            }).join('');
            traceHtml = `<h4>🧭 决策链</h4><div class="decision-trace">${rows}</div>`;
        }
        const badge = task.outcome
            ? `<span class="outcome-badge outcome-${task.outcome}">${OUTCOME_CN[task.outcome] || task.outcome}</span>` : '';
        const outputHtml = task.output
            ? `<h4>📄 交付物</h4><div class="task-output">${this.escape(task.output)}</div>` : '';

        document.getElementById('modalTitle').textContent = task.title;
        document.getElementById('modalBody').innerHTML = `
            <p><strong>编号：</strong>${task.id} ${badge}</p>
            <p><strong>状态：</strong>${task.state}</p>
            <p><strong>优先级：</strong>${PRIORITY_CN[task.priority] || task.priority}</p>
            <p><strong>负责：</strong>${this.escape(agent)}</p>
            <p><strong>花费：</strong>${cost} &nbsp; <strong>Token：</strong>${tokens}</p>
            <button class="btn-run" id="runAgenticBtn">▶️ 运行政府流程</button>
            ${traceHtml}${outputHtml}`;
        const runBtn = document.getElementById('runAgenticBtn');
        if (runBtn) runBtn.addEventListener('click', () => this.runAgentic(task.id));
        document.getElementById('taskModal').classList.add('active');
    }

    // ===== 动作 =====
    async createTask() {
        const input = document.getElementById('newTaskTitle');
        const title = (input.value || '').trim();
        if (!title) { this.showToast('请输入任务内容'); return; }
        const btn = document.getElementById('createTaskBtn');
        btn.disabled = true; btn.textContent = '创建中…';
        try {
            const r = await fetch('/api/task/create', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, priority: 'high' })
            });
            const res = await r.json();
            input.value = '';
            if (res.task_id && document.getElementById('autoRun').checked) {
                this.showToast('任务已创建，正在跑政府流程…');
                await fetch('/api/task/run', {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ task_id: res.task_id })
                });
                await this.loadData();
                this.showTaskDetail(res.task_id);
            } else {
                this.showToast('任务已创建');
                await this.loadData();
            }
        } catch (e) {
            this.showToast('创建失败（确认用 server.py 启动，而非纯静态）');
        } finally {
            btn.disabled = false; btn.textContent = '＋ 新建任务';
        }
    }

    async runAgentic(taskId) {
        const btn = document.getElementById('runAgenticBtn');
        if (btn) { btn.disabled = true; btn.textContent = '⏳ 政府流程运行中…'; }
        try {
            const r = await fetch('/api/task/run', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task_id: taskId })
            });
            const res = await r.json();
            await this.loadData();
            this.showTaskDetail(taskId);
            this.showToast(`完成：${OUTCOME_CN[res.outcome] || res.outcome}` + (res.llm_enabled ? '' : '（离线模式）'));
        } catch (e) {
            if (btn) { btn.disabled = false; btn.textContent = '▶️ 运行政府流程'; }
            this.showToast('运行失败（需用 server.py 启动）');
        }
    }

    async approveTask() {
        if (!this.currentTask) return;
        await fetch('/api/task/action', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_id: this.currentTask.id, action: 'approve' })
        }).catch(() => {});
        document.getElementById('taskModal').classList.remove('active');
        this.showToast('已批准'); this.loadData();
    }

    async vetoTask() {
        if (!this.currentTask) return;
        await fetch('/api/task/action', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_id: this.currentTask.id, action: 'veto', reason: '总统否决' })
        }).catch(() => {});
        document.getElementById('taskModal').classList.remove('active');
        this.showToast('已否决'); this.loadData();
    }

    async fireAgent() {
        if (!this.currentTask) return;
        const agent = this.currentTask.agent || this.currentTask.assigned_agent;
        if (agent) {
            await fetch('/api/agent/fire', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ agent_id: agent, reason: 'INEFFICIENCY' })
            }).catch(() => {});
            this.showToast(`@${agent} 你被解雇了！`);
        }
        document.getElementById('taskModal').classList.remove('active');
        this.loadData();
    }

    // ===== 工具 =====
    escape(s) {
        return String(s == null ? '' : s).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
    }

    timeAgo(ts) {
        if (!ts) return '刚刚';
        const diff = (Date.now() - new Date(ts).getTime()) / 1000;
        if (diff < 60) return '刚刚';
        if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`;
        if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`;
        return `${Math.floor(diff / 86400)} 天前`;
    }

    showToast(msg) {
        const el = document.getElementById('toast');
        if (!el) return;
        el.textContent = msg;
        el.classList.add('show');
        clearTimeout(this._toastT);
        this._toastT = setTimeout(() => el.classList.remove('show'), 2600);
    }

    startAutoRefresh() {
        this.refreshInterval = setInterval(() => {
            const modalOpen = document.getElementById('taskModal').classList.contains('active');
            if (!modalOpen) this.loadData();
        }, 8000);
    }

    refreshCurrentTab() {
        switch (this.currentTab) {
            case 'kanban': this.renderKanban(); break;
            case 'monitor': this.renderMonitor(); break;
            case 'congress': this.renderCongress(); break;
            case 'doge': this.renderDOGE(); break;
            case 'truth': this.renderTruthSocial(); break;
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new MAGAgentsDashboard();
});
