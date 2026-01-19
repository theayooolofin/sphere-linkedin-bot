import os
import requests
import google.generativeai as genai

# Setup from GitHub Secrets
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
token = os.environ["LINKEDIN_ACCESS_TOKEN"]
urn = os.environ["LINKEDIN_PERSON_URN"]

def generate_post():
    # Use the stable model name to prevent 404 errors
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Using your "Punchy-Minimalist" style rules
    prompt = """
    Write a LinkedIn post in my voice. 
    Style: Punchy-Minimalist. Short, one-sentence paragraphs. Use white space.
    Tone: Authoritative and direct. No corporate fluff.
    Hook: Start with a provocative hook about sales or AI efficiency.
    Ending: A sharp one-sentence takeaway.
    Topics: Sales mindset, AI automation, or the 'luxurious' engineering of Sphere.ng.
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
        print("✅ Success! Post is live on LinkedIn.")
    else:
        print(f"❌ Failed: {r.status_code}, {r.text}")
        exit(1)

if __name__ == "__main__":
    text = generate_post()
    post_to_linkedin(text)
