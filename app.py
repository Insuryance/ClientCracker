"""Client Hunter — Find any company's clients from their website + the internet."""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Page config ──
st.set_page_config(
    page_title="Client Hunter",
    page_icon="🎯",
    layout="wide",
)

# ── Check API key ──
if not os.getenv("ANTHROPIC_API_KEY"):
    st.error(
        "🔑 **Anthropic API key not found!**\n\n"
        "1. Copy `.env.example` to `.env`\n"
        "2. Paste your API key from [console.anthropic.com](https://console.anthropic.com)\n"
        "3. Restart the app"
    )
    st.stop()

from src.website_scraper import scrape_website
from src.web_enricher import enrich_from_web
from src.ai_analyzer import extract_clients_from_text, extract_clients_from_search_results, identify_company_name
from src.export import create_excel

# ── Custom CSS ──
st.markdown("""
<style>
    .block-container { max-width: 900px; padding-top: 2rem; }
    .stProgress > div > div > div { background-color: #2D5F8A; }
    div[data-testid="stMetric"] {
        background: #f8f9fa; border-radius: 8px;
        padding: 12px 16px; border-left: 4px solid #2D5F8A;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ──
st.title("🎯 Client Hunter")
st.caption("Enter a competitor's website → get their full client list → download as Excel")

# ── Input ──
col1, col2 = st.columns([3, 1])
with col1:
    url = st.text_input(
        "Company website URL",
        placeholder="e.g. https://www.notion.so",
        label_visibility="collapsed",
    )
with col2:
    hunt = st.button("🔍 Hunt for Clients", type="primary", use_container_width=True)

st.divider()

# ── Main logic ──
if hunt and url:
    all_clients = {}  # name -> client dict (deduplication)

    status = st.status("Starting client hunt...", expanded=True)

    # ─── Phase 1: Scrape website ───
    with status:
        st.write("**Phase 1/3 — Scraping the company website**")
        progress = st.progress(0, text="Preparing...")

        def website_progress(msg):
            progress.progress(30, text=msg)

        scrape_data = scrape_website(url, progress_callback=website_progress)
        pages = scrape_data["pages_scraped"]

        if not pages:
            st.error("Could not access this website. Check the URL and try again.")
            st.stop()

        # Identify company name from homepage
        st.write("Identifying company name...")
        company_name = identify_company_name(url, pages[0]["text"])
        st.write(f"Company identified: **{company_name}**")

        # Send each scraped page to Claude for extraction
        st.write(f"Analyzing {len(pages)} pages with AI...")
        progress.progress(50, text="AI is reading the pages...")

        for page in pages:
            clients = extract_clients_from_text(page["text"], company_name)
            for c in clients:
                name = c["name"].strip()
                if name.lower() not in all_clients:
                    all_clients[name.lower()] = {
                        "name": name,
                        "confidence": c.get("confidence", "medium"),
                        "source_context": c.get("source_context", ""),
                        "source_type": "🌐 Website",
                        "source_url": page["url"],
                    }

        progress.progress(100, text=f"Found {len(all_clients)} clients from website")
        st.write(f"✅ Found **{len(all_clients)}** clients from the website")

    # ─── Phase 2: Web enrichment ───
    with status:
        st.write("**Phase 2/3 — Searching news, Reddit, and blogs**")
        progress2 = st.progress(0, text="Searching the internet...")

        def web_progress(msg):
            progress2.progress(50, text=msg)

        enrichment = enrich_from_web(company_name, progress_callback=web_progress)

        # Build combined text from search snippets + articles
        snippet_texts = []
        for sr in enrichment["search_results"]:
            for r in sr["results"]:
                snippet_texts.append(f"Title: {r['title']}\nSnippet: {r['snippet']}\nURL: {r['url']}")

        article_texts = []
        for art in enrichment["article_texts"]:
            article_texts.append(f"Article from {art['url']}:\n{art['text']}")

        combined_text = "\n\n---\n\n".join(snippet_texts + article_texts)

        if combined_text.strip():
            st.write("AI is analyzing search results...")
            web_clients = extract_clients_from_search_results(combined_text, company_name)

            new_count = 0
            for c in web_clients:
                name = c["name"].strip()
                if name.lower() not in all_clients:
                    all_clients[name.lower()] = {
                        "name": name,
                        "confidence": c.get("confidence", "low"),
                        "source_context": c.get("source_context", ""),
                        "source_type": "📰 Web/News",
                    }
                    new_count += 1

            progress2.progress(100, text=f"Found {new_count} additional clients from the web")
            st.write(f"✅ Found **{new_count}** additional clients from the web")
        else:
            progress2.progress(100, text="No additional results found")
            st.write("No additional sources found")

    # ─── Phase 3: Compile results ───
    with status:
        st.write("**Phase 3/3 — Compiling results**")

    status.update(label=f"Hunt complete! Found {len(all_clients)} clients.", state="complete")

    # ── Results display ──
    st.subheader(f"📊 Results for {company_name}")

    clients_list = sorted(all_clients.values(), key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x["confidence"], 3))

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Clients", len(clients_list))
    m2.metric("High Confidence", sum(1 for c in clients_list if c["confidence"] == "high"))
    m3.metric("From Website", sum(1 for c in clients_list if "Website" in c["source_type"]))
    m4.metric("From Web/News", sum(1 for c in clients_list if "Web" in c["source_type"]))

    # Client table
    st.dataframe(
        [
            {
                "Client": c["name"],
                "Confidence": c["confidence"].upper(),
                "Source": c["source_type"],
                "Details": c["source_context"],
            }
            for c in clients_list
        ],
        use_container_width=True,
        hide_index=True,
    )

    # ── Excel download ──
    excel_buffer = create_excel(clients_list, company_name)

    st.download_button(
        label="📥 Download Excel Report",
        data=excel_buffer,
        file_name=f"client_hunter_{company_name.lower().replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
    )

elif hunt and not url:
    st.warning("Please enter a website URL first.")

# ── Footer ──
st.divider()
st.caption(
    "**How it works:** Scrapes the target website for client pages (case studies, testimonials, logos) → "
    "Searches news, Reddit, and blogs for unlisted clients → Uses AI to extract company names → "
    "Deduplicates and exports to Excel."
)
