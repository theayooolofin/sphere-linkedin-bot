import os
import requests
import google.generativeai as genai

# Setup from your GitHub Vault
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
token = os.environ["LINKEDIN_ACCESS_TOKEN"]
urn = os.environ["LINKEDIN_PERSON_URN"]

def generate_post():
    # Using 'gemini-1.5-flash-latest' to avoid the 404 error
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    prompt = """
    Write a LinkedIn post in my voice. 
    Style: Punchy-Minimalist. No long paragraphs. Use white space.
    Tone: Authoritative and direct. No corporate fluff.
    Topics: Sales mindset, AI efficiency, or the 'luxurious' engineering behind Sphere.ng.
    End with a sharp one-sentence takeaway.
    """
    
    response = model.generate_content(prompt)
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
        print("✅ Success! Post is live.")
    else:
        print(f"❌ Failed: {r.status_code}")
        print(f"Details: {r.text}")
        exit(1)

if __name__ == "__main__":
    try:
        text = generate_post()
        post_to_linkedin(text)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
