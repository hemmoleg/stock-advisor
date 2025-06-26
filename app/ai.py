import re
#from transformers import AutoTokenizer, AutoModelForSequenceClassification
#import torch
#import torch.nn.functional as F
import os
from dotenv import load_dotenv
import openai

load_dotenv()

# Set environment variable to avoid tokenizer warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Load the tokenizer specific to the ProsusAI FinBERT model
# This tokenizer splits and encodes financial text in a way that matches the model's expectations
#tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
# Load the actual pretrained FinBERT model for sequence classification
# The model has been fine-tuned to classify financial text sentiment
#model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

# Define the labels used by the model: negative, neutral, and positive sentiment
labels = ["Positive", "Negative", "Neutral"]

#def classify_text_finbert(text):
#  # Tokenize the input text for the model
#  # 'return_tensors="pt"' tells the tokenizer to return PyTorch tensors
#  # 'truncation' and 'padding' ensure consistent input size
#  inputs = tokenizer(
#    text,
#    return_tensors="pt"
#  )
#  
#  # Turn off gradient tracking since we are doing inference, not training
#  with torch.no_grad():
#    # Pass the tokenized input through the model to get raw outputs (logits)
#    outputs = model(**inputs)
#  
#  # Apply softmax to convert logits into probabilities for each class
#  probs = F.softmax(outputs.logits, dim=1)
#  
#  # Get index of highest probability
#  pred_idx = torch.argmax(probs, dim=1).item()
#
#  return {
#      "sentiment": labels[pred_idx],
#      "probabilities": dict(zip(labels, probs[0].tolist()))
#  }

def extract_stocks(text):
  # Simple regex-based company extraction
  companies = []
  
  # Look for stock symbols in parentheses
  stock_pattern = r'\(([A-Z]{1,5})\)'
  matches = re.findall(stock_pattern, text)
  companies.extend(matches)
  
  # Look for common company suffixes
  company_pattern = r'([A-Z][A-Za-z\s&]+?(?:Inc\.|Corp\.|Ltd\.|LLC|Co\.|Company|Corporation|Limited))'
  matches = re.findall(company_pattern, text)
  companies.extend(matches)
  
  # Look for standalone capitalized words that might be company names
  standalone_pattern = r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\b'
  matches = re.findall(standalone_pattern, text)
  companies.extend(matches)
  
  return list(set(companies))

def classify_text(title): 
  # Function to analyze a news article using ChatGPT
  client = openai.OpenAI(api_key=os.environ.get("GPT_API_KEY"))
  
  prompt = f"""Analyze the sentiment of this financial news text and respond with ONLY the sentiment classification and probability score in this exact format:
              sentiment probability
                Where sentiment must be exactly one of: positive, negative, neutral
                And probability must be a number between 0 and 1 (e.g., 0.85)
                
                Text to analyze: {title}

                Respond with only the sentiment and probability, nothing else."""

  try:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
          {"role": "user", "content": prompt}
        ],
        temperature=0.1  # Low temperature for more consistent outputs
      )
    
    response = completion.choices[0].message.content.strip()
    
    # Parse the response to extract sentiment and probability
    parts = response.split()
    if len(parts) >= 2:
        sentiment = parts[0].lower()
        try:
            probability = float(parts[1])
            # Ensure probability is between 0 and 1
            probability = max(0.0, min(1.0, probability))
        except ValueError:
            probability = 0.5  # Default probability if parsing fails
    else:
        sentiment = "neutral"
        probability = 0.5
    
    # Ensure sentiment is one of the expected values
    if sentiment not in ["positive", "negative", "neutral"]:
        sentiment = "neutral"
    
    #companies = extract_stocks(title)
    
    return {
        "sentiment": sentiment.capitalize(),
        "probabilities": {
            "Positive": probability if sentiment == "positive" else 0.0,
            "Negative": probability if sentiment == "negative" else 0.0,
            "Neutral": probability if sentiment == "neutral" else 0.0
        },
        #"companies": companies
    }
    
  except Exception as e:
    print(f"Error in ChatGPT classification: {e}")
    # Fallback to neutral sentiment
    companies = extract_stocks(title)
    return {
        "sentiment": "Neutral",
        "probabilities": {"Positive": 0.0, "Negative": 0.0, "Neutral": 1.0},
        #"companies": companies
    }
  

def gpt_test():
  client = openai.OpenAI(api_key=os.environ.get("GPT_API_KEY"))
  #prompt = f"Extract the full text of the article at this URL: https://finnhub.io/api/news?id=63bc3d8fbc2f47fbea40de0ad793510e831f1e0194099c48768be9e796c70c53. If the article cannot be accessed, summarize what it is about."
  #prompt = "give me the text from the article at https://finnhub.io/api/news?id=63bc3d8fbc2f47fbea40de0ad793510e831f1e0194099c48768be9e796c70c53"
  prompt = "give me the text from the article at https://finnhub.io/api/news?id=bbe91f3e19b36c6f3ef413ddb16497ea38e6eba4e98764cbf2637e5390868a35 use finnhub as a source"
  completion = client.chat.completions.create(
      #model="gpt-4.1-nano-2025-04-14",
      #model="o4-mini-2025-04-16",
      #model="gpt-4o-mini-2024-07-18",
      #model="gpt-4.1-mini-2025-04-14",
      #model="gpt-4.1-2025-04-14",
      #model="chatgpt-4o-latest",
      #model="gpt-4-turbo-2024-04-09",
      #model="gpt-4o-mini-search-preview-2025-03-11",
      model="gpt-4o-search-preview-2025-03-11",
      messages=[
        {"role": "user", "content": prompt}
      ]
    )

  print(completion.choices[0].message)
