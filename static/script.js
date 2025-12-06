document.getElementById('analyze-btn').addEventListener('click', handleAnalyze);
document.getElementById('screenshot-upload').addEventListener('change', handleImageUpload);
document.getElementById('new-check-btn').addEventListener('click', resetForm);
document.getElementById('remove-image').addEventListener('click', removeImage);

let uploadedImageBase64 = null;

async function handleAnalyze() {
    const text = document.getElementById('text-input').value.trim();
    const parentEmail = document.getElementById('parent-email').value.trim();
    
    if (!text && !uploadedImageBase64) {
        alert('Please enter a message or upload a screenshot to analyze.');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                image_base64: uploadedImageBase64,
                parent_email: parentEmail
            })
        });

        if (!response.ok) {
            throw new Error('Analysis failed');
        }

        const result = await response.json();
        displayResults(result);
    } catch (error) {
        console.error('Error:', error);
        alert('Something went wrong during analysis. Please try again.');
    } finally {
        showLoading(false);
    }
}

function displayResults(result) {
    document.querySelector('.input-section').style.display = 'none';
    document.getElementById('results-section').style.display = 'block';

    const score = result.toxicity_score;
    const toxicityFill = document.getElementById('toxicity-fill');
    const toxicityScore = document.getElementById('toxicity-score');
    
    toxicityFill.style.width = score + '%';
    toxicityScore.textContent = score + '%';

    let levelClass = 'low';
    if (score >= 70) levelClass = 'extreme';
    else if (score >= 50) levelClass = 'high';
    else if (score >= 30) levelClass = 'medium';

    toxicityFill.className = 'meter-fill ' + levelClass;
    toxicityScore.className = 'score-value ' + levelClass;

    document.getElementById('toxicity-explanation').textContent = result.explanation;

    const categoriesDiv = document.getElementById('categories');
    categoriesDiv.innerHTML = '';
    if (result.categories && result.categories.length > 0) {
        result.categories.forEach(cat => {
            const tag = document.createElement('span');
            tag.className = 'category-tag';
            tag.textContent = cat;
            categoriesDiv.appendChild(tag);
        });
    }

    document.getElementById('emotional-support').textContent = result.emotional_support;

    const emailCard = document.getElementById('email-card');
    if (result.email_sent && result.email_preview) {
        emailCard.style.display = 'block';
        document.getElementById('email-preview').innerHTML = result.email_preview;
    } else {
        emailCard.style.display = 'none';
    }
}

function showLoading(show) {
    document.getElementById('loading-overlay').style.display = show ? 'flex' : 'none';
}

function resetForm() {
    document.querySelector('.input-section').style.display = 'block';
    document.getElementById('results-section').style.display = 'none';
    document.getElementById('text-input').value = '';
    document.getElementById('parent-email').value = '';
    removeImage();
}

function handleImageUpload(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('image-preview');
            preview.src = e.target.result;
            document.getElementById('image-preview-container').style.display = 'block';
            uploadedImageBase64 = e.target.result.split(',')[1];
        }
        reader.readAsDataURL(file);
    }
}

function removeImage() {
    document.getElementById('image-preview-container').style.display = 'none';
    document.getElementById('image-preview').src = '#';
    document.getElementById('screenshot-upload').value = '';
    uploadedImageBase64 = null;
}
