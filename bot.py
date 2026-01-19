import os
import requests
from google import genai

# Setup using the NEW library
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
token = os.environ["LINKEDIN_ACCESS_TOKEN"]
urn = os.environ["LINKEDIN_PERSON_URN"]

def generate_post():
    # Using the most stable modern model
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Write a punchy, minimalist LinkedIn post about sales or AI efficiency. Use short sentences and lots of white space."
    )
    return response.text

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
        print("✅ Success!")
    else:
        print(f"❌ Failed: {r.status_code}, {r.text}")
        exit(1)

if __name__ == "__main__":
    text = generate_post()
    post_to_linkedin(text)
