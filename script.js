document.getElementById('analyze-btn').addEventListener('click', handleAnalyze);

// Simulated Gemini API call with keyword analysis
function analyzeTextWithGemini(text) {
    const keywordSets = [
        { level: 80, keywords: ['kill', 'hate', 'die', 'murder'], categories: ['threats', 'hate speech'] },
        { level: 60, keywords: ['stupid', 'idiot', 'dumb', 'loser'], categories: ['bullying', 'harassment'] },
        { level: 40, keywords: ['ugly', 'fat', 'smelly'], categories: ['body shaming', 'verbal abuse'] },
        { level: 20, keywords: ['bad', 'sad', 'cry'], categories: ['unkind'] }
    ];

    let score = 0;
    let categories = new Set();
    const lowerCaseText = text.toLowerCase();

    for (const set of keywordSets) {
        for (const keyword of set.keywords) {
            if (lowerCaseText.includes(keyword)) {
                score = Math.max(score, set.level);
                set.categories.forEach(cat => categories.add(cat));
            }
        }
    }

    let analysis = "This message seems okay.";
    if (score >= 80) {
        analysis = "This message is highly toxic and contains threats or hate speech.";
    } else if (score >= 60) {
        analysis = "This message is moderately toxic and contains bullying or harassment.";
    } else if (score >= 40) {
        analysis = "This message has some toxic elements, like body shaming or verbal abuse.";
    } else if (score >= 20) {
        analysis = "This message has some unkind elements.";
    }

    return {
        "toxicity_score": `${score}%`,
        "analysis": analysis,
        "categories": Array.from(categories)
    };
}

function handleAnalyze() {
    const text = document.getElementById('text-input').value;
    const parentEmail = document.getElementById('parent-email').value;

    const geminiResult = analyzeTextWithGemini(text);
    const toxicity = parseInt(geminiResult.toxicity_score);

    let emotionalSupport = "";
    if (toxicity >= 20) {
        emotionalSupport = "It's okay to feel upset or hurt by messages like this. Remember to be kind to yourself and take a break if you need to. You can always talk to a trusted adult about how you're feeling.";
    }

    let emailSent = "no";
    let emailPreview = "";
    if (toxicity >= 40 && parentEmail) {
        emailSent = "yes";
        emailPreview = `
            <p><strong>To:</strong> ${parentEmail}</p>
            <p><strong>Subject:</strong> Cyberbullying Alert — Emotional Support Recommended</p>
            <p>Hi,</p>
            <p>This is an alert from KindNest. A message with potentially harmful content has been detected. The message contained elements of ${geminiResult.categories.join(', ')}.</p>
            <p>This kind of message can be very upsetting and may cause feelings of sadness, anxiety, or fear. We recommend checking in with your child and offering them your support.</p>
            <p>The goal is to provide comfort and safety, not to punish or blame. A calm and supportive conversation can make a big difference.</p>
            <p>Best,</p>
            <p>The KindNest Team</p>
        `;
        // In a real application, you would call the sendEmail tool here.
        sendEmail({ to: parentEmail, subject: "Cyberbullying Alert — Emotional Support Recommended", body: emailPreview });
    }

    const result = {
        "toxicity_score": geminiResult.toxicity_score,
        "analysis": geminiResult.analysis,
        "emotional_support": emotionalSupport,
        "email_sent": emailSent,
        "email_preview": emailPreview
    };

    updateUI(result);
}

function updateUI(result) {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = `
        <p><strong>Toxicity Score:</strong> ${result.toxicity_score}</p>
        <p><strong>Analysis:</strong> ${result.analysis}</p>
        <p><strong>Emotional Support:</strong> ${result.emotional_support}</p>
        <p><strong>Email Sent:</strong> ${result.email_sent}</p>
    `;

    const emailPreviewContainer = document.getElementById('email-preview-container');
    const emailPreviewDiv = document.getElementById('email-preview');
    if (result.email_sent === "yes") {
        emailPreviewDiv.innerHTML = result.email_preview;
        emailPreviewContainer.style.display = 'block';
    } else {
        emailPreviewContainer.style.display = 'none';
    }
}

function sendEmail(email) {
    console.log("Sending email:", email);
}
