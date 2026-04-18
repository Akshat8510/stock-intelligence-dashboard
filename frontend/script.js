const API = window.location.origin;
let priceChart, volChart, compareChart;
let compareSelection = [];

// ─── Init ─────────────────────────────────────────────────────────────────────
async function init() {
    try {
        const response = await fetch(`${API}/companies`);
        const companies = await response.json();
        const list = document.getElementById('company-list');
        list.innerHTML = '';

        Object.entries(companies).forEach(([name, symbol]) => {
            const btn = document.createElement('button');
            btn.dataset.name   = name;
            btn.dataset.symbol = symbol;
            btn.className = 'w-full text-left px-4 py-3 rounded-xl hover:bg-gray-800 transition-all text-gray-400 hover:text-white flex justify-between items-center group';
            btn.innerHTML = `<span>${name}</span><span class="text-xs opacity-0 group-hover:opacity-100 transition-opacity text-blue-400">Analyse →</span>`;
            btn.onclick = (e) => {
                if (e.ctrlKey || e.metaKey) {
                    toggleCompareSelection(name, symbol, btn);
                } else {
                    clearCompareSelection();
                    document.querySelectorAll('#company-list button').forEach(b => b.classList.remove('active-link'));
                    btn.classList.add('active-link');
                    showSingleDashboard(name, symbol);
                }
            };
            list.appendChild(btn);
        });
    } catch (err) {
        console.error('Failed to load company list:', err);
    }

    // Load movers in background — don't block sidebar
    loadMovers();
}

// ─── Single-stock dashboard ───────────────────────────────────────────────────
async function showSingleDashboard(name, symbol) {
    document.getElementById('welcome-msg').classList.add('hidden');
    document.getElementById('compare-content').classList.add('hidden');
    document.getElementById('dashboard-content').classList.remove('hidden');

    document.getElementById('stock-name').innerText  = name;
    document.getElementById('stock-symbol').innerText = symbol;
    document.getElementById('stock-trend').innerText  = '';
    document.getElementById('insight-box').innerHTML  = '<span class="text-gray-500">Loading…</span>';

    let data, summary;
    try {
        const [dataRes, summaryRes] = await Promise.all([
            fetch(`${API}/data/${symbol}`),
            fetch(`${API}/summary/${symbol}`)
        ]);

        // Guard: both must be OK before we try to use the data
        if (!dataRes.ok || !summaryRes.ok) {
            const which = !dataRes.ok ? symbol : symbol;
            document.getElementById('insight-box').innerHTML =
                `⚠️ <span class="text-orange-400">Could not load data for <b>${name}</b>.</span>
                 <br><span class="text-gray-400 text-sm">Yahoo Finance may be rate-limiting. Try again in a few seconds.</span>`;
            return;
        }

        data    = await dataRes.json();
        summary = await summaryRes.json();
    } catch (err) {
        document.getElementById('insight-box').innerHTML =
            `❌ <span class="text-rose-400">Network error fetching ${name}.</span>`;
        console.error(err);
        return;
    }

    // Guard: API should return an array — if not, something went wrong
    if (!Array.isArray(data) || data.length === 0) {
        document.getElementById('insight-box').innerHTML =
            `⚠️ <span class="text-orange-400">No price data available for <b>${name}</b>.</span>`;
        return;
    }

    updateTrendBadge(summary.trend);
    updateStats(summary);
    renderCharts(data);
    generateInsight(data, summary);
}

function updateTrendBadge(trend) {
    const badge = document.getElementById('stock-trend');
    badge.innerText  = trend;
    badge.className  = 'px-2 py-1 rounded text-xs font-bold';
    if (trend === 'Bullish')      badge.classList.add('bg-emerald-900/40', 'text-emerald-400');
    else if (trend === 'Bearish') badge.classList.add('bg-rose-900/40',    'text-rose-400');
    else                          badge.classList.add('bg-gray-800',        'text-gray-400');
}

function updateStats(summary) {
    const cards = [
        { label: 'Current Price', value: `₹${summary.current_price}`,    color: 'text-white' },
        { label: '52W High',      value: `₹${summary['52_week_high']}`,   color: 'text-emerald-400' },
        { label: '52W Low',       value: `₹${summary['52_week_low']}`,    color: 'text-rose-400' },
        { label: 'Momentum',      value: summary.momentum_score,           color: 'text-blue-400' },
    ];
    document.getElementById('stats-grid').innerHTML = cards.map(c => `
        <div class="bg-gray-900 border border-gray-800 p-4 rounded-2xl min-w-[130px] stat-card shadow-lg">
            <p class="text-gray-500 text-[10px] uppercase font-bold tracking-widest mb-1">${c.label}</p>
            <p class="text-xl font-bold ${c.color}">${c.value}</p>
        </div>`).join('');
}

function renderCharts(stockData) {
    const ctx    = document.getElementById('stockChart').getContext('2d');
    const volCtx = document.getElementById('volatilityChart').getContext('2d');

    const labels = stockData.map(d => d.Date);
    const prices = stockData.map(d => d.Close);
    const ma7    = stockData.map(d => d.MA7);
    const vol    = stockData.map(d => d.Volatility);

    if (priceChart) priceChart.destroy();
    if (volChart)   volChart.destroy();

    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [
                { label: 'Close Price', data: prices, borderColor: '#3b82f6', borderWidth: 3,
                  pointRadius: 2, tension: 0.3, fill: true, backgroundColor: 'rgba(59,130,246,0.05)' },
                { label: '7-Day MA',    data: ma7,    borderColor: '#10b981', borderWidth: 2,
                  pointRadius: 0, borderDash: [5, 5], tension: 0.3 }
            ]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: '#64748b' }, grid: { display: false } },
                y: { ticks: { color: '#64748b' }, grid: { color: '#1e293b' } }
            }
        }
    });

    volChart = new Chart(volCtx, {
        type: 'bar',
        data: {
            labels: labels.slice(-10),
            datasets: [{ label: 'Volatility', data: vol.slice(-10),
                backgroundColor: '#6366f1', borderRadius: 4 }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { display: false }, x: { ticks: { color: '#64748b' } } }
        }
    });
}

function generateInsight(data, summary) {
    const latestVol = data[data.length - 1].Volatility;
    const box       = document.getElementById('insight-box');
    const trend     = summary.trend;
    let msg = '';

    if (latestVol > 0.025) {
        msg = `⚠️ <span class="text-orange-400">High volatility detected.</span> Expect significant price swings in coming sessions.`;
    } else if (trend === 'Bullish') {
        msg = `🚀 <span class="text-emerald-400">Bullish momentum.</span> Price is trading above its 20-day average — positive short-term signal.`;
    } else if (trend === 'Bearish') {
        msg = `📉 <span class="text-rose-400">Bearish momentum.</span> Price is below its 20-day average — watch for support levels.`;
    } else {
        msg = `✅ <span class="text-blue-400">Stable market trend.</span> Low volatility, neutral momentum — consolidation phase likely.`;
    }
    box.innerHTML = msg;
}

// ─── Compare mode ─────────────────────────────────────────────────────────────
function toggleCompareSelection(name, symbol, btn) {
    const idx = compareSelection.findIndex(s => s.symbol === symbol);
    if (idx !== -1) {
        compareSelection.splice(idx, 1);
        btn.classList.remove('compare-link');
    } else {
        if (compareSelection.length >= 2) return;
        compareSelection.push({ name, symbol });
        btn.classList.add('compare-link');
    }
    renderCompareUI();
}

function renderCompareUI() {
    const panel = document.getElementById('compare-selection');
    const btn   = document.getElementById('compare-btn');

    if (compareSelection.length === 0) {
        panel.innerHTML = '<span class="text-gray-500 italic">Select two stocks to compare</span>';
        btn.classList.add('hidden');
    } else {
        panel.innerHTML = compareSelection.map(s =>
            `<div class="text-blue-400 font-medium">• ${s.name}</div>`).join('');
        btn.classList.toggle('hidden', compareSelection.length < 2);
    }
}

function clearCompareSelection() {
    compareSelection = [];
    document.querySelectorAll('.compare-link').forEach(b => b.classList.remove('compare-link'));
    renderCompareUI();
}

async function runCompare() {
    if (compareSelection.length < 2) return;
    const [s1, s2] = compareSelection;

    document.getElementById('welcome-msg').classList.add('hidden');
    document.getElementById('dashboard-content').classList.add('hidden');
    document.getElementById('compare-content').classList.remove('hidden');
    document.getElementById('compare-subtitle').innerText =
        `${s1.name} (${s1.symbol}) vs ${s2.name} (${s2.symbol})`;

    try {
        const res = await fetch(`${API}/compare?symbol1=${s1.symbol}&symbol2=${s2.symbol}`);
        if (!res.ok) throw new Error('Compare endpoint failed');
        const data = await res.json();

        const d1  = data[s1.symbol];
        const d2  = data[s2.symbol];
        const ctx = document.getElementById('compareChart').getContext('2d');
        if (compareChart) compareChart.destroy();

        compareChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: d1.map(d => d.Date),
                datasets: [
                    { label: s1.name, data: d1.map(d => d.Normalised),
                      borderColor: '#3b82f6', borderWidth: 2.5, pointRadius: 2, tension: 0.3, fill: false },
                    { label: s2.name, data: d2.map(d => d.Normalised),
                      borderColor: '#f59e0b', borderWidth: 2.5, pointRadius: 2, tension: 0.3, fill: false }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: true, labels: { color: '#94a3b8' } },
                    tooltip: { callbacks: { label: ctx => ` ${ctx.dataset.label}: ${ctx.parsed.y.toFixed(2)}` } }
                },
                scales: {
                    x: { ticks: { color: '#64748b' }, grid: { display: false } },
                    y: { ticks: { color: '#64748b' }, grid: { color: '#1e293b' } }
                }
            }
        });
    } catch (err) {
        console.error('Compare failed:', err);
        document.getElementById('compare-subtitle').innerText += ' — data unavailable for one or both stocks';
    }
}

// ─── Gainers / Losers ─────────────────────────────────────────────────────────
async function loadMovers() {
    try {
        const res = await fetch(`${API}/gainers-losers`);
        if (!res.ok) return;
        const data  = await res.json();
        const panel = document.getElementById('movers-panel');
        const list  = document.getElementById('movers-list');

        const fmt = (m, sign) => `
            <div class="flex justify-between items-center px-2 py-1 rounded-lg ${sign > 0 ? 'bg-emerald-900/20' : 'bg-rose-900/20'}">
                <span class="${sign > 0 ? 'text-emerald-400' : 'text-rose-400'} truncate max-w-[110px]">${m.name}</span>
                <span class="font-mono text-xs ${sign > 0 ? 'text-emerald-400' : 'text-rose-400'}">${sign > 0 ? '+' : ''}${m.daily_return}%</span>
            </div>`;

        list.innerHTML =
            data.gainers.map(m => fmt(m,  1)).join('') +
            `<div class="my-1 border-t border-gray-800"></div>` +
            data.losers.map(m  => fmt(m, -1)).join('');

        panel.classList.remove('hidden');
    } catch (_) { /* silent — movers are optional */ }
}

init();