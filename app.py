from flask import Flask, request, jsonify, render_template
import torch
import os
import sys
from transformers import BertTokenizer

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from model import AbusiveLanguageDetector

app = Flask(__name__)

# Load model and tokenizer globally
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = AbusiveLanguageDetector().to(device)

# Load model checkpoint
try:
    checkpoint = torch.load('output/best_model.pth', map_location=device, weights_only=False)
    if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
        model.load_state_dict(checkpoint['model_state_dict'])
    else:
        model.load_state_dict(checkpoint)
    print("✓ Model loaded successfully")
except Exception as e:
    print(f"⚠ Warning: Could not load model - {e}")
    print("Model will use initialized weights")

model.eval()

# Load tokenizer
try:
    try:
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', local_files_only=True)
    except:
        tokenizer = BertTokenizer.from_pretrained('models/bert-base-uncased', local_files_only=True)
    print("✓ Tokenizer loaded successfully")
except Exception as e:
    print(f"⚠ Warning: Could not load tokenizer - {e}")
    raise RuntimeError("Failed to load tokenizer")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
            
        text = data['text']
        
        # Tokenize
        encoding = tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=128,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        # Make prediction
        with torch.no_grad():
            input_ids = encoding['input_ids'].to(device)
            attention_mask = encoding['attention_mask'].to(device)
            abuse_logits, severity_logits = model(input_ids, attention_mask)
            
            abuse_probs = torch.softmax(abuse_logits, dim=1)
            severity_probs = torch.softmax(severity_logits, dim=1)
            
            confidence, predicted = torch.max(abuse_probs, dim=1)
            severity_idx = torch.argmax(severity_probs, dim=1)
        
        severity_levels = {
            0: "SAFE",
            1: "MILD",
            2: "SERIOUS",
            3: "SEVERE"
        }
        
        result = {
            'text': text,
            'label': 'abusive' if predicted.item() == 1 else 'non-abusive',
            'confidence': float(confidence.item()),
            'probabilities': {
                'non-abusive': float(abuse_probs[0][0].item()),
                'abusive': float(abuse_probs[0][1].item())
            },
            'severity': severity_levels[severity_idx.item()],
            'severity_probabilities': {
                'SAFE': float(severity_probs[0][0].item()),
                'MILD': float(severity_probs[0][1].item()),
                'SERIOUS': float(severity_probs[0][2].item()),
                'SEVERE': float(severity_probs[0][3].item())
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'device': str(device)})

if __name__ == '__main__':
    print(f"\n✓ Server starting on http://localhost:5000")
    print(f"✓ Device: {device}")
    print(f"✓ Press Ctrl+C to stop the server\n")
    app.run(host='0.0.0.0', port=5000, debug=False)