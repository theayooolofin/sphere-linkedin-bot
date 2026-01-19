import os
import requests
from openai import OpenAI

# Setup
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
token = os.environ["LINKEDIN_ACCESS_TOKEN"]
raw_id = os.environ["LINKEDIN_PERSON_URN"]

def generate_post():
    prompt_text = "Write a punchy, minimalist LinkedIn post about sales or AI. Use lots of white space."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt_text}]
    )
    return response.choices[0].message.content

def post_to_linkedin(content):
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {token}", 
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    
    # Clean the ID to remove any accidental prefixes
    clean_id = str(raw_id).replace("urn:li:person:", "").replace("urn:li:member:", "")
    
    post_data = {
        # Using 'member' which is the standard for modern individual URNs
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
        print("✅ SUCCESS! The post is live on your profile.")
    else:
        # If member fails, we try one last time with person
        print("Switching namespace and retrying...")
        post_data["author"] = f"urn:li:person:{clean_id}"
        r = requests.post(url, headers=headers, json=post_data)
        
        if r.status_code == 201:
            print("✅ SUCCESS! (Posted using Person namespace)")
        else:
            print(f"❌ Final LinkedIn Error: {r.status_code}")
            print(f"Details: {r.text}")
            exit(1)

if __name__ == "__main__":
    text = generate_post()
    post_to_linkedin(text)
