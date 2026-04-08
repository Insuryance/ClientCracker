# 🎯 Client Hunter

**Find any company's clients from their website AND hidden sources across the internet.**

Give it a company's website (e.g., `www.stripe.com`), and Client Hunter will:

1. **Scrape the website** for listed clients, partners, case studies, and testimonials
2. **Search the internet** (news articles, Reddit, blogs) for unlisted clients
3. **Combine everything** into a clean, downloadable Excel spreadsheet

Perfect for **competitive analysis** - find out who's using your competitor's product so you can target those same companies.

---

## 🚀 What You'll Need (Prerequisites)

Don't worry — I'll walk you through everything. Here's what we need:

| Tool | What It Is | Why We Need It |
|------|-----------|---------------|
| **Python 3.10+** | A programming language | Runs our code |
| **Git** | Version control tool | Puts our project on GitHub |
| **GitHub account** | Code hosting platform | Stores our project online |
| **Anthropic API key** | AI access key | Claude reads & understands websites |

---

## 📦 Step-by-Step Setup (For Complete Beginners)

### Step 1: Install Python

**On Mac:**
```bash
# Open Terminal (search "Terminal" in Spotlight)
# Install Homebrew first (a package manager)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Then install Python
brew install python
```

**On Windows:**
1. Go to [python.org/downloads](https://python.org/downloads)
2. Download Python 3.12+
3. **IMPORTANT:** Check ✅ "Add Python to PATH" during install
4. Open Command Prompt (search "cmd" in Start)

**Verify it works:**
```bash
python3 --version
# Should show: Python 3.10.x or higher
```

### Step 2: Install Git

**On Mac:**
```bash
brew install git
```

**On Windows:**
1. Go to [git-scm.com](https://git-scm.com)
2. Download and install (keep all defaults)

**Verify:**
```bash
git --version
```

### Step 3: Get an Anthropic API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up for a free account
3. Go to **API Keys** → **Create Key**
4. Copy the key (starts with `sk-ant-...`) — you'll need it soon
5. Add some credits ($5 is more than enough to start)

### Step 4: Download & Set Up This Project

```bash
# Clone the project (downloads it to your computer)
git clone https://github.com/YOUR_USERNAME/client-hunter.git
cd client-hunter

# Create a virtual environment (keeps things clean)
python3 -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# You should now see (venv) at the start of your terminal line

# Install all required packages
pip install -r requirements.txt
```

### Step 5: Add Your API Key

```bash
# Copy the example config file
cp .env.example .env

# Open .env in a text editor and paste your API key
# On Mac:
open .env
# On Windows:
notepad .env
```

Inside `.env`, replace the placeholder:
```
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

### Step 6: Run the App! 🎉

```bash
streamlit run app.py
```

Your browser will open at `http://localhost:8501` with the app running!

---

## 🎮 How to Use

1. **Enter a website URL** (e.g., `https://www.notion.so`)
2. **Click "Hunt for Clients"**
3. **Wait** — the tool scrapes the site, then searches the web (takes 1–3 minutes)
4. **Review** the client list with sources and confidence levels
5. **Download** the Excel file for your outreach

---

## 📁 Project Structure

```
client-hunter/
├── app.py                 # Main app (the UI you see in browser)
├── src/
│   ├── __init__.py
│   ├── website_scraper.py # Scrapes the target company's website
│   ├── web_enricher.py    # Searches news, Reddit, blogs for more clients
│   ├── ai_analyzer.py     # Uses Claude to understand page content
│   └── export.py          # Creates the Excel download
├── requirements.txt       # Python packages we need
├── .env.example           # Template for your API key
├── .gitignore             # Files Git should ignore
└── README.md              # This file!
```

---

## 🔮 Future Roadmap

- [ ] **Space Crawler** — Enter an industry (e.g., "project management") and auto-discover competitors + their clients
- [ ] **CRM Integration** — Push client lists directly into HubSpot/Salesforce
- [ ] **Email Finder** — Find contact info for discovered clients
- [ ] **Change Detection** — Monitor competitor sites for new client additions
- [ ] **Bulk Analysis** — Analyze multiple competitors at once

---

## 🛠 Troubleshooting

| Problem | Fix |
|---------|-----|
| `command not found: python3` | Reinstall Python and make sure "Add to PATH" is checked |
| `ModuleNotFoundError` | Make sure your virtual environment is activated: `source venv/bin/activate` |
| `ANTHROPIC_API_KEY not found` | Check your `.env` file exists and has the key |
| `Rate limit exceeded` | Wait 60 seconds and try again, or add more API credits |
| App won't open in browser | Go to `http://localhost:8501` manually |

---

## 📄 License

MIT — use it however you want!
