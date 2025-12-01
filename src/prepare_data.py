"""
Data Preparation Script for Abusive Language Detection
Converts raw data to required format and creates training datasets
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from sklearn.model_selection import train_test_split
from collections import Counter
import re


def load_raw_data(csv_path):
    """Load raw CSV data"""
    print(f"Loading data from: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} samples")
    print(f"Columns: {df.columns.tolist()}")
    return df


def map_columns(df, text_col='comments', label_col='tagging'):
    """Map raw CSV columns to expected format"""
    df_mapped = pd.DataFrame()
    df_mapped['text'] = df[text_col].astype(str).str.strip()
    df_mapped['label'] = df[label_col].astype(int)
    return df_mapped


def assign_severity(df):
    """
    Assign severity levels based on text characteristics and label
    Severity: 0=safe, 1=mild, 2=serious, 3=severe
    """
    
    def calculate_severity(row):
        if row['label'] == 0:
            return 0  # Non-abusive = Safe
        
        text = str(row['text']).lower()
        
        # Severe indicators
        severe_patterns = [
            r'fuck', r'shit', r'bitch', r'cunt', r'motherfucker',
            r'kill.*yourself', r'die', r'rape', r'murder'
        ]
        if any(re.search(pattern, text) for pattern in severe_patterns):
            return 3
        
        # Serious indicators
        serious_patterns = [
            r'hate', r'stupid', r'idiot', r'dumb', r'loser',
            r'pussy', r'dick', r'faggot', r'slut'
        ]
        if any(re.search(pattern, text) for pattern in serious_patterns):
            return 2
        
        # Mild indicators
        mild_patterns = [
            r'sucks', r'crap', r'bloody', r'gross', r'weird'
        ]
        if any(re.search(pattern, text) for pattern in mild_patterns):
            return 1
        
        # Default for labeled abusive
        return 1
    
    df['severity'] = df.apply(calculate_severity, axis=1)
    return df


def clean_text(text):
    """Clean text for better model training"""
    text = str(text).strip()
    # Keep most special characters for context
    # but remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    return text


def balance_dataset(df, random_state=42):
    """Balance dataset to address class imbalance"""
    abusive = df[df['label'] == 1]
    non_abusive = df[df['label'] == 0]
    
    print(f"\nClass distribution BEFORE balancing:")
    print(f"  Abusive: {len(abusive)} ({len(abusive)/len(df)*100:.1f}%)")
    print(f"  Non-abusive: {len(non_abusive)} ({len(non_abusive)/len(df)*100:.1f}%)")
    
    # Use stratified approach - balance to 1:1 ratio (most efficient)
    # Keep all abusive samples and downsample non-abusive to match
    if len(abusive) < len(non_abusive):
        # More non-abusive than abusive: downsample non-abusive to 1:1
        non_abusive_sampled = non_abusive.sample(n=len(abusive), random_state=random_state)
        df_balanced = pd.concat([abusive, non_abusive_sampled], ignore_index=True)
    else:
        # More abusive than non-abusive: downsample abusive to 1:1
        abusive_sampled = abusive.sample(n=len(non_abusive), random_state=random_state)
        df_balanced = pd.concat([abusive_sampled, non_abusive], ignore_index=True)
    
    # Shuffle
    df_balanced = df_balanced.sample(frac=1, random_state=random_state).reset_index(drop=True)
    
    print(f"\nClass distribution AFTER balancing:")
    print(f"  Abusive: {len(df_balanced[df_balanced['label']==1])} ({len(df_balanced[df_balanced['label']==1])/len(df_balanced)*100:.1f}%)")
    print(f"  Non-abusive: {len(df_balanced[df_balanced['label']==0])} ({len(df_balanced[df_balanced['label']==0])/len(df_balanced)*100:.1f}%)")
    
    return df_balanced


def analyze_data_quality(df):
    """Analyze and print data quality metrics"""
    print("\n" + "="*60)
    print("DATA QUALITY ANALYSIS")
    print("="*60)
    
    print(f"\nDataset Size: {len(df)} samples")
    print(f"\nLabel Distribution:")
    print(df['label'].value_counts())
    
    print(f"\nSeverity Distribution:")
    print(df['severity'].value_counts().sort_index())
    
    # Text length analysis
    df['text_length'] = df['text'].str.len()
    df['word_count'] = df['text'].str.split().str.len()
    
    print(f"\nText Length Statistics:")
    print(f"  Mean: {df['text_length'].mean():.1f} characters")
    print(f"  Median: {df['text_length'].median():.1f} characters")
    print(f"  Min: {df['text_length'].min()} characters")
    print(f"  Max: {df['text_length'].max()} characters")
    
    print(f"\nWord Count Statistics:")
    print(f"  Mean: {df['word_count'].mean():.1f} words")
    print(f"  Median: {df['word_count'].median():.1f} words")
    print(f"  Min: {df['word_count'].min()} words")
    print(f"  Max: {df['word_count'].max()} words")
    
    # Missing values
    print(f"\nMissing Values:")
    print(f"  Text: {df['text'].isna().sum()}")
    print(f"  Label: {df['label'].isna().sum()}")
    print(f"  Severity: {df['severity'].isna().sum()}")
    
    return df


def extract_abusive_tokens(df):
    """Extract common tokens from abusive texts for dictionary building"""
    abusive_texts = df[df['label'] == 1]['text'].tolist()
    non_abusive_texts = df[df['label'] == 0]['text'].tolist()
    
    # Tokenize and count
    abusive_tokens = Counter()
    non_abusive_tokens = Counter()
    
    for text in abusive_texts:
        tokens = re.findall(r'\b\w+\b', text.lower())
        abusive_tokens.update(tokens)
    
    for text in non_abusive_texts:
        tokens = re.findall(r'\b\w+\b', text.lower())
        non_abusive_tokens.update(tokens)
    
    # Find tokens more common in abusive text
    abusive_specific = {}
    for token, count in abusive_tokens.most_common(500):
        if len(token) > 2:  # Skip short tokens
            abusive_freq = count / len(abusive_texts)
            non_abusive_freq = non_abusive_tokens.get(token, 0) / len(non_abusive_texts) if len(non_abusive_texts) > 0 else 0
            
            if abusive_freq > non_abusive_freq and abusive_freq > 0.01:
                ratio = abusive_freq / (non_abusive_freq + 1e-10)
                abusive_specific[token] = {
                    'frequency': count,
                    'abusive_ratio': count / max(1, count + non_abusive_tokens.get(token, 0)),
                    'ratio': ratio
                }
    
    return abusive_specific


def save_processed_data(df, output_dir):
    """Save processed data in required format"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Split data
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['label'])
    
    print(f"\n" + "="*60)
    print("DATASET SPLIT")
    print("="*60)
    print(f"Training samples: {len(train_df)}")
    print(f"Test samples: {len(test_df)}")
    
    # Save as CSV
    train_path = output_dir / 'train.csv'
    test_path = output_dir / 'test.csv'
    
    train_df[['text', 'label', 'severity']].to_csv(train_path, index=False)
    test_df[['text', 'label', 'severity']].to_csv(test_path, index=False)
    
    print(f"\n✓ Saved training data: {train_path}")
    print(f"✓ Saved test data: {test_path}")
    
    return train_path, test_path


def prepare_data(input_csv, output_dir='data', random_state=42):
    """
    Main data preparation pipeline
    """
    print("\n" + "="*60)
    print("ABUSIVE LANGUAGE DETECTION - DATA PREPARATION")
    print("="*60)
    
    # Load
    df = load_raw_data(input_csv)
    
    # Map columns
    df = map_columns(df)
    
    # Clean text
    df['text'] = df['text'].apply(clean_text)
    
    # Assign severity
    df = assign_severity(df)
    
    # Analyze quality
    df = analyze_data_quality(df)
    
    # Balance
    df = balance_dataset(df, random_state=random_state)
    
    # Save
    train_path, test_path = save_processed_data(df, output_dir)
    
    # Extract tokens for token database
    print(f"\n" + "="*60)
    print("EXTRACTING ABUSIVE TOKENS")
    print("="*60)
    tokens = extract_abusive_tokens(df)
    
    # Save tokens
    tokens_path = Path(output_dir) / 'abusive_tokens.json'
    with open(tokens_path, 'w') as f:
        json.dump(tokens, f, indent=2)
    print(f"✓ Extracted and saved {len(tokens)} abusive tokens: {tokens_path}")
    
    print("\n" + "="*60)
    print("DATA PREPARATION COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("  1. python src/train.py")
    print("\nYour data is ready!")
    
    return train_path, test_path, tokens_path


if __name__ == '__main__':
    # Prepare your data
    input_file = 'data/Suspicious Communication on Social Platforms.csv'
    prepare_data(input_file)
