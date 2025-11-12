# 🌺 HNN Fast – Hawaii Local News Scraper & AI Summarizer 📰✨  

**HNN Fast** is a modern web app that automatically scrapes **Hawaii News Now**’s latest stories each day and transforms them into a clean, engaging newsletter — written by AI, formatted in Markdown, and sprinkled with emojis and links 🌴🤖.  

---

## 🚀 Overview  

Every morning, **HNN Fast**:  
1. 🧠 Pulls the newest articles directly from [hawaiinewsnow.com](https://www.hawaiinewsnow.com) using **SERP API**.  
2. 🗞️ Summarizes all stories into a **business & accounting–focused** newsletter using **OpenRouter’s LLMs** (e.g. Gemini or DeepSeek).  
3. 💾 Saves the newsletter into a lightweight local **SQLite database (`news_archive.db`)** for quick caching and reuse.  
4. 🌐 Serves the results through a **Django web interface**, deployable on [Render.com](https://render.com).  

---

## ✨ Features  

| Feature | Description |
|----------|-------------|
| 🔍 **Daily Scrape** | Automatically collects that day’s news via SERP API queries. |
| 🤖 **AI Summarization** | Generates human-readable, Markdown-formatted newsletters with emojis and links. |
| 💾 **Caching** | Saves each day’s newsletter in `news_archive.db` so repeated requests return instantly. |
| ⚡ **Django Backend** | Built on Django 5 with Whitenoise for fast, secure static delivery. |
| ☁️ **Render Deployment** | Easily deployable to the Render free tier with `render.yaml` and `build.sh`. |
| 💬 **Modern Markdown Output** | Share-ready output that looks great in Slack, email, or your favorite Markdown viewer. |

---

## 🛠️ Tech Stack  

- **Backend:** Django 5.0 + Python 3.11  
- **AI Engine:** [OpenRouter API](https://openrouter.ai/) (Gemini / DeepSeek models)  
- **Scraper:** [SERP API](https://serpapi.com) for reliable Google search results  
- **Database:** SQLite (`news_archive.db`)  
- **Deployment:** Render.com (Free Tier)  
- **Environment Management:** Python `venv` + `.env` via `python-dotenv`  

---

## ⚙️ Environment Setup  

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/HNN_Fast.git
cd HNN_Fast

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations and start the app
python manage.py migrate
python manage.py runserver
