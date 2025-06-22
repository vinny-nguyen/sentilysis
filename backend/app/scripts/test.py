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
final_payload = {"prompt": final_prompt}

response = requests.post(url, json=final_payload)

print("\n\n--- Final Sentiment Analysis ---\n")
if response.status_code == 200:
    result = response.json()
    print(result.get("generated_text", "No response"))
else:
    print(f"Error: {response.status_code}")
    print(response.text)
