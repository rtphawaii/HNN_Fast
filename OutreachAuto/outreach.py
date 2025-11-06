from pathlib import Path
from dotenv import load_dotenv
import os
import requests
from openai import OpenAI

load_dotenv()  # reads .env file

SERP_API_KEY=os.getenv("SERP_API_KEY")

# Load LLM
load_dotenv()
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

# Initialize client (once at startup)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=openrouter_api_key,
)

def query_llm(prompt_text):
    prompt='You are helping a prospective business partner write a 5 sentence informed and researched outreach message to a prospective customer, use the following information to draft a message and only include the content of the message with the name of the customer. Dont include a subject line. The following content is the customer you are writing to: '
    try:
        completion = client.chat.completions.create(
            model="x-ai/grok-4-fast",
            messages=[
                {"role": "user", "content": prompt+prompt_text}
            ]
        )

        return completion.choices[0].message.content
    except Exception as e:
        print(f"[LLM ERROR] {e}")
        return "⚠️ LLM request failed. Check your API key or network."

def flatten_profile(profile):
    def _flatten(obj, parent_key=''):
        items = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                items.extend(_flatten(v, new_key))
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                new_key = f"{parent_key}[{i}]"
                items.extend(_flatten(v, new_key))
        else:
            if obj not in (None, "", []):
                items.append((parent_key, str(obj)))
        return items

    flattened_items = _flatten(profile)
    return ", ".join(f"{k}: {v}" for k, v in flattened_items)

def outreach(query):

    query=f'site:linkedin.com/in "{query}"'

    params = {
    "engine": "google",
    "q": query,
    "hl": "en",
    "num": "5",
    "api_key": SERP_API_KEY
    }

    resp = requests.get("https://serpapi.com/search", params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    print('SERP RESULT: ', resp)

    print("SERP URL:", resp.url)                         # helpful for debugging
    organic = data.get("organic_results") or []
    print("SERP organic count:", len(organic))

    # Extract LinkedIn profiles
    profiles = []
    for item in organic:
        link = item.get("link") or item.get("displayed_link") or ""
        title = item.get("title") or ""
        snippet = item.get("snippet") or ""
        if "linkedin.com/in" in link:                    # only personal profiles
            profiles.append({
                "link": link,
                "parsed": flatten_profile({"title": title, "snippet": snippet})
            })

    print("Parsed profiles:", profiles)

    # Run your LLM (or other logic) to create the result rows
    results = []
    for p in profiles:
        try:
            llm_title = query_llm(p["parsed"])           # your function
        except Exception as e:
            llm_title = "Profile summary unavailable"
            print("LLM error:", e)

        results.append({
            "title": llm_title,
            "link": p["link"],
            "subtitle": ""                               # fill if you want
        })

    print("Final results:", results)
    return results
