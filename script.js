document.getElementById('analyze-btn').addEventListener('click', handleAnalyze);
document.getElementById('test-btn').addEventListener('click', handleTest);

function handleAnalyze() {
    const text = document.getElementById('text-input').value;
    // Dummy analysis for now
    const result = {
        "toxicity_score": "10%",
        "analysis": "This is a safe message.",
        "emotional_support": "",
        "email_sent": "no"
    };
    updateUI(result);
}

function handleTest() {
    const heading = document.querySelector('h1');
    heading.textContent = "I'm running!";
}

function updateUI(result) {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = `
        <p><strong>Toxicity Score:</strong> ${result.toxicity_score}</p>
        <p><strong>Analysis:</strong> ${result.analysis}</p>
        <p><strong>Emotional Support:</strong> ${result.emotional_support}</p>
        <p><strong>Email Sent:</strong> ${result.email_sent}</p>
    `;
}
