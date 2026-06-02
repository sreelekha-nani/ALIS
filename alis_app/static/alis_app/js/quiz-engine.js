// ALIS Dynamic Quiz Engine

let currentAssessmentId = null;
let questions = [];
let currentIndex = 0;
let answers = []; // To store {question_id: x, choice: 'A'}
let startTime = 0;

function startQuiz(assessmentId) {
    currentAssessmentId = assessmentId;
    fetch(`/api/questions/${assessmentId}/`)
        .then(res => res.json())
        .then(data => {
            questions = data.questions;
            if (questions.length === 0) {
                alert("This assessment has no questions yet.");
                return;
            }
            currentIndex = 0;
            answers = [];
            startTime = Date.now();

            document.getElementById('setupScreen').style.display = 'none';
            document.getElementById('quizScreen').style.display = 'block';
            loadQuestion();
        })
        .catch(err => console.error("Question fetch error:", err));
}

function loadQuestion() {
    const q = questions[currentIndex];
    const container = document.getElementById('questionContainer');
    
    container.innerHTML = `
        <div class="animate-in">
            <div class="text-mono" style="margin-bottom: 2rem; color: var(--gold-primary);">${q.concept} // Level: ${q.difficulty}</div>
            <h2 class="h-editorial" style="font-size: 2.2rem; margin-bottom: 3rem;">${q.text}</h2>
            <div class="option-grid">
                ${['A', 'B', 'C', 'D'].map((choice, idx) => `
                    <button class="option-btn" onclick="selectOption(${q.id}, '${choice}')">
                        <span class="text-mono" style="font-size: 0.7rem; opacity: 0.5;">0${idx+1}</span>
                        ${q.options[idx]}
                    </button>
                `).join('')}
            </div>
        </div>
    `;

    document.getElementById('progressFill').style.width = `${((currentIndex) / questions.length) * 100}%`;
}

function selectOption(qId, choice) {
    answers.push({ question_id: qId, choice: choice });
    
    currentIndex++;
    if (currentIndex < questions.length) {
        loadQuestion();
    } else {
        finishQuiz();
    }
}

async function finishQuiz() {
    document.getElementById('progressFill').style.width = `100%`;
    
    const payload = {
        assessment_id: currentAssessmentId,
        answers: answers
    };

    try {
        const response = await fetch('/save-quiz-result/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            document.getElementById('quizScreen').style.display = 'none';
            document.getElementById('resultScreen').style.display = 'block';
            document.getElementById('scoreText').innerHTML = `Assessment Synced. You scored <strong>${result.score}%</strong>. Intelligence level calibrated to <strong>${result.level}</strong>.`;
        }
    } catch (err) {
        console.error("Save error:", err);
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Auto-start if assessment ID is in the template context
document.addEventListener('DOMContentLoaded', () => {
    const quizEl = document.getElementById('quizScreen');
    // If assessment data is injected by Django into a script tag or hidden field
    // For this prototype, we'll check if a specific ID was passed
    const path = window.location.pathname;
    const match = path.match(/\/quiz\/(\d+)\//);
    if (match) {
        startQuiz(match[1]);
    }
});
