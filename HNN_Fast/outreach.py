from pathlib import Path
from dotenv import load_dotenv
import os
import requests
from openai import OpenAI
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()  # reads .env file once

SERP_API_KEY = os.getenv("SERP_API_KEY")
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

# ---------------------- Paths ---------------------- #

# Project root (HNN_FAST/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Where the SQLite DB lives.
# Default: <project_root>/news_archive.db
# You can override with NEWS_DB_PATH in Render env vars if needed.
DB_PATH = Path(os.getenv("NEWS_DB_PATH", BASE_DIR / "news_archive.db"))


# ---------------------- DB Helpers ---------------------- #

def init_db(db_path: Path = DB_PATH):
    """Ensure the news_archive table exists."""
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS news_archive (
            date TEXT PRIMARY KEY,
            content TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def get_news_for_date(date_str: str, db_path: Path = DB_PATH) -> str | None:
    """Return stored newsletter text for a given date (YYYY-MM-DD) if present."""
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("SELECT content FROM news_archive WHERE date = ?", (date_str,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    return None


def save_news_for_date(date_str: str, content: str, db_path: Path = DB_PATH):
    """Insert or replace the newsletter content for a given date."""
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO news_archive (date, content)
        VALUES (?, ?)
    """, (date_str, content))
    conn.commit()
    conn.close()


# ---------------------- LLM + SERP Logic ---------------------- #

# Initialize OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=openrouter_api_key,
)

def query_llm(prompt_text: str) -> str:
    prompt = (
        "Write a business and accounting focused newsletter in markdown format "
        "with emojis and links that summarizes all of the articles:\n\n"
    )
    try:
        completion = client.chat.completions.create(
            # model="deepseek/deepseek-chat-v3-0324",
            model="google/gemini-2.5-flash",
            messages=[
                {"role": "user", "content": prompt + prompt_text}
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


def format_serp_results(organic):
    """
    Takes a list of SERP API 'organic_results' and returns
    a formatted string with titles, links, and snippets.
    """
    if not organic:
        return "No organic results found."

    formatted = []
    for i, result in enumerate(organic, start=1):
        title = result.get("title", "No title")
        link = result.get("link", "No link")
        snippet = result.get("snippet", "No snippet")
        formatted.append(f"{i}. {title}\n   {link}\n   {snippet}\n")

    return "\n".join(formatted)


def outreach(keyword: str | None = None,
             max_results: int = 100,
             page_size: int = 10) -> str:
    """
    - If today's newsletter exists in SQLite (news_archive.db), return it.
    - Otherwise:
        - Search Hawaii News Now for today's articles (by date path).
        - Optionally filter with a keyword (in the Google query).
        - Paginate through Google/SerpAPI to collect up to max_results.
        - Send a formatted digest of all articles to the LLM.
        - Store the generated newsletter in SQLite and return it.
    """

    if not SERP_API_KEY:
        raise RuntimeError("SERP_API_KEY is not set in the environment.")

    # Make sure DB/table exists
    init_db()

    # Dates:
    # - date_path: for the URL (yyyy/mm/dd)
    # - date_key: for DB (yyyy-mm-dd)
    hawaii_tz = ZoneInfo("Pacific/Honolulu")
    now = datetime.now(hawaii_tz)
    date_path = now.strftime('%Y/%m/%d')
    date_key = now.strftime('%Y-%m-%d')

    # 1) Check DB cache first
    cached = get_news_for_date(date_key)
    if cached:
        print(f"[CACHE HIT] Returning newsletter from DB for {date_key}")
        return cached

    print(f"[CACHE MISS] No entry for {date_key}, generating new newsletter...")

    # 2) Build Google query
    base_query = f"site:https://www.hawaiinewsnow.com/{date_path}/"

    full_query = base_query

    print("Search query:", full_query)

    # 3) Collect SERP results with pagination
    all_organic = []
    start = 0

    while len(all_organic) < max_results:
        params = {
            "engine": "google",
            "q": full_query,
            "hl": "en",
            "num": page_size,   # results per page
            "start": start,     # pagination offset: 0, 10, 20, ...
            "api_key": SERP_API_KEY,
        }

        resp = requests.get("https://serpapi.com/search", params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        print(f"[SERP] URL: {resp.url}")
        organic = data.get("organic_results") or []
        print(f"[SERP] start={start}, organic count={len(organic)}")

        if not organic:
            break  # no more pages

        all_organic.extend(organic)

        pagination = data.get("serpapi_pagination", {})
        if "next" not in pagination:
            break

        start += page_size

    all_organic = all_organic[:max_results]
    print("Total organic collected:", len(all_organic))

    # 4) Format and send to LLM
    articles = format_serp_results(all_organic)
    print("Formatted articles string length:", len(articles))

    newsletter_text = query_llm(articles)

    # 5) Save to DB for future calls
    save_news_for_date(date_key, newsletter_text)
    print(f"[DB] Saved newsletter for {date_key} at {DB_PATH}")

    return newsletter_text
