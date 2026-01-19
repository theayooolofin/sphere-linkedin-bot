import os
import time
import random
import requests
from openai import OpenAI

# Setup from GitHub Secrets
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
token = os.environ["LINKEDIN_ACCESS_TOKEN"]
urn = os.environ["LINKEDIN_PERSON_URN"]

def generate_post():
    MAX_RETRIES = 5
    prompt_text = (
        "Write a punchy, minimalist LinkedIn post about sales or AI efficiency. "
        "Style: No long paragraphs. Use lots of white space. Tone: Authoritative. "
        "End with a sharp one-sentence takeaway."
    )
    
    for attempt in range(MAX_RETRIES):
        try:
            # Using GPT-4o-mini: It's fast, cheap, and very reliable
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt_text}]
            )
            return response.choices[0].message.content
        except Exception as e:
            if "429" in str(e) and attempt < MAX_RETRIES - 1:
                delay = 2.0 * (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limit hit. Retrying in {delay:.1f}s...")
                time.sleep(delay)
            else:
                raise e

def post_to_linkedin(content):
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {token}", 
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    post_data = {
        "author": f"urn:li:person:{urn}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": content},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    r = requests.post(url, headers=headers, json=post_data)
    if r.status_code == 201:
        print("✅ Success! OpenAI-generated post is live.")
    else:
        print(f"❌ LinkedIn Error: {r.status_code}, {r.text}")
        exit(1)

if __name__ == "__main__":
    text = generate_post()
    post_to_linkedin(text)
