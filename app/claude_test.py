import os
import requests
import anthropic
from dotenv import load_dotenv

load_dotenv()

# Lazy initialization of Anthropic client
_client = None

def get_anthropic_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ.get("CLAUDE_API_KEY"))
    return _client

def get_news_content_with_claude(url):
    website_response = requests.get(url)

    extracted_url = extract_url_with_claude(website_response.text)
    #print("Extracted URL:", extracted_url)
    return website_response.text

    ###
    # somehow remove ssr. from url MAYBE if necessary
    ###
    
    #website_response = requests.get(extracted_url)

    client = get_anthropic_client()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[
            {"role": "user", "content": f"""Parse this chunk of the HTML
              page and give me just the text of the news article: {website_response.text}"""}
        ]
    )

    return message.to_dict()["content"][0]["text"]

def extract_url_with_claude(text):
    client = get_anthropic_client()
    message = client.messages.create(
          model="claude-sonnet-4-20250514",
          max_tokens=4000,
          messages=[
              {"role": "user", "content": f"""Somewhere in the script on that website
              is an encoded URL. Find and return nothing but that URL: {text}"""},
              {"role": "assistant", "content": ":"} # to only get the URL and not the whole text
          ]
      )
    extracted_url = message.to_dict()["content"][0]["text"]
    return extracted_url 