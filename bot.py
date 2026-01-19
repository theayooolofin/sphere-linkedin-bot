import os
import time
import requests
from google import genai
from google.genai import errors

# Setup
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
token = os.environ["LINKEDIN_ACCESS_TOKEN"]
urn = os.environ["LINKEDIN_PERSON_URN"]

def generate_post():
    MAX_RETRIES = 3
    # Your minimalist, authoritative prompt
    prompt_text = "Write a punchy, minimalist LinkedIn post about sales or AI efficiency. Use short sentences and lots of white space."
    
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt_text
            )
            return response.text
        except errors.ClientError as e:
            # If we hit the 429 quota limit, wait 60 seconds and try again
            if "429" in str(e) and attempt < MAX_RETRIES - 1:
                print(f"Quota hit. Retrying in 60 seconds... (Attempt {attempt + 1})")
                time.sleep(60)
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
        print("✅ Success! The post is live.")
    else:
        print(f"❌ LinkedIn Post Failed: {r.status_code}, {r.text}")
        exit(1)

if __name__ == "__main__":
    text = generate_post()
    post_to_linkedin(text)
