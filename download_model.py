import os
from transformers import BertTokenizer, BertModel

def download_bert():
    print("Downloading BERT model and tokenizer...")
    
    # Create models directory if it doesn't exist
    os.makedirs('models/bert-base-uncased', exist_ok=True)
    
    try:
        # Download and save tokenizer
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        tokenizer.save_pretrained('models/bert-base-uncased')
        print("✓ Tokenizer downloaded and saved")
        
        # Download and save model
        model = BertModel.from_pretrained('bert-base-uncased')
        model.save_pretrained('models/bert-base-uncased')
        print("✓ Model downloaded and saved")
        
        print("\nSuccess! Model and tokenizer saved to models/bert-base-uncased/")
        print("You can now use the system in offline mode.")
        
    except Exception as e:
        print(f"\nError downloading model: {str(e)}")
        print("Please check your internet connection and try again.")

if __name__ == '__main__':
    download_bert()