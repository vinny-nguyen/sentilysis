import requests
import json
from scrape_reddit import scrape_reddit, format_reddit_data
import re



ticker = 'AAPL'
reddit_data = scrape_reddit(ticker)

# URL of your local FastAPI app
url = "http://localhost:8000/ai/generate"

results = []

for post in reddit_data:
    # Format each post as string
    post_string = f"""
Title: {post['title']}
Summary: {post['summary']}
Subreddit: {post['subreddit']}
Date: {post['date']}
Score: {post['score']}
"""

    # Create prompt for individual post
    prompt = f"""
You are an AI assistant that analyzes a Reddit post about a stock ticker and returns a structured summary.
Preserve the original message, the view of the stock (positive, negative, neutral), and the tone/emotion.
Retain the original message and information conveyed. Don't miss out on any insights, and any "whys". 

Post:
{post_string}

Return in JSON format like:
{{
    "summary": "short and clear summary of the post",
    "stock_view": "positive, negative, or neutral",
    "over_tone": "emotional tone (e.g. optimistic, fearful, excited)"
}}
"""

    payload = {
        "prompt": prompt
    }

    # Call the FastAPI endpoint
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        result = response.json()
        results.append({
            "input_post": post["title"],
            "ai_response": result.get("generated_text", "No response")
        })
    else:
        results.append({
            "input_post": post["title"],
            "ai_response": f"ERROR {response.status_code}: {response.text}"
        })

# Print or store results



def clean_ai_responses(data):
    cleaned = []
    for item in data:
        raw = item.get("ai_response", "")
        match = re.search(r"```json\s*(\{.*?\})\s*```", raw, re.DOTALL)
        if not match:
            match = re.search(r"(\{.*?\})", raw, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(1))
                cleaned.append(parsed)
            except json.JSONDecodeError:
                continue
    return cleaned







cleaned_data = clean_ai_responses(results)
print("\n\n--- Individual Summaries ---\n")

summaries = json.dumps(cleaned_data, indent=4)
print(summaries)


# ✅ NEW FINAL STEP: Generate overall sentiment analysis from summaries
final_prompt = f"""
You are a financial sentiment analysis expert.

You are given a list of AI-generated summaries of Reddit posts related to the stock `{ticker}`.
Each entry contains:
- A short summary of the post
- The stock view: positive, neutral, or negative
- The emotional tone

Your task is to create a structured sentiment report suitable for a dashboard. The report must:

1. Start with a **clear, balanced overview paragraph** summarizing the general outlook on the stock.
2. Then list categorized bullet points under **Positive**, **Neutral**, and **Negative**.
   - Only include points **from the summaries provided**.
   - Respect and use the `stock_view` and `summary` fields to decide where to categorize each point.
   - Do NOT skip any summaries — include all of them in one of the categories.
3. Each bullet point should be:
   - One sentence.
   - Informative and precise.
   - Preserving the key takeaway or insight from the original post.

Format:

Recent sentiment trends suggest [...summary paragraph...]

**Positive:**
- [...]

**Neutral:**
- [...]

**Negative:**
- [...]

If a category has no entries, write: `No major sentiment detected.`

Try to be as professional as possible. Avoid the term "Reddit User." Don't keep blatently mentioning
Reddit. Phrase the information in a way that sounds like a financial advisor is saying it. 

Here is the list of post summaries:
{summaries}
"""


# Call /ai/generate again
final_payload = {
    "prompt": final_prompt
}

response = requests.post(url, json=final_payload)

print("\n\n--- Final Sentiment Analysis ---\n")
if response.status_code == 200:
    result = response.json()
    print(result.get("generated_text", "No response"))
else:
    print(f"Error: {response.status_code}")
    print(response.text)
