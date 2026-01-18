import os
import requests
import google.generativeai as genai

# Setup from your GitHub Vault
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
token = os.environ["LINKEDIN_ACCESS_TOKEN"]
urn = os.environ["LINKEDIN_PERSON_URN"]

def generate_post():
    model = genai.GenerativeModel('gemini-1.5-flash')
    # This prompt uses your "Punchy-Minimalist" style
    prompt = """
    Write a LinkedIn post in my voice. 
    Style: Punchy-Minimalist. No long paragraphs. Use lots of white space.
    Tone: Authoritative and direct. No corporate fluff.
    Topics: Sales mindset, AI efficiency, or the 'luxurious' engineering behind Sphere.ng.
    End with a sharp one-sentence takeaway.
    """
    response = model.generate_content(prompt)
    return response.text

def post_to_linkedin(content):
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {"Authorization": f"Bearer {token}", "X-Restli-Protocol-Version": "2.0.0"}
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
    print(f"Post Status: {r.status_code}")

if __name__ == "__main__":
    text = generate_post()
    post_to_linkedin(text)
