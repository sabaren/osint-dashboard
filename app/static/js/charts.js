// OSINT Dashboard — Chart.js configuration (sabare.net theme)

Chart.defaults.color = '#68e1ff';
Chart.defaults.borderColor = 'rgba(0, 42, 53, 0.4)';
Chart.defaults.font.family = 'Comfortaa, cursive';

const sabareColors = ['#68e1ff', '#a8fff0', '#00bfff', '#00abe5', '#0067a7', '#004774', '#34d399', '#fbbf24'];

function createSourceChart(canvasId, data) {
    if (!canvasId || !data) return;
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data).map(s => s.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())),
            datasets: [{
                data: Object.values(data),
                backgroundColor: sabareColors.slice(0, Object.keys(data).length),
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#68e1ff', padding: 15 } }
            }
        }
    });
}

function createTypeChart(canvasId, data) {
    if (!canvasId || !data) return;
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data).map(t => t.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())),
            datasets: [{
                label: 'Count',
                data: Object.values(data),
                backgroundColor: '#00bfff',
                borderRadius: 4,
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true, ticks: { color: '#68e1ff' }, grid: { color: 'rgba(0, 42, 53, 0.4)' } },
                x: { ticks: { color: '#68e1ff' }, grid: { display: false } }
            },
            plugins: { legend: { display: false } }
        }
    });
}
