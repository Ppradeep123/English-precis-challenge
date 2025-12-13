// Global variables
let currentParagraph = '';

// DOM elements
const startSection = document.getElementById('start-section');
const challengeSection = document.getElementById('challenge-section');
const resultsSection = document.getElementById('results-section');
const loading = document.getElementById('loading');

const startBtn = document.getElementById('start-btn');
const checkBtn = document.getElementById('check-btn');
const tryAgainBtn = document.getElementById('try-again-btn');
const newParagraphBtn = document.getElementById('new-paragraph-btn');
const refreshParagraphBtn = document.getElementById('refresh-paragraph-btn');

const originalText = document.getElementById('original-text');
const wordCount = document.getElementById('word-count');
const precisInput = document.getElementById('precis-input');
const precisWordCount = document.getElementById('precis-word-count');

// Event listeners
startBtn.addEventListener('click', startChallenge);
checkBtn.addEventListener('click', checkPrecis);
tryAgainBtn.addEventListener('click', startChallenge);
newParagraphBtn.addEventListener('click', startChallenge);
refreshParagraphBtn.addEventListener('click', refreshParagraph);
precisInput.addEventListener('input', updateWordCount);

// Functions
async function startChallenge() {
    showLoading(true);
    hideAllSections();
    
    try {
        const response = await fetch('/get_paragraph', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentParagraph = data.paragraph;
            originalText.textContent = data.paragraph;
            wordCount.textContent = data.word_count;
            precisInput.value = '';
            updateWordCount();
            
            showSection(challengeSection);
        } else {
            alert('Error loading paragraph: ' + data.error);
            showSection(startSection);
        }
    } catch (error) {
        alert('Network error: ' + error.message);
        showSection(startSection);
    }
    
    showLoading(false);
}

async function checkPrecis() {
    const precisText = precisInput.value.trim();
    
    if (!precisText) {
        alert('Please write a précis before checking.');
        return;
    }
    
    showLoading(true);
    hideAllSections();
    
    try {
        const response = await fetch('/evaluate_precis', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                original_text: currentParagraph,
                precis_text: precisText
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data.results);
            showSection(resultsSection);
        } else {
            alert('Evaluation error: ' + data.error);
            showSection(challengeSection);
        }
    } catch (error) {
        alert('Network error: ' + error.message);
        showSection(challengeSection);
    }
    
    showLoading(false);
}

function displayResults(results) {
    document.getElementById('total-score').textContent = results.total_score;
    document.getElementById('semantic-score').textContent = results.semantic_score;
    document.getElementById('ai-score').textContent = results.ai_comparison_score;
    document.getElementById('grammar-score').textContent = results.grammar_score;
    document.getElementById('length-score').textContent = results.length_score;
    document.getElementById('feedback').textContent = results.feedback;
    document.getElementById('ai-summary').textContent = results.ai_summary;
}

async function refreshParagraph() {
    showLoading(true);
    
    try {
        const response = await fetch('/get_paragraph', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentParagraph = data.paragraph;
            originalText.textContent = data.paragraph;
            wordCount.textContent = data.word_count;
            precisInput.value = '';
            updateWordCount();
        } else {
            alert('Error loading new paragraph: ' + data.error);
        }
    } catch (error) {
        alert('Network error: ' + error.message);
    }
    
    showLoading(false);
}

function updateWordCount() {
    const words = precisInput.value.trim().split(/\s+/).filter(word => word.length > 0);
    precisWordCount.textContent = words.length;
}

function showSection(section) {
    section.classList.remove('hidden');
}

function hideAllSections() {
    startSection.classList.add('hidden');
    challengeSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
}

function showLoading(show) {
    if (show) {
        loading.classList.remove('hidden');
    } else {
        loading.classList.add('hidden');
    }
}