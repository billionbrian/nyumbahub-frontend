async function renderAnalytics(properties) {
    const ctx = document.getElementById('viewsChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: properties.map(p => p.title),
            datasets: [{
                label: 'Views',
                data: properties.map(p => p.analytics.views),
                backgroundColor: 'rgba(46, 204, 113, 0.7)'
            }]
        },
        options: { responsive: true }
    });
}