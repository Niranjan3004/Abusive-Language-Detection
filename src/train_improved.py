"""
Improved Training Script for Abusive Language Detection
Uses enhanced model architecture and data preparation
"""

import os
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import ReduceLROnPlateau, CosineAnnealingWarmRestarts
from torch.utils.data import DataLoader
from tqdm import tqdm
import numpy as np
from dotenv import load_dotenv
import json
from pathlib import Path

# Import from local modules
try:
    from src.data import AbusiveLanguageDataset
    from src.model_improved import EnhancedAbusiveLanguageDetector, HybridAbusiveLanguageDetector
    from src.prepare_data import prepare_data
except ModuleNotFoundError:
    from data import AbusiveLanguageDataset
    from model_improved import EnhancedAbusiveLanguageDetector, HybridAbusiveLanguageDetector
    from prepare_data import prepare_data


class EarlyStopping:
    """Early stopping to prevent overfitting"""
    
    def __init__(self, patience=3, min_delta=0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_score = None
        self.best_epoch = 0
    
    def __call__(self, val_loss):
        if self.best_score is None:
            self.best_score = val_loss
        elif val_loss < self.best_score - self.min_delta:
            self.best_score = val_loss
            self.counter = 0
        else:
            self.counter += 1
        
        return self.counter >= self.patience


def calculate_metrics(predictions, labels, threshold=0.5):
    """Calculate precision, recall, F1 score"""
    pred_binary = (predictions >= threshold).astype(int)
    
    tp = ((pred_binary == 1) & (labels == 1)).sum()
    tn = ((pred_binary == 0) & (labels == 0)).sum()
    fp = ((pred_binary == 1) & (labels == 0)).sum()
    fn = ((pred_binary == 0) & (labels == 1)).sum()
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    accuracy = (tp + tn) / len(labels)
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
    }


def train_epoch(model, train_loader, optimizer, device, use_auxiliary=False):
    """Train for one epoch"""
    model.train()
    total_loss = 0
    all_predictions = []
    all_labels = []
    
    abuse_criterion = nn.CrossEntropyLoss()
    severity_criterion = nn.CrossEntropyLoss()
    auxiliary_criterion = nn.CrossEntropyLoss()
    
    progress_bar = tqdm(train_loader, desc='Training')
    
    for batch in progress_bar:
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['label'].to(device)
        severities = batch['severity'].to(device)
        
        optimizer.zero_grad()
        
        # Forward pass
        if use_auxiliary:
            abuse_logits, severity_logits, aux_logits, confidence = model(
                input_ids, attention_mask, return_aux=True
            )
        else:
            abuse_logits, severity_logits = model(input_ids, attention_mask)
        
        # Calculate losses
        abuse_loss = abuse_criterion(abuse_logits, labels)
        severity_loss = severity_criterion(severity_logits, severities)
        
        total_loss_batch = abuse_loss + 0.3 * severity_loss
        
        # Add auxiliary loss if available
        if use_auxiliary:
            aux_loss = auxiliary_criterion(aux_logits, labels)
            total_loss_batch += 0.1 * aux_loss
        
        total_loss_batch.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        
        total_loss += total_loss_batch.item()
        
        # Track predictions
        with torch.no_grad():
            probs = torch.softmax(abuse_logits, dim=1)[:, 1]
            all_predictions.extend(probs.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
        
        progress_bar.set_postfix({'loss': total_loss_batch.item()})
    
    # Calculate metrics
    metrics = calculate_metrics(np.array(all_predictions), np.array(all_labels))
    
    return total_loss / len(train_loader), metrics


def validate(model, val_loader, device):
    """Validate model"""
    model.eval()
    total_loss = 0
    all_predictions = []
    all_labels = []
    all_severities = []
    
    abuse_criterion = nn.CrossEntropyLoss()
    severity_criterion = nn.CrossEntropyLoss()
    
    with torch.no_grad():
        for batch in tqdm(val_loader, desc='Validating'):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)
            severities = batch['severity'].to(device)
            
            abuse_logits, severity_logits = model(input_ids, attention_mask)
            
            abuse_loss = abuse_criterion(abuse_logits, labels)
            severity_loss = severity_criterion(severity_logits, severities)
            total_loss += (abuse_loss + severity_loss).item()
            
            # Track predictions
            probs = torch.softmax(abuse_logits, dim=1)[:, 1]
            all_predictions.extend(probs.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
            sev_preds = torch.argmax(severity_logits, dim=1)
            all_severities.extend(sev_preds.cpu().numpy())
    
    # Calculate metrics
    metrics = calculate_metrics(np.array(all_predictions), np.array(all_labels))
    
    return total_loss / len(val_loader), metrics, np.array(all_severities)


def train_improved_model(
    train_dataset_path,
    test_dataset_path,
    output_dir='output',
    epochs=10,
    batch_size=16,
    learning_rate=2e-5,
    use_enhanced=True,
    use_auxiliary=False,
):
    """
    Improved training procedure
    
    Args:
        train_dataset_path: Path to training CSV
        test_dataset_path: Path to test CSV
        output_dir: Output directory for models
        epochs: Number of training epochs
        batch_size: Batch size
        learning_rate: Learning rate
        use_enhanced: Use enhanced model architecture
        use_auxiliary: Use auxiliary classifier for regularization
    """
    
    print("\n" + "="*70)
    print("IMPROVED ABUSIVE LANGUAGE DETECTION - TRAINING")
    print("="*70)
    
    # Setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\nDevice: {device}")
    print(f"Enhanced Model: {use_enhanced}")
    print(f"Auxiliary Loss: {use_auxiliary}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Load datasets
    print(f"\nLoading datasets...")
    train_dataset = AbusiveLanguageDataset(train_dataset_path)
    test_dataset = AbusiveLanguageDataset(test_dataset_path)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)
    
    print(f"Training samples: {len(train_dataset)}")
    print(f"Test samples: {len(test_dataset)}")
    
    # Initialize model
    print(f"\nInitializing model...")
    if use_enhanced:
        model = EnhancedAbusiveLanguageDetector().to(device)
    else:
        from src.model import AbusiveLanguageDetector
        model = AbusiveLanguageDetector().to(device)
    
    # Optimizer and scheduler
    optimizer = AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-5)
    scheduler = CosineAnnealingWarmRestarts(
        optimizer, T_0=3, T_mult=2, eta_min=1e-6
    )
    early_stopping = EarlyStopping(patience=4, min_delta=0.001)
    
    # Training loop
    best_val_loss = float('inf')
    best_f1 = 0
    
    print("\nStarting training...")
    print("="*70)
    
    for epoch in range(epochs):
        print(f"\nEpoch {epoch+1}/{epochs}")
        
        # Train
        train_loss, train_metrics = train_epoch(
            model, train_loader, optimizer, device, use_auxiliary
        )
        
        # Validate
        val_loss, val_metrics, severity_preds = validate(model, test_loader, device)
        
        # Update scheduler
        scheduler.step()
        
        # Print metrics
        print(f"Train Loss: {train_loss:.4f}")
        print(f"  Accuracy: {train_metrics['accuracy']:.4f}")
        print(f"  Precision: {train_metrics['precision']:.4f}")
        print(f"  Recall: {train_metrics['recall']:.4f}")
        print(f"  F1-Score: {train_metrics['f1']:.4f}")
        
        print(f"Val Loss: {val_loss:.4f}")
        print(f"  Accuracy: {val_metrics['accuracy']:.4f}")
        print(f"  Precision: {val_metrics['precision']:.4f}")
        print(f"  Recall: {val_metrics['recall']:.4f}")
        print(f"  F1-Score: {val_metrics['f1']:.4f}")
        
        # Save best model
        if val_metrics['f1'] > best_f1:
            best_f1 = val_metrics['f1']
            best_val_loss = val_loss
            
            checkpoint = {
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'scheduler_state_dict': scheduler.state_dict(),
                'train_metrics': train_metrics,
                'val_metrics': val_metrics,
                'val_loss': val_loss,
                'best_f1': best_f1,
            }
            
            model_path = os.path.join(output_dir, 'best_model_improved.pth')
            torch.save(checkpoint, model_path)
            print(f"✓ Saved best model with F1-Score: {best_f1:.4f}")
        
        # Early stopping check
        if early_stopping(val_loss):
            print(f"\n✓ Early stopping triggered after {epoch+1} epochs")
            break
    
    print("\n" + "="*70)
    print("TRAINING COMPLETE")
    print("="*70)
    print(f"Best F1-Score: {best_f1:.4f}")
    print(f"Best Validation Loss: {best_val_loss:.4f}")


def main():
    """Main training entry point"""
    
    # Load environment variables
    if not os.path.exists('.env'):
        print("Creating .env file with defaults...")
        with open('.env', 'w') as f:
            f.write("""TRAIN_DATASET=data/train.csv
TEST_DATASET=data/test.csv
EPOCHS=10
BATCH_SIZE=16
LEARNING_RATE=2e-5
""")
    
    load_dotenv()
    
    # First, prepare data if needed
    raw_csv = 'data/Suspicious Communication on Social Platforms.csv'
    if os.path.exists(raw_csv) and not os.path.exists('data/train.csv'):
        print("Preparing data from raw CSV...")
        prepare_data(raw_csv)
    
    # Load configuration
    TRAIN_DATASET = os.getenv('TRAIN_DATASET', 'data/train.csv')
    TEST_DATASET = os.getenv('TEST_DATASET', 'data/test.csv')
    EPOCHS = int(os.getenv('EPOCHS', 10))
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 16))
    LEARNING_RATE = float(os.getenv('LEARNING_RATE', 2e-5))
    
    print(f"\nConfiguration:")
    print(f"  Training dataset: {TRAIN_DATASET}")
    print(f"  Test dataset: {TEST_DATASET}")
    print(f"  Epochs: {EPOCHS}")
    print(f"  Batch size: {BATCH_SIZE}")
    print(f"  Learning rate: {LEARNING_RATE}")
    
    # Train improved model
    train_improved_model(
        TRAIN_DATASET,
        TEST_DATASET,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        learning_rate=LEARNING_RATE,
        use_enhanced=True,
        use_auxiliary=True,
    )


if __name__ == '__main__':
    main()
