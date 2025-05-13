from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

# Load the tokenizer specific to the ProsusAI FinBERT model
# This tokenizer splits and encodes financial text in a way that matches the model's expectations
tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
# Load the actual pretrained FinBERT model for sequence classification
# The model has been fine-tuned to classify financial text sentiment
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

# Define the labels used by the model: negative, neutral, and positive sentiment
labels = ["Positive", "Negative", "Neutral"]

def analyze_sentiment(text):
  # Tokenize the input text for the model
  # 'return_tensors="pt"' tells the tokenizer to return PyTorch tensors
  # 'truncation' and 'padding' ensure consistent input size
  inputs = tokenizer(
    text,
    return_tensors="pt"
  )
  
  # Turn off gradient tracking since we are doing inference, not training
  with torch.no_grad():
    # Pass the tokenized input through the model to get raw outputs (logits)
    outputs = model(**inputs)
  
  # Apply softmax to convert logits into probabilities for each class
  probs = F.softmax(outputs.logits, dim=1)
  
 # Get index of highest probability
  pred_idx = torch.argmax(probs, dim=1).item()

  return {
      "sentiment": labels[pred_idx],
      "probabilities": dict(zip(labels, probs[0].tolist()))
  }