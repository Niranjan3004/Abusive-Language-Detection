document.addEventListener('DOMContentLoaded', function() {
    const textInput = document.getElementById('textInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const charCount = document.getElementById('charCount');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultsSection = document.getElementById('resultsSection');
    const errorMessage = document.getElementById('errorMessage');
    const successResults = document.getElementById('successResults');

    // Update character count
    textInput.addEventListener('input', function() {
        charCount.textContent = this.value.length;
    });

    // Analyze button click
    analyzeBtn.addEventListener('click', analyzeText);

    // Allow Enter+Ctrl to submit
    textInput.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            analyzeText();
        }
    });

    async function analyzeText() {
        const text = textInput.value.trim();

        if (!text) {
            showError('Please enter some text to analyze.');
            return;
        }

        // Show loading state
        loadingSpinner.style.display = 'block';
        resultsSection.style.display = 'none';
        errorMessage.style.display = 'none';
        analyzeBtn.disabled = true;

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });

            const data = await response.json();

            if (!response.ok) {
                showError(data.error || 'Error analyzing text');
                return;
            }

            displayResults(data);
        } catch (error) {
            showError('Network error: ' + error.message);
        } finally {
            loadingSpinner.style.display = 'none';
            analyzeBtn.disabled = false;
        }
    }

    function displayResults(data) {
        // Update classification
        const label = data.label.charAt(0).toUpperCase() + data.label.slice(1);
        document.getElementById('label').textContent = label;
        document.getElementById('label').className = 'label-badge ' + data.label.replace(' ', '-').toLowerCase();

        // Update confidence
        const confidencePercent = (data.confidence * 100).toFixed(2);
        document.getElementById('confidence').textContent = confidencePercent + '%';

        // Update severity
        document.getElementById('severityLevel').textContent = data.severity;
        const severityIndex = { 'SAFE': 0, 'MILD': 1, 'SERIOUS': 2, 'SEVERE': 3 }[data.severity] || 0;
        document.getElementById('severityBar').style.width = ((severityIndex + 1) / 4 * 100) + '%';

        // Update probability bars
        const nonAbuseProb = (data.probabilities['non-abusive'] * 100).toFixed(1);
        const abuseProb = (data.probabilities['abusive'] * 100).toFixed(1);

        document.getElementById('probNonAbusive').style.width = nonAbuseProb + '%';
        document.getElementById('probNonAbuseValue').textContent = nonAbuseProb + '%';

        document.getElementById('probAbusive').style.width = abuseProb + '%';
        document.getElementById('probAbuseValue').textContent = abuseProb + '%';

        // Update severity probabilities
        const sevProbs = data.severity_probabilities;
        const severityLevels = ['SAFE', 'MILD', 'SERIOUS', 'SEVERE'];
        const sevIds = ['Safe', 'Mild', 'Serious', 'Severe'];

        for (let i = 0; i < severityLevels.length; i++) {
            const prob = (sevProbs[severityLevels[i]] * 100).toFixed(1);
            document.getElementById('prob' + sevIds[i]).style.width = prob + '%';
            document.getElementById('prob' + sevIds[i] + 'Value').textContent = prob + '%';
        }

        // Update analyzed text
        document.getElementById('analyzedText').textContent = data.text;

        // Show results
        successResults.style.display = 'block';
        resultsSection.style.display = 'block';
        errorMessage.style.display = 'none';
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        successResults.style.display = 'none';
        resultsSection.style.display = 'block';
    }
});
