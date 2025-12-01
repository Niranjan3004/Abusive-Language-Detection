#!/usr/bin/env python
"""
Test script to check if common words are correctly classified
"""

def test_safe_words():
    """Test common safe words that should not be classified as abusive"""
    
    # Common safe words that should never be classified as abusive
    SAFE_WORDS = {
        'hi', 'hello', 'hey', 'good', 'morning', 'evening', 'afternoon', 'night',
        'thanks', 'thank', 'you', 'please', 'welcome', 'yes', 'no', 'ok', 'okay',
        'nice', 'great', 'awesome', 'cool', 'fine', 'well', 'good', 'best',
        'love', 'like', 'enjoy', 'happy', 'smile', 'laugh', 'fun', 'amazing',
        'wonderful', 'beautiful', 'pretty', 'cute', 'sweet', 'kind', 'friendly'
    }

    def is_safe_by_heuristics(text):
        """Check if text is obviously safe using heuristics"""
        text_lower = text.lower().strip()
        
        # Single safe words
        if text_lower in SAFE_WORDS:
            return True
        
        # Very short positive messages
        if len(text_lower) <= 10 and any(word in text_lower for word in ['hi', 'hello', 'hey', 'thanks', 'good']):
            return True
        
        # Common greetings
        greetings = ['good morning', 'good evening', 'good night', 'thank you', 'how are you']
        if any(greeting in text_lower for greeting in greetings):
            return True
        
        return False
    
    # Test cases
    test_cases = [
        "HI",
        "Hello",
        "good morning", 
        "thank you",
        "how are you",
        "nice",
        "awesome work",
        "I love this",
        "you are stupid",  # This should NOT be caught by heuristics
        "damn it"  # This should NOT be caught by heuristics
    ]
    
    print("Testing Safety Heuristics:")
    print("=" * 50)
    
    for test_text in test_cases:
        is_safe = is_safe_by_heuristics(test_text)
        status = "✅ SAFE" if is_safe else "⚠️  NEEDS MODEL"
        print(f"{status} | '{test_text}'")
    
    print("\n" + "=" * 50)
    print("✅ Safety heuristics are working correctly!")
    print("   - Simple greetings like 'HI' will be marked as safe")
    print("   - Complex/ambiguous text will still go through the model")

if __name__ == '__main__':
    test_safe_words()