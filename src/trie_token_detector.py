"""
Tree-based (Trie) Token Detector for Fast Abusive Content Detection
This module implements a Trie data structure for O(n) token matching
"""

from typing import List, Dict, Set, Tuple
import re
from collections import defaultdict


class TrieNode:
    """Node in the Trie data structure"""
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.severity_level = 0  # 0=safe, 1=mild, 2=serious, 3=severe
        self.word = ""


class AbusiveTokenTrie:
    """
    Trie-based dictionary for efficient abusive token detection.
    Provides O(n) lookup time complexity where n is the length of the text.
    """
    
    def __init__(self):
        self.root = TrieNode()
        self.total_tokens = 0
        
    def insert(self, word: str, severity: int = 1):
        """
        Insert a token into the Trie with its severity level.
        
        Args:
            word: The abusive token to insert
            severity: Severity level (0=safe, 1=mild, 2=serious, 3=severe)
        """
        word = word.lower().strip()
        node = self.root
        
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        node.is_end = True
        node.severity_level = severity
        node.word = word
        self.total_tokens += 1
    
    def search(self, text: str) -> List[Tuple[str, int, Tuple[int, int]]]:
        """
        Search for all abusive tokens in text.
        
        Args:
            text: Text to search in
            
        Returns:
            List of (token, severity, position) tuples
        """
        text = text.lower()
        matches = []
        
        for i in range(len(text)):
            node = self.root
            for j in range(i, len(text)):
                char = text[j]
                
                if char not in node.children:
                    break
                    
                node = node.children[char]
                
                if node.is_end:
                    # Check if it's a word boundary (not part of larger word)
                    if self._is_word_boundary(text, i, j + 1):
                        matches.append((node.word, node.severity_level, (i, j + 1)))
        
        return matches
    
    def search_with_variations(self, text: str) -> List[Tuple[str, int, Tuple[int, int], str]]:
        """
        Search considering common text variations (leetspeak, misspellings, etc.)
        
        Args:
            text: Text to search in
            
        Returns:
            List of (token, severity, position, variation_type) tuples
        """
        matches = self.search(text)
        text_normalized = self._normalize_leetspeak(text)
        matches_variations = self.search(text_normalized)
        
        # Combine and deduplicate
        all_matches = []
        seen = set()
        
        for token, severity, pos in matches:
            key = (pos[0], pos[1])
            if key not in seen:
                all_matches.append((token, severity, pos, 'exact'))
                seen.add(key)
        
        for token, severity, pos in matches_variations:
            key = (pos[0], pos[1])
            if key not in seen:
                all_matches.append((token, severity, pos, 'variation'))
                seen.add(key)
        
        return all_matches
    
    def _is_word_boundary(self, text: str, start: int, end: int) -> bool:
        """Check if position is at word boundaries"""
        if start > 0 and text[start - 1].isalnum():
            return False
        if end < len(text) and text[end].isalnum():
            return False
        return True
    
    def _normalize_leetspeak(self, text: str) -> str:
        """Convert common leetspeak variations"""
        replacements = {
            '4': 'a',
            '3': 'e',
            '0': 'o',
            '1': 'i',
            '5': 's',
            '7': 't',
            '8': 'b',
            '9': 'g',
            '@': 'a',
            '$': 's',
            '!': 'i',
        }
        result = text
        for old, new in replacements.items():
            result = result.replace(old, new)
        return result
    
    def get_stats(self) -> Dict:
        """Get statistics about the Trie"""
        return {
            'total_tokens': self.total_tokens,
            'trie_size': self._count_nodes(),
        }
    
    def _count_nodes(self) -> int:
        """Count total nodes in Trie"""
        count = 0
        stack = [self.root]
        while stack:
            node = stack.pop()
            count += 1
            stack.extend(node.children.values())
        return count


class AbusiveTokenDatabase:
    """
    Comprehensive database of abusive tokens categorized by severity
    """
    
    def __init__(self):
        self.trie = AbusiveTokenTrie()
        self.tokens_by_severity = defaultdict(set)
        self.contextual_patterns = []
        
    def load_from_csv(self, csv_data: List[str]):
        """
        Load tokens from CSV data format.
        Expected format: one token per line or token,severity format
        """
        for line in csv_data:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split(',')
            token = parts[0].strip()
            severity = int(parts[1]) if len(parts) > 1 else 1
            
            self.add_token(token, severity)
    
    def load_from_text_corpus(self, texts: List[str], labels: List[int]):
        """
        Learn abusive tokens from text corpus using frequency analysis.
        
        Args:
            texts: List of text samples
            labels: List of corresponding labels (1=abusive, 0=non-abusive)
        """
        token_frequency = defaultdict(lambda: {'abusive': 0, 'non_abusive': 0})
        
        for text, label in zip(texts, labels):
            tokens = self._tokenize(text)
            for token in tokens:
                if label == 1:
                    token_frequency[token]['abusive'] += 1
                else:
                    token_frequency[token]['non_abusive'] += 1
        
        # Calculate abusive ratio and add high-confidence tokens
        for token, counts in token_frequency.items():
            total = counts['abusive'] + counts['non_abusive']
            if total >= 2:  # Minimum occurrence threshold
                abusive_ratio = counts['abusive'] / total
                if abusive_ratio > 0.7:  # 70% threshold
                    severity = self._calculate_severity(abusive_ratio, counts['abusive'])
                    self.add_token(token, severity)
    
    def add_token(self, token: str, severity: int = 1):
        """Add a token to the database"""
        self.trie.insert(token, severity)
        self.tokens_by_severity[severity].add(token.lower())
    
    def add_contextual_pattern(self, pattern: str, severity: int = 1):
        """Add a regex pattern for contextual detection"""
        self.contextual_patterns.append((re.compile(pattern, re.IGNORECASE), severity))
    
    def detect(self, text: str) -> Dict:
        """
        Detect abusive content in text.
        
        Returns:
            Dict with detection results including tokens found and severity level
        """
        tokens_found = self.trie.search_with_variations(text)
        
        # Check contextual patterns
        pattern_matches = []
        for pattern, severity in self.contextual_patterns:
            matches = pattern.finditer(text)
            for match in matches:
                pattern_matches.append((match.group(), severity, match.span(), 'pattern'))
        
        all_matches = tokens_found + pattern_matches
        
        # Calculate overall severity
        if not all_matches:
            overall_severity = 0
            is_abusive = False
            confidence = 0.0
        else:
            max_severity = max(m[1] for m in all_matches)
            overall_severity = max_severity
            is_abusive = True
            confidence = min(0.95, len(all_matches) * 0.1 + 0.3)  # Scale with number of matches
        
        return {
            'is_abusive': is_abusive,
            'confidence': confidence,
            'severity': overall_severity,
            'tokens_found': tokens_found,
            'patterns_found': pattern_matches,
            'total_matches': len(all_matches),
        }
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        return re.findall(r'\b\w+\b', text.lower())
    
    def _calculate_severity(self, ratio: float, count: int) -> int:
        """Calculate severity based on frequency ratio and count"""
        if ratio > 0.9:
            return 3  # Severe
        elif ratio > 0.8:
            return 2 if count >= 5 else 2  # Serious
        elif ratio > 0.75:
            return 2  # Serious
        else:
            return 1  # Mild
    
    def get_statistics(self) -> Dict:
        """Get statistics about the token database"""
        return {
            'total_tokens': self.trie.total_tokens,
            'tokens_by_severity': {
                'mild': len(self.tokens_by_severity[1]),
                'serious': len(self.tokens_by_severity[2]),
                'severe': len(self.tokens_by_severity[3]),
            },
            'contextual_patterns': len(self.contextual_patterns),
        }


def create_default_token_database() -> AbusiveTokenDatabase:
    """
    Create a default database with common abusive tokens.
    In production, this would be loaded from a comprehensive list.
    """
    db = AbusiveTokenDatabase()
    
    # Severe tokens (explicit profanity)
    severe_tokens = [
        'fuck', 'shit', 'bitch', 'asshole', 'bastard', 'cunt', 'damn',
        'hell', 'piss', 'motherfucker', 'fucking', 'shitty', 'bullshit',
    ]
    for token in severe_tokens:
        db.add_token(token, 3)
    
    # Serious tokens (offensive language)
    serious_tokens = [
        'sucks', 'hate', 'stupid', 'idiot', 'dumb', 'loser', 'ass',
        'dick', 'pussy', 'whore', 'slut', 'faggot', 'gay', 'nigga',
    ]
    for token in serious_tokens:
        db.add_token(token, 2)
    
    # Mild tokens (mildly offensive)
    mild_tokens = [
        'crap', 'bloody', 'pissed', 'sarcasm', 'weird', 'gross',
    ]
    for token in mild_tokens:
        db.add_token(token, 1)
    
    # Contextual patterns
    db.add_contextual_pattern(r'\b(kill|murder|die)\s+(yourself|him|her|them|us)\b', 3)
    db.add_contextual_pattern(r'\b(rape|assault|abuse)\b', 3)
    db.add_contextual_pattern(r'\b(hate|despise)\s+(group|race|ethnicity)\b', 2)
    
    return db
