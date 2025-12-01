#!/usr/bin/env python
"""
Quick test to demonstrate the fixed predictions
"""
import requests
import json
import sys
import os
import time
import threading
from subprocess import Popen, PIPE

def test_predictions():
    """Test the fixed prediction API"""
    
    test_cases = [
        ("Hi", "Should be NON-ABUSIVE"),
        ("Hello there", "Should be NON-ABUSIVE"), 
        ("Fuck you", "Should be ABUSIVE"),
        ("You are stupid", "Should be ABUSIVE"),
        ("Thank you", "Should be NON-ABUSIVE"),
        ("Go kill yourself", "Should be ABUSIVE")
    ]
    
    print("🧪 Testing Fixed Abusive Language Detection\n")
    print("=" * 60)
    
    for text, expected in test_cases:
        try:
            response = requests.post('http://localhost:5000/predict', 
                                   json={'text': text}, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                label = result['label']
                confidence = result['confidence']
                severity = result['severity']
                
                print(f"Text: '{text}'")
                print(f"Expected: {expected}")
                print(f"Result: {label.upper()} ({confidence:.2f} confidence)")
                print(f"Severity: {severity}")
                
                # Check if prediction matches expectation
                if ("NON-ABUSIVE" in expected and label == "non-abusive") or \
                   ("ABUSIVE" in expected and label == "abusive"):
                    print("✅ CORRECT")
                else:
                    print("❌ INCORRECT")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing '{text}': {str(e)}")
            
        print("-" * 40)

if __name__ == '__main__':
    print("Starting Flask app in background...")
    
    # Start Flask app
    app_process = Popen([sys.executable, 'app.py'], 
                       stdout=PIPE, stderr=PIPE, cwd=os.getcwd())
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test if server is running
        test_response = requests.get('http://localhost:5000/health', timeout=5)
        if test_response.status_code == 200:
            print("✅ Flask app started successfully\n")
            test_predictions()
        else:
            print("❌ Flask app not responding")
            
    except Exception as e:
        print(f"❌ Could not connect to Flask app: {e}")
        
    finally:
        # Clean up
        try:
            app_process.terminate()
            app_process.wait(timeout=5)
        except:
            app_process.kill()
        print("\n🔚 Test completed")