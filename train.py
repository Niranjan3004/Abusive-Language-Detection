#!/usr/bin/env python
"""
Main entry point for training the improved model
Run this from the project root directory: python train.py
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Now run the training
if __name__ == '__main__':
    from train_improved import main
    main()
