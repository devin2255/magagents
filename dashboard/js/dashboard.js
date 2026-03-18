// TRUMPTOPIA AI Dashboard - Oval Office Command Center
// Real-time monitoring and control interface

class TrumptopiaDashboard {
    constructor() {
        this.tasks = [];
        this.agents = [];
        this.posts = [];
        this.currentTab = 'kanban';
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.setupTabs();
        this.setupModal();
        this.loadData();
        this.startAutoRefresh();
        this.renderInitialData();
    }

    // Tab Navigation
    setupTabs() {
        const tabBtns = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');

        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const tabId = btn.dataset.tab;
                
                // Update active states
                tabBtns.forEach(b => b.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));
                
                btn.classList.add('active');
                document.getElementById(tabId).classList.add('active');
                
                this.currentTab = tabId;
                this.refreshCurrentTab();
            });
        });
    }

    // Modal Setup
    setupModal() {
        const modal = document.getElementById('taskModal');
        const closeBtn = modal.querySelector('.close');
        
        closeBtn.addEventListener('click', () => {
            modal.classList.remove('active');
        });

        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });

        // Action buttons
        modal.querySelector('.btn-approve').addEventListener('click', () => this.approveTask());
        modal.querySelector('.btn-veto').addEventListener('click', () => this.vetoTask());
        modal.querySelector('.btn-fire').addEventListener('click', () => this.fireAgent());
    }

    // Data Loading
    async loadData() {
        try {
            // Load from local API or mock data
            const response = await fetch('/api/tasks');
            if (response.ok) {
                this.tasks = await response.json();
            } else {
                this.loadMockData();
            }
        } catch (error) {
            console.log('Using mock data:', error);
            this.loadMockData();
        }
        this.renderAll();
    }

    loadMockData() {
        this.tasks = [
            { id: 'TRUMP-001', title: 'Build Border Wall API', state: 'pending', priority: 'critical', agent: 'defense', created: new Date().toISOString() },
            { id: 'TRUMP-002', title: 'DOGE Efficiency Audit', state: 'congress', priority: 'high', agent: 'doge_musk', created: new Date().toISOString() },
            { id: 'TRUMP-003', title: 'Tax Reform Bill', state: 'potus', priority: 'high', agent: 'treasury', created: new Date().toISOString() },
            { id: 'TRUMP-004', title: 'Security Review', state: 'cabinet', priority: 'normal', agent: 'defense', created: new Date().toISOString() },
            { id: 'TRUMP-005', title: 'Trade Deal Negotiation', state: 'doing', priority: 'critical', agent: 'commerce', created: new Date().toISOString() },
            { id: 'TRUMP-006', title: 'Infrastructure Plan', state: 'done', priority: 'normal', agent: 'energy', created: new Date().toISOString() }
        ];

        this.agents = [
            { id: 'trump_president', name: 'POTUS', efficiency: 95, status: 'active' },
            { id: 'doge_musk', name: 'DOGE', efficiency: 88, status: 'active' },
            { id: 'defense', name: 'Defense', efficiency: 94, status: 'active' },
            { id: 'commerce', name: 'Commerce', efficiency: 45, status: 'warning' },
            { id: 'treasury', name: 'Treasury', efficiency: 87, status: 'active' },
            { id: 'congress_senate', name: 'Senate', efficiency: 72, status: 'active' }
        ];

        this.posts = [
            { agent: 'trump_president', content: 'TREMENDOUS progress on the Border Wall API! Nobody builds better APIs than us!!! #MAGA #Winning', time: '2 min ago', avatar: '🎩' },
            { agent: 'doge_musk', content: '🐕 Found $247.32 in waste today! Fired 3 inefficient agents! DRAINING THE SWAMP!!!', time: '5 min ago', avatar: '🐕' },
            { agent: 'congress_senate', content: 'Bill passed with 2/3 majority! Great work from both sides of the aisle.', time: '15 min ago', avatar: '🏛️' }
        ];
    }

    // Render Methods
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
            container.innerHTML = stateTasks.map(task => this.createTaskCard(task)).join('');
            
            // Add click handlers
            container.querySelectorAll('.task-card').forEach(card => {
                card.addEventListener('click', () => this.showTaskDetail(card.dataset.taskId));
            });
        });
    }

    createTaskCard(task) {
        const priorityClass = task.priority === 'critical' ? 'critical' : task.priority === 'high' ? 'high-priority' : '';
        return `
            <div class="task-card ${priorityClass}" data-task-id="${task.id}">
                <div class="task-title">${task.title}</div>
                <div class="task-meta">
                    <span>${task.agent || 'Unassigned'}</span>
                    <span>${task.priority.toUpperCase()}</span>
                </div>
            </div>
        `;
    }

    renderMonitor() {
        const total = this.tasks.length;
        const active = this.tasks.filter(t => !['done', 'cancelled'].includes(t.state)).length;
        const completed = this.tasks.filter(t => t.state === 'done').length;
        const fired = this.agents.filter(a => a.status === 'fired').length;

        document.getElementById('totalTasks').textContent = total;
        document.getElementById('activeTasks').textContent = active;
        document.getElementById('completedTasks').textContent = completed;
        document.getElementById('firedAgents').textContent = fired;

        // Render chart
        this.renderTaskChart();
    }

    renderTaskChart() {
        const canvas = document.getElementById('taskChart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const states = ['pending', 'congress', 'potus', 'cabinet', 'doing', 'done'];
        const counts = states.map(s => this.tasks.filter(t => t.state === s).length);
        
        // Simple bar chart
        const maxCount = Math.max(...counts, 1);
        const barWidth = canvas.width / states.length - 10;
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        states.forEach((state, i) => {
            const height = (counts[i] / maxCount) * (canvas.height - 30);
            const x = i * (barWidth + 10) + 5;
            const y = canvas.height - height - 20;
            
            ctx.fillStyle = '#D4AF37';
            ctx.fillRect(x, y, barWidth, height);
            
            ctx.fillStyle = '#fff';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(state, x + barWidth/2, canvas.height - 5);
            ctx.fillText(counts[i], x + barWidth/2, y - 5);
        });
    }

    renderCongress() {
        // Render Senate bills
        const senateBills = this.tasks.filter(t => t.state === 'congress');
        document.getElementById('senateBills').innerHTML = senateBills.map(task => `
            <div class="bill-item">
                <span>${task.title}</span>
                <span class="vote-status">🗳️ Voting...</span>
            </div>
        `).join('');

        // Render House bills
        document.getElementById('houseBills').innerHTML = senateBills.map(task => `
            <div class="bill-item">
                <span>${task.title}</span>
                <span class="vote-status">⏳ Queue</span>
            </div>
        `).join('');
    }

    renderDOGE() {
        // Calculate waste metrics
        const waste = this.agents.reduce((sum, a) => sum + (100 - a.efficiency) * 10, 0);
        const fired = this.agents.filter(a => a.status === 'fired').length;
        const avgEff = this.agents.reduce((sum, a) => sum + a.efficiency, 0) / this.agents.length;
        const gain = Math.round((95 - avgEff) * 2);

        document.getElementById('wasteAmount').textContent = `$${waste.toFixed(2)}`;
        document.getElementById('dogeFired').textContent = fired;
        document.getElementById('efficiencyGain').textContent = `${gain}%`;

        // Render leaderboard
        const tbody = document.querySelector('#leaderboardTable tbody');
        const sortedAgents = [...this.agents].sort((a, b) => b.efficiency - a.efficiency);
        
        tbody.innerHTML = sortedAgents.map(agent => `
            <tr>
                <td>${agent.name}</td>
                <td>${agent.efficiency}%</td>
                <td><span class="status-${agent.status}">${agent.status}</span></td>
            </tr>
        `).join('');
    }

    renderTruthSocial() {
        const container = document.getElementById('truthPosts');
        container.innerHTML = this.posts.map(post => `
            <div class="post">
                <div class="post-header">
                    <div class="post-avatar">${post.avatar}</div>
                    <div>
                        <div class="post-author">@${post.agent}</div>
                        <div class="post-time">${post.time}</div>
                    </div>
                </div>
                <div class="post-content">${post.content}</div>
                <div class="post-hashtags">#MAGA #Winning #BestAgents</div>
            </div>
        `).join('');
    }

    // Actions
    showTaskDetail(taskId) {
        const task = this.tasks.find(t => t.id === taskId);
        if (!task) return;

        document.getElementById('modalTitle').textContent = task.title;
        document.getElementById('modalBody').innerHTML = `
            <p><strong>ID:</strong> ${task.id}</p>
            <p><strong>State:</strong> ${task.state}</p>
            <p><strong>Priority:</strong> ${task.priority}</p>
            <p><strong>Assigned:</strong> ${task.agent || 'Unassigned'}</p>
            <p><strong>Created:</strong> ${new Date(task.created).toLocaleString()}</p>
        `;

        document.getElementById('taskModal').classList.add('active');
        this.currentTask = task;
    }

    approveTask() {
        if (this.currentTask) {
            this.currentTask.state = 'cabinet';
            this.addPost('trump_president', `✅ APPROVED ${this.currentTask.title}! TREMENDOUS!!!`, '🎩');
            this.renderAll();
            document.getElementById('taskModal').classList.remove('active');
        }
    }

    vetoTask() {
        if (this.currentTask) {
            this.currentTask.state = 'cancelled';
            this.addPost('trump_president', `❌ VETOED ${this.currentTask.title}! Total disaster!!!`, '🎩');
            this.renderAll();
            document.getElementById('taskModal').classList.remove('active');
        }
    }

    fireAgent() {
        if (this.currentTask && this.currentTask.agent) {
            const agent = this.agents.find(a => a.id === this.currentTask.agent);
            if (agent) {
                agent.status = 'fired';
                this.addPost('trump_president', `@${agent.name} You're FIRED!!! Incompetent!!!`, '🎩');
                this.renderAll();
            }
            document.getElementById('taskModal').classList.remove('active');
        }
    }

    addPost(agent, content, avatar) {
        this.posts.unshift({
            agent,
            content,
            avatar,
            time: 'Just now'
        });
        if (this.posts.length > 50) this.posts.pop();
    }

    // Auto Refresh
    startAutoRefresh() {
        this.refreshInterval = setInterval(() => {
            this.refreshCurrentTab();
        }, 5000);
    }

    refreshCurrentTab() {
        switch(this.currentTab) {
            case 'kanban': this.renderKanban(); break;
            case 'monitor': this.renderMonitor(); break;
            case 'congress': this.renderCongress(); break;
            case 'doge': this.renderDOGE(); break;
            case 'truth': this.renderTruthSocial(); break;
        }
    }

    renderInitialData() {
        this.renderAll();
    }
}

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new TrumptopiaDashboard();
});
