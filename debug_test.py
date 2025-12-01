#!/usr/bin/env python
"""
Debug test to check if the preprocessing function works correctly
"""
import re

# Same lists and function from app.py
ABUSIVE_WORDS = {
    'fuck', 'fucking', 'shit', 'bitch', 'asshole', 'damn', 'bastard', 
    'idiot', 'stupid', 'hate', 'kill', 'die', 'murder', 'violence',
    'attack', 'bomb', 'terrorist', 'rape', 'abuse', 'threat'
}

SAFE_WORDS = {
    'hi', 'hello', 'hey', 'good', 'nice', 'great', 'awesome', 'cool',
    'thanks', 'thank', 'please', 'welcome', 'yes', 'no', 'ok', 'okay'
}

def preprocess_text(text):
    """Basic preprocessing and rule-based classification"""
    text_lower = text.lower().strip()
    words = re.findall(r'\b\w+\b', text_lower)
    
    print(f"Debug - Input: '{text}'")
    print(f"Debug - Lowercase: '{text_lower}'")
    print(f"Debug - Words: {words}")
    print(f"Debug - Words count: {len(words)}")
    
    # Check for explicit safe words
    safe_matches = [word for word in words if word in SAFE_WORDS]
    if len(words) <= 2 and safe_matches:
        print(f"Debug - Found safe words: {safe_matches}")
        return 'safe_override'
    
    # Check for explicit abusive words
    abusive_matches = [word for word in words if word in ABUSIVE_WORDS]
    if abusive_matches:
        print(f"Debug - Found abusive words: {abusive_matches}")
        return 'abusive_override'
    
    print("Debug - No override, using BERT model")
    return None

def test_cases():
    """Test the preprocessing function"""
    test_texts = [
        "Hi",
        "Hello",
        "Fuck",
        "You are stupid",
        "Thank you",
        "Hi there how are you"
    ]
    
    print("=" * 50)
    print("TESTING PREPROCESSING FUNCTION")
    print("=" * 50)
    
    for text in test_texts:
        print(f"\nTesting: '{text}'")
        result = preprocess_text(text)
        print(f"Result: {result}")
        
        if result == 'safe_override':
            print("✅ WILL BE CLASSIFIED AS NON-ABUSIVE")
        elif result == 'abusive_override':
            print("✅ WILL BE CLASSIFIED AS ABUSIVE")
        else:
            print("⚠️ WILL USE BERT MODEL (might be wrong)")
        print("-" * 30)

if __name__ == '__main__':
    test_cases()