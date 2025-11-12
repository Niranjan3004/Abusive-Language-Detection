# Quick Reference - Abusive Language Detection

## Start the App
```powershell
# Windows - Double-click or run:
run_app.bat

# Manual start:
python app.py

# Open browser:
http://localhost:5000
```

## Command Line Usage
```powershell
# Analyze single text
python evaluate.py --text "Your text here"

# Example:
python evaluate.py --text "That's awesome"
```

## API Usage (Python)
```python
import requests

url = "http://localhost:5000/predict"
data = {"text": "Your text here"}
response = requests.post(url, json=data)
result = response.json()
print(result)
```

## API Usage (PowerShell)
```powershell
$headers = @{"Content-Type" = "application/json"}
$body = @{"text" = "Your text"} | ConvertTo-Json
$response = Invoke-RestMethod -Uri "http://localhost:5000/predict" -Method POST -Headers $headers -Body $body
$response | ConvertTo-Json
```

## API Usage (cURL)
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"Your text here"}'
```

## Response Format
```json
{
  "text": "analyzed text",
  "label": "abusive" | "non-abusive",
  "confidence": 0.95,
  "probabilities": {
    "non-abusive": 0.05,
    "abusive": 0.95
  },
  "severity": "SEVERE" | "SERIOUS" | "MILD" | "SAFE",
  "severity_probabilities": {
    "SAFE": 0.01,
    "MILD": 0.04,
    "SERIOUS": 0.15,
    "SEVERE": 0.80
  }
}
```

## Setup Steps (First Time)
```powershell
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download BERT model (optional but recommended)
python download_model.py

# 4. Train model (if you have data)
python src/train.py

# 5. Run app
python app.py
```

## Project Structure
```
├── app.py                 # Flask web app
├── evaluate.py           # CLI tool
├── download_model.py     # Download BERT
├── run_app.bat          # Windows startup
├── requirements.txt      # Dependencies
├── data/
│   ├── train.csv        # Training data
│   └── test.csv         # Test data
├── models/
│   └── bert-base-uncased/
├── output/
│   └── best_model.pth   # Trained model
├── src/
│   ├── model.py
│   ├── data.py
│   └── train.py
├── templates/
│   └── index.html       # Web UI
└── static/
    ├── style.css        # Styles
    └── script.js        # Frontend logic
```

## Endpoints
| Method | URL | Purpose |
|--------|-----|---------|
| GET | `/` | Web interface |
| POST | `/predict` | Analyze text |
| GET | `/health` | Server status |

## Common Issues & Solutions

### Port 5000 in use?
Change in `app.py` last line:
```python
app.run(port=5001)  # Use different port
```

### Model not found?
```powershell
python download_model.py
# or
python src/train.py  # if you have training data
```

### Import errors?
```powershell
pip install -r requirements.txt --upgrade
```

### CUDA errors?
The app automatically uses CPU if GPU unavailable. Check startup message.

## File Links
- 📖 Full Setup Guide: `SETUP.md`
- 📝 Fixes Applied: `FIXES_APPLIED.md`
- 🔧 Original Readme: `README.md`

## Tips
- Use `Ctrl+C` to stop the server
- Save text to `data/` directory for batch processing
- GPU speeds up predictions (optional)
- Model loads once at startup for performance
- All computations run locally (offline compatible)

## Version Info
- Python: 3.7+
- PyTorch: 1.7+
- Flask: 2.0+
- BERT: base-uncased

---
Last Updated: November 12, 2025
