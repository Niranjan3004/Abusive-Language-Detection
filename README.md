# Abusive Language Detection

This project implements a BERT-based model for detecting abusive language in text.

## Project Structure
```
Abusive Language Detection/
├── data/               # Directory for dataset files
├── src/               # Source code
│   ├── model.py       # Model architecture
│   ├── data.py        # Data preprocessing
│   └── train.py       # Training script
├── output/            # Model outputs and checkpoints
└── requirements.txt   # Project dependencies
```

## Setup

1. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Prepare your dataset:
   - Place your training data at `data/train.csv`
   - Place your testing data at `data/test.csv`
   - The CSV files should have columns: `text` and `label`

4. Configure the environment:
   - The project uses the following environment variables (defined in `env` file):
     - TRAIN_DATASET: Path to training dataset
     - TEST_DATASET: Path to testing dataset
     - EPOCHS: Number of training epochs
     - BATCH_SIZE: Training batch size
     - LEARNING_RATE: Learning rate for optimization
     - OUTPUT_DIR: Directory for saving model outputs

## Training

To train the model:

```bash
python src/train.py
```

The best model will be saved in the `output` directory.

## Model Architecture

The model uses BERT (bert-base-uncased) as the backbone with a classification head on top for binary classification of abusive language.

## Requirements

- Python 3.7+
- PyTorch
- Transformers
- Pandas
- NumPy
- scikit-learn
- python-dotenv
- tqdm# Abusive-Language-Detection
