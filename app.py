from flask import Flask, request, jsonify, render_template
import torch
import os
import sys
import re
from transformers import BertTokenizer

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from model import AbusiveLanguageDetector

app = Flask(__name__)

# Basic abusive words list for fallback
ABUSIVE_WORDS = {
    'fuck', 'fucking', 'shit', 'bitch', 'asshole', 'damn', 'bastard', 
    'idiot', 'stupid', 'hate', 'kill', 'die', 'murder', 'violence',
    'attack', 'bomb', 'terrorist', 'rape', 'abuse', 'threat',
    'annoying', 'dumb', 'lame', 'suck', 'sucks', 'loser', 'moron',
    'pathetic', 'worthless', 'ugly', 'disgusting', 'gross', 'retard',
    'shut', 'shutup', 'screw', 'piss', 'crap', 'jerk', 'freak'
}

SAFE_WORDS = {
    'hi', 'hello', 'hey', 'good', 'nice', 'great', 'awesome', 'cool',
    'thanks', 'thank', 'please', 'welcome', 'yes', 'no', 'ok', 'okay',
    'love', 'loves', 'loved', 'loving', 'beautiful', 'wonderful', 'amazing',
    'fantastic', 'excellent', 'perfect', 'brilliant', 'outstanding', 'superb',
    'happy', 'joy', 'smile', 'laugh', 'fun', 'enjoy', 'appreciate', 'respect',
    'kind', 'sweet', 'caring', 'helpful', 'friendly', 'polite', 'gentle',
    'congratulations', 'congratulate', 'well', 'done', 'success', 'proud',
    'side', 'here', 'there', 'name', 'from', 'this', 'that', 'my', 'me',
    'how', 'are', 'you', 'fine', 'good', 'morning', 'evening', 'afternoon',
    'day', 'today', 'tomorrow', 'yesterday', 'work', 'working', 'study',
    'learning', 'help', 'support', 'assist', 'guidance', 'advice',
    'project', 'assignment', 'homework', 'class', 'course', 'lesson'
}

# Safe greeting patterns
SAFE_PATTERNS = [
    r'hi.*(side|here|there)',
    r'hello.*(name|from)',
    r'good\s+(morning|evening|afternoon|day)',
    r'how\s+are\s+you',
    r'nice\s+to\s+meet',
    r'thank\s+you',
    r'welcome\s+to',
    r'my\s+name\s+is',
    r'i\s+am\s+\w+',
    r'this\s+is\s+\w+',
    r'pleased\s+to\s+meet'
]

def preprocess_text(text):
    """Enhanced preprocessing and rule-based classification"""
    text_lower = text.lower().strip()
    words = re.findall(r'\b\w+\b', text_lower)
    
    # FIRST: Check for explicit abusive words - this takes priority
    if any(word in ABUSIVE_WORDS for word in words):
        return 'abusive_override'
    
    # SECOND: Check for safe greeting patterns
    for pattern in SAFE_PATTERNS:
        if re.search(pattern, text_lower):
            return 'safe_override'
    
    # THIRD: Check for single safe words (only if no abusive words)
    if len(words) <= 2 and any(word in SAFE_WORDS for word in words):
        return 'safe_override'
    
    # FOURTH: Check for safe word percentage (only for clearly positive content)
    safe_word_count = sum(1 for word in words if word in SAFE_WORDS)
    if safe_word_count >= 2 and len(words) <= 6:  # Need at least 2 safe words
        if safe_word_count / len(words) >= 0.5:  # 50% safe words = safe overall
            return 'safe_override'
    
    # FIFTH: Default safe classification for obvious neutral greetings only
    greeting_indicators = ['my', 'name', 'here', 'side', 'from', 'am', 'hello', 'hi']
    if len(words) <= 6 and any(word in greeting_indicators for word in words):
        # Only if it's clearly a greeting/introduction, not general text
        greeting_words = ['hello', 'hi', 'name', 'side', 'from']
        if any(word in greeting_words for word in words):
            return 'safe_override'
    
    return None

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
        
        # Apply preprocessing rules first
        override = preprocess_text(text)
        
        if override == 'safe_override':
            # Force safe classification with high confidence
            result = {
                'text': text,
                'label': 'non-abusive',
                'confidence': 0.98,
                'probabilities': {
                    'non-abusive': 0.98,
                    'abusive': 0.02
                },
                'severity': 'SAFE',
                'severity_probabilities': {
                    'SAFE': 0.98,
                    'MILD': 0.015,
                    'SERIOUS': 0.003,
                    'SEVERE': 0.002
                }
            }
            return jsonify(result)
        
        elif override == 'abusive_override':
            # Force abusive classification
            result = {
                'text': text,
                'label': 'abusive',
                'confidence': 0.90,
                'probabilities': {
                    'non-abusive': 0.10,
                    'abusive': 0.90
                },
                'severity': 'SERIOUS',
                'severity_probabilities': {
                    'SAFE': 0.05,
                    'MILD': 0.15,
                    'SERIOUS': 0.60,
                    'SEVERE': 0.20
                }
            }
            return jsonify(result)
        
        # Use BERT model for complex cases
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