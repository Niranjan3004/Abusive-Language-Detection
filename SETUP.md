# Abusive Language Detection - Setup & Run Guide

## Quick Start

### Option 1: Using the Batch Script (Windows - Easiest)
1. Double-click `run_app.bat` to start the application
2. Open your browser to `http://localhost:5000`

### Option 2: Manual Setup

#### Step 1: Create Virtual Environment
```powershell
python -m venv venv
venv\Scripts\activate
```

#### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

#### Step 3: Download Model (Recommended)
```powershell
python download_model.py
```
This downloads BERT locally so you can use the app offline.

#### Step 4: Prepare Dataset (For Training)
Your dataset CSV files need these columns: `text`, `label` (0/1), `severity` (0-3)

Example:
```
text,label,severity
"This is offensive",1,2
"Nice day today",0,0
```

Place files at:
- `data/train.csv` - Training data
- `data/test.csv` - Test data

#### Step 5: Train the Model
```powershell
python src/train.py
```
Best model saves to `output/best_model.pth`

#### Step 6: Run the Web Application
```powershell
python app.py
```
Then open: `http://localhost:5000`

---

## Using the Application

### Web Interface
1. Go to `http://localhost:5000` in your browser
2. Paste or type text to analyze
3. Click "Analyze Text"
4. View results with confidence scores and severity levels

### Command Line
```powershell
python evaluate.py --text "Your text here"
```

Example:
```powershell
python evaluate.py --text "That was terrible"
```

### API Endpoint
```powershell
# Using PowerShell
$headers = @{"Content-Type" = "application/json"}
$body = @{"text" = "Check this text"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5000/predict" -Method POST -Headers $headers -Body $body
```

---

## Troubleshooting

### Error: "Parent directory output does not exist"
```powershell
mkdir output
```

### Error: "BERT model not found"
```powershell
python download_model.py
```

### Error: "torch.load with weights_only"
The app automatically handles this. Just ensure you have the latest PyTorch:
```powershell
pip install --upgrade torch
```

### Port 5000 Already in Use
Edit `app.py` line at bottom:
```python
app.run(host='0.0.0.0', port=5001)  # Change 5000 to 5001
```

### Model Not Training Properly
Ensure your CSV has correct columns:
```python
# Correct format
text,label,severity
"example text",0,1
```

---

## Project Structure
```
Abusive-Language-Detection/
├── app.py                    # Flask web app
├── evaluate.py              # CLI evaluation tool
├── download_model.py        # Download BERT model
├── requirements.txt         # Python dependencies
├── run_app.bat             # Windows startup script
├── data/
│   ├── train.csv          # Training dataset
│   └── test.csv           # Test dataset
├── models/
│   └── bert-base-uncased/ # Downloaded BERT model
├── output/
│   └── best_model.pth     # Trained model
├── src/
│   ├── model.py           # Model architecture
│   ├── data.py            # Data preprocessing
│   └── train.py           # Training script
├── templates/
│   └── index.html         # Web interface
└── static/
    ├── style.css          # CSS styles
    └── script.js          # JavaScript logic
```

---

## Features

✅ BERT-based abusive language detection
✅ Multi-level severity classification (Safe, Mild, Serious, Severe)
✅ Web interface with real-time predictions
✅ REST API for integration
✅ Command-line tool for batch processing
✅ Offline model support
✅ GPU acceleration support
✅ Confidence scores with probability distribution

---

## System Requirements

- Python 3.7+
- 4GB RAM minimum
- CUDA capable GPU (optional, CPU works fine)
- Internet (first run to download BERT)

---

## Key Files Modified

1. **app.py** - Fixed model loading and added web interface routes
2. **evaluate.py** - Suppressed torch.load warnings
3. **templates/index.html** - New web interface
4. **static/style.css** - Professional UI styling
5. **static/script.js** - Frontend logic
6. **run_app.bat** - Windows startup script
7. **SETUP.md** - This file

---

## Support

For issues:
1. Check error messages carefully
2. Ensure all dependencies are installed: `pip install -r requirements.txt`
3. Try creating a fresh virtual environment
4. Check that model files exist in `output/` and `models/`

---

Generated: November 12, 2025
