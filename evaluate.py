import os
import torch
import argparse

# Force transformers / huggingface to operate in offline mode when possible.
# This prevents attempts to reach out to huggingface.co when there's no network
# (avoids NameResolutionError seen when DNS/network is unavailable).
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_HUB_OFFLINE", "1")

from transformers import BertTokenizer
from src.model import AbusiveLanguageDetector

def load_model(model_path):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = AbusiveLanguageDetector().to(device)
    
    try:
        if os.path.exists(model_path):
            checkpoint = torch.load(model_path, map_location=device)
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                model.load_state_dict(checkpoint['model_state_dict'])
            else:
                model.load_state_dict(checkpoint)
            print(f"Loaded model from {model_path}")
        else:
            print(f"Warning: Model file {model_path} not found. Using initialized model.")
    except Exception as e:
        print(f"Warning: Error loading model - {str(e)}")
        print("Using initialized model.")
    
    model.eval()
    return model, device

def get_severity_level(severity_probs):
    severity_idx = torch.argmax(severity_probs).item()
    severity_conf = torch.softmax(severity_probs, dim=0)[severity_idx].item()
    
    severity_levels = {
        0: ("SAFE", "Content appears to be safe"),
        1: ("MILD", "Mildly abusive content detected (e.g., mild insults)"),
        2: ("SERIOUS", "Seriously abusive content detected (e.g., severe insults, threats)"),
        3: ("SEVERE", "Extremely abusive content detected (e.g., profanity, extreme hate speech)")
    }
    
    return severity_levels[severity_idx][0], severity_levels[severity_idx][1], severity_conf

def predict_text(text, model, tokenizer, device):
    # Tokenize the input text
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
    
    input_ids = encoding['input_ids'].to(device)
    attention_mask = encoding['attention_mask'].to(device)
    
    with torch.no_grad():
        abuse_logits, severity_logits = model(input_ids, attention_mask)
        abuse_probs = torch.softmax(abuse_logits, dim=1)
        severity_probs = torch.softmax(severity_logits, dim=1)
        
        confidence, predicted = torch.max(abuse_probs, dim=1)
        
    severity_level, severity_message, severity_conf = get_severity_level(severity_logits[0])
        
    return {
        'label': 'abusive' if predicted.item() == 1 else 'non-abusive',
        'confidence': confidence.item(),
        'probabilities': {
            'non-abusive': abuse_probs[0][0].item(),
            'abusive': abuse_probs[0][1].item()
        },
        'severity_level': severity_level,
        'severity_message': severity_message,
        'severity_confidence': severity_conf * 100
    }

def main():
    parser = argparse.ArgumentParser(description='Detect abusive language in text')
    parser.add_argument('--model', default='output/best_model.pth', help='Path to the trained model')
    parser.add_argument('--text', required=True, help='Text to analyze')
    args = parser.parse_args()
    
    # Load model and tokenizer
    model, device = load_model(args.model)
    
    # Try to load tokenizer from local paths first
    try:
        # Try local cache first
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', local_files_only=True)
    except Exception as e1:
        try:
            # Try models directory next
            tokenizer = BertTokenizer.from_pretrained('models/bert-base-uncased', local_files_only=True)
        except Exception as e2:
            print("Error: Could not load tokenizer in offline mode.")
            print("Please ensure you have downloaded the model first by:")
            print("1. Having an internet connection and running once, or")
            print("2. Manually downloading bert-base-uncased to models/bert-base-uncased")
            raise RuntimeError("Failed to load tokenizer") from e2
    
    # Make prediction
    result = predict_text(args.text, model, tokenizer, device)
    
    # Print results
    print("\nAnalysis Results:")
    print(f"Text: {args.text}")
    print(f"\nSeverity Level: {result['severity_level']}")
    print(f"Warning: {result['severity_message']}")
    print(f"\nClassification: {result['label']}")
    print(f"Confidence: {result['confidence']*100:.2f}%")
    print("\nDetailed Analysis:")
    print(f"Non-abusive probability: {result['probabilities']['non-abusive']*100:.2f}%")
    print(f"Abusive probability: {result['probabilities']['abusive']*100:.2f}%")
    
    if result['probabilities']['abusive'] > 0.3:
        print("\nCAUTION: This text contains potentially harmful content.")

if __name__ == '__main__':
    main()