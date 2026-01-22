import os
import requests
from openai import OpenAI

# Initialize
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
token = os.environ["LINKEDIN_ACCESS_TOKEN"]
raw_id = os.environ["LINKEDIN_PERSON_URN"]

def generate_post():
    # Punchy-minimalist voice
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Write a short, punchy LinkedIn post about AI sales efficiency. Use lots of white space."}]
    )
    return response.choices[0].message.content

def post_to_linkedin(content):
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {token}", 
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    
    # Strip any accidental prefixes to prevent the 'Data Processing' error
    clean_id = str(raw_id).replace("urn:li:person:", "").replace("urn:li:member:", "").strip()
    
    post_data = {
        # Using the strictly required member namespace with your verified ID
        "author": f"urn:li:member:{clean_id}",
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
        print("✅ SUCCESS! Your automated post is finally live.")
    else:
        print(f"❌ FAILED: {r.status_code}")
        print(f"Details: {r.text}")
        exit(1)

if __name__ == "__main__":
    text = generate_post()
    post_to_linkedin(text)
