#!/usr/bin/env python
"""
Main entry point for data preparation
Run this from the project root directory: python prepare_data.py
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Now run the data preparation
if __name__ == '__main__':
    from prepare_data import prepare_data
    
    csv_path = 'data/Suspicious Communication on Social Platforms.csv'
    prepare_data(csv_path)
