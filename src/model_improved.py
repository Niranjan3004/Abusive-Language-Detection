"""
Improved Abusive Language Detection Model
Enhanced architecture with attention mechanisms and better feature extraction
"""

import torch
from torch import nn
from transformers import BertModel, BertTokenizer


class EnhancedAbusiveLanguageDetector(nn.Module):
    """
    Enhanced model with:
    - Multi-head attention for better feature focusing
    - Residual connections
    - Better dropout and regularization
    - Ensemble approach with multiple classifiers
    """
    
    def __init__(self, model_name='bert-base-uncased', num_classes=2, num_severity_levels=4):
        super(EnhancedAbusiveLanguageDetector, self).__init__()
        
        try:
            self.bert = BertModel.from_pretrained(model_name, local_files_only=True)
        except Exception as e:
            print(f"Attempting to download BERT model {model_name}...")
            self.bert = BertModel.from_pretrained(model_name)
            self.bert.save_pretrained(f"models/{model_name}")
            print(f"Model saved locally in models/{model_name}")
        
        hidden_size = self.bert.config.hidden_size
        
        # ============ ATTENTION LAYERS ============
        # Multi-head attention for better feature extraction
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_size,
            num_heads=8,
            dropout=0.1,
            batch_first=True
        )
        
        # ============ FEATURE EXTRACTION ============
        # Enhanced feature extraction with multiple paths
        self.feature_extraction = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),
            nn.LayerNorm(hidden_size),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.LayerNorm(hidden_size // 2),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size // 2, hidden_size // 4),
        )
        
        # Alternative feature path for diversity
        self.alternative_feature_path = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.15),
            nn.Linear(hidden_size // 2, hidden_size // 4),
            nn.ReLU(),
        )
        
        # ============ CLASSIFIERS ============
        feature_dim = hidden_size // 4
        
        # Abuse classifier (main task)
        self.abuse_classifier = nn.Sequential(
            nn.Linear(feature_dim * 2, feature_dim),
            nn.LayerNorm(feature_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(feature_dim, num_classes),
        )
        
        # Auxiliary classifier for robustness
        self.auxiliary_classifier = nn.Sequential(
            nn.Linear(feature_dim * 2, feature_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(feature_dim, num_classes),
        )
        
        # Severity classifier
        self.severity_classifier = nn.Sequential(
            nn.Linear(feature_dim * 2, feature_dim),
            nn.LayerNorm(feature_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(feature_dim, num_severity_levels),
        )
        
        # Confidence score predictor
        self.confidence_predictor = nn.Sequential(
            nn.Linear(feature_dim * 2, feature_dim // 2),
            nn.ReLU(),
            nn.Linear(feature_dim // 2, 1),
            nn.Sigmoid(),
        )
    
    def forward(self, input_ids, attention_mask, return_aux=False):
        """
        Forward pass with auxiliary outputs
        
        Args:
            input_ids: Token IDs
            attention_mask: Attention mask
            return_aux: Whether to return auxiliary classifier outputs
            
        Returns:
            abuse_logits, severity_logits, (auxiliary_logits, confidence)
        """
        # Get BERT outputs
        bert_output = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            output_hidden_states=True
        )
        
        # Use multiple BERT layers for richer representation
        last_hidden = bert_output.last_hidden_state
        pooled_output = bert_output.pooler_output
        
        # Apply attention mechanism
        attention_output, _ = self.attention(last_hidden, last_hidden, last_hidden)
        attention_output = attention_output.mean(dim=1)  # Global average pooling
        
        # Combine representations
        combined = pooled_output + attention_output * 0.5
        
        # Extract features through multiple paths
        features_main = self.feature_extraction(combined)
        features_alt = self.alternative_feature_path(combined)
        
        # Combine features
        combined_features = torch.cat([features_main, features_alt], dim=1)
        
        # Get predictions
        abuse_logits = self.abuse_classifier(combined_features)
        severity_logits = self.severity_classifier(combined_features)
        
        if return_aux:
            auxiliary_logits = self.auxiliary_classifier(combined_features)
            confidence = self.confidence_predictor(combined_features)
            return abuse_logits, severity_logits, auxiliary_logits, confidence
        
        return abuse_logits, severity_logits


class HybridAbusiveLanguageDetector(nn.Module):
    """
    Hybrid model combining BERT with rule-based token detection
    Provides both deep learning and fast rule-based inference
    """
    
    def __init__(self, model_name='bert-base-uncased', num_classes=2, num_severity_levels=4):
        super(HybridAbusiveLanguageDetector, self).__init__()
        
        # BERT-based component
        self.bert_model = EnhancedAbusiveLanguageDetector(
            model_name, num_classes, num_severity_levels
        )
        
        # Fusion layer to combine token-level information
        self.token_fusion = nn.Sequential(
            nn.Linear(num_classes + num_severity_levels, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
        )
        
        # Final fusion classifier
        self.fusion_classifier = nn.Sequential(
            nn.Linear(32 + num_classes, 32),
            nn.ReLU(),
            nn.Linear(32, num_classes),
        )
        
        self.num_classes = num_classes
        self.num_severity_levels = num_severity_levels
    
    def forward(self, input_ids, attention_mask, token_features=None):
        """
        Forward pass with optional token features
        
        Args:
            input_ids: Token IDs
            attention_mask: Attention mask
            token_features: Optional pre-computed token features (for tree-based detection)
                          Shape: (batch_size, num_classes + num_severity_levels)
            
        Returns:
            abuse_logits, severity_logits
        """
        # BERT forward pass
        abuse_logits, severity_logits = self.bert_model(input_ids, attention_mask)
        
        # If token features provided, fuse them
        if token_features is not None:
            fused = self.token_fusion(token_features)
            abuse_logits_final = self.fusion_classifier(
                torch.cat([abuse_logits, fused], dim=1)
            )
            return abuse_logits_final, severity_logits
        
        return abuse_logits, severity_logits


class LightweightAbusiveDetector(nn.Module):
    """
    Lightweight model for fast inference on resource-constrained devices
    Uses knowledge distillation from enhanced model
    """
    
    def __init__(self, model_name='bert-base-uncased', num_classes=2, num_severity_levels=4):
        super(LightweightAbusiveDetector, self).__init__()
        
        try:
            self.bert = BertModel.from_pretrained(model_name, local_files_only=True)
        except Exception:
            self.bert = BertModel.from_pretrained(model_name)
        
        hidden_size = self.bert.config.hidden_size
        
        # Lightweight feature extraction
        self.feature_extractor = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.LayerNorm(hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 2, hidden_size // 4),
        )
        
        # Simple classifiers
        self.abuse_classifier = nn.Linear(hidden_size // 4, num_classes)
        self.severity_classifier = nn.Linear(hidden_size // 4, num_severity_levels)
    
    def forward(self, input_ids, attention_mask):
        """Lightweight forward pass"""
        bert_output = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled = bert_output.pooler_output
        features = self.feature_extractor(pooled)
        
        abuse_logits = self.abuse_classifier(features)
        severity_logits = self.severity_classifier(features)
        
        return abuse_logits, severity_logits


# Alias for backward compatibility
AbusiveLanguageDetector = EnhancedAbusiveLanguageDetector
