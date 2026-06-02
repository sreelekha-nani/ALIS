// Django-compatible dashboard script
const progressChartCtx = document.getElementById('progressChart').getContext('2d');
let progressChart;

function capitalize(str) { return str.charAt(0).toUpperCase() + str.slice(1); }

function updateRecommendations(level, subject) {
    const list = document.getElementById('recommendationsList');
    if (!list) return;
    list.innerHTML = '';

    const recs = {
        math: {
            Weak: [
                { title: "Basic Arithmetic Fundamentals", type: "Video", icon: "🎥" },
                { title: "Step-by-Step Addition & Subtraction", type: "Notes", icon: "📝" },
                { title: "Times Tables Practice", type: "Exercise", icon: "🧩" }
            ],
            Average: [
                { title: "Algebra Made Simple", type: "Video", icon: "🎥" },
                { title: "Percentage & Ratio Examples", type: "Practice", icon: "💻" },
                { title: "Geometry Problem Set", type: "Exercise", icon: "🧩" }
            ],
            Strong: [
                { title: "Advanced Equation Solving", type: "Challenge", icon: "🏆" },
                { title: "Calculus Introduction", type: "Course", icon: "🎓" },
                { title: "Math Olympiad Problems", type: "Competition", icon: "🔬" }
            ]
        },
        coding: {
            Weak: [
                { title: "What is Programming?", type: "Video", icon: "🎥" },
                { title: "Variables & Data Types", type: "Notes", icon: "📝" },
                { title: "Your First Loop", type: "Tutorial", icon: "🛠️" }
            ],
            Average: [
                { title: "Functions & Return Values", type: "Video", icon: "🎥" },
                { title: "Array & List Operations", type: "Practice", icon: "💻" },
                { title: "Debugging Exercises", type: "Exercise", icon: "🧩" }
            ],
            Strong: [
                { title: "Algorithm Design Patterns", type: "Course", icon: "🎓" },
                { title: "Recursion Deep Dive", type: "Challenge", icon: "🏆" },
                { title: "System Design Basics", type: "Research", icon: "🔬" }
            ]
        },
        science: {
            Weak: [
                { title: "Introduction to Physics", type: "Video", icon: "🎥" },
                { title: "Basic Chemistry Concepts", type: "Notes", icon: "📝" },
                { title: "Human Body Basics", type: "Tutorial", icon: "🛠️" }
            ],
            Average: [
                { title: "Newton's Laws Explained", type: "Video", icon: "🎥" },
                { title: "Chemical Reactions Practice", type: "Practice", icon: "💻" },
                { title: "Photosynthesis Lab", type: "Exercise", icon: "🧩" }
            ],
            Strong: [
                { title: "Quantum Physics Intro", type: "Course", icon: "🎓" },
                { title: "Organic Chemistry Problems", type: "Challenge", icon: "🏆" },
                { title: "Research Paper Analysis", type: "Research", icon: "🔬" }
            ]
        }
    };

    const subjKey = subject.toLowerCase() || 'math';
    const items = (recs[subjKey] && recs[subjKey][level]) || (recs.math[level] || recs.math.Weak);

    items.forEach(item => {
        const div = document.createElement('div');
        div.className = 'content-card';
        div.style.minWidth = '220px';
        div.style.height = '140px';
        div.innerHTML = `
            <div class="card-overlay"></div>
            <div class="card-content">
                <div class="text-mono" style="font-size: 0.6rem; color: var(--gold-primary);">${item.type}</div>
                <div class="h-editorial" style="font-size: 1.1rem; margin-top: 0.25rem;">${item.title}</div>
            </div>
        `;
        list.appendChild(div);
    });
}

function renderChart(labels, scores) {
    if (!progressChartCtx) return;
    if (progressChart) progressChart.destroy();

    progressChart = new Chart(progressChartCtx, {
        type: 'line',
        data: {
            labels: labels.length > 0 ? labels : ['No Data'],
            datasets: [{
                label: 'Accuracy %',
                data: scores.length > 0 ? scores : [0],
                borderColor: '#D4AF37',
                backgroundColor: 'rgba(212, 175, 55, 0.03)',
                borderWidth: 1,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#D4AF37',
                pointRadius: 0,
                pointHoverRadius: 5,
                pointHoverBackgroundColor: '#FFF4C4',
                pointHoverBorderColor: '#D4AF37',
                pointHoverBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { 
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(10, 10, 10, 0.9)',
                    titleFont: { family: 'Inter', size: 10 },
                    bodyFont: { family: 'Inter', size: 12 },
                    borderColor: 'rgba(212, 175, 55, 0.2)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    display: false
                },
                x: {
                    display: false
                }
            }
        }
    });
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    const level = document.getElementById('userLevelLabel')?.textContent.trim() || "Weak";
    const subject = document.getElementById('subjectLabel')?.textContent.trim() || "Math";
    
    updateRecommendations(level, subject);
    // Placeholder for chart data - in a real app, this would be fetched from a Django API
    renderChart(['Latest'], [parseInt(document.getElementById('lastScore')?.textContent) || 0]);
});
