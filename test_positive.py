#!/usr/bin/env python
"""
Test the fix for "loves" and other positive words
"""
import re

# Updated safe words list (same as in app.py)
SAFE_WORDS = {
    'hi', 'hello', 'hey', 'good', 'nice', 'great', 'awesome', 'cool',
    'thanks', 'thank', 'please', 'welcome', 'yes', 'no', 'ok', 'okay',
    'love', 'loves', 'loved', 'loving', 'beautiful', 'wonderful', 'amazing',
    'fantastic', 'excellent', 'perfect', 'brilliant', 'outstanding', 'superb',
    'happy', 'joy', 'smile', 'laugh', 'fun', 'enjoy', 'appreciate', 'respect',
    'kind', 'sweet', 'caring', 'helpful', 'friendly', 'polite', 'gentle',
    'congratulations', 'congratulate', 'well', 'done', 'success', 'proud'
}

def preprocess_text(text):
    """Test the preprocessing function"""
    text_lower = text.lower().strip()
    words = re.findall(r'\b\w+\b', text_lower)
    
    # Check for explicit safe words
    if len(words) <= 2 and any(word in SAFE_WORDS for word in words):
        return 'safe_override'
    
    return None

def test_positive_words():
    """Test positive words that should be NON-ABUSIVE"""
    test_cases = [
        "Loves",
        "Love",
        "I love this",
        "Beautiful",
        "Amazing work",
        "Wonderful",
        "Excellent",
        "Perfect",
        "Happy",
        "Thank you",
        "Congratulations"
    ]
    
    print("🧪 Testing Positive Words Fix")
    print("=" * 40)
    
    for text in test_cases:
        result = preprocess_text(text)
        print(f"'{text}' → {result}")
        
        if result == 'safe_override':
            print("✅ WILL BE NON-ABUSIVE")
        else:
            print("⚠️ Will use BERT (might be wrong)")
        print("-" * 20)

if __name__ == '__main__':
    test_positive_words()