"""Searches news, Reddit, and blogs to find clients NOT listed on the company website."""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

# Search queries designed to surface client relationships
SEARCH_TEMPLATES = [
    '"{company}" customers case study',
    '"{company}" "powered by" OR "built with" OR "uses"',
    '"{company}" client list OR customer stories',
    '"{company}" testimonial OR review enterprise',
    'site:reddit.com "{company}" using OR switched OR migrated',
    '"{company}" partnership announcement',
]


def build_search_queries(company_name: str) -> list[str]:
    """Generate search queries tailored to finding clients."""
    return [t.format(company=company_name) for t in SEARCH_TEMPLATES]


def search_duckduckgo(query: str, max_results: int = 8) -> list[dict]:
    """
    Search DuckDuckGo HTML version (no API key needed).
    Returns list of {"title": str, "url": str, "snippet": str}.
    """
    url = "https://html.duckduckgo.com/html/"
    try:
        resp = requests.post(url, data={"q": query}, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  ⚠ Search failed for '{query}': {e}")
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    results = []

    for result_div in soup.select(".result")[:max_results]:
        title_tag = result_div.select_one(".result__title a")
        snippet_tag = result_div.select_one(".result__snippet")
        if title_tag:
            results.append({
                "title": title_tag.get_text(strip=True),
                "url": title_tag.get("href", ""),
                "snippet": snippet_tag.get_text(strip=True) if snippet_tag else "",
            })

    return results


def fetch_article_text(url: str) -> str:
    """Fetch and extract readable text from an article URL."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        return text[:8000]  # Cap length
    except requests.RequestException:
        return ""


def enrich_from_web(company_name: str, progress_callback=None) -> dict:
    """
    Search multiple sources for additional client information.
    Returns {
        "queries_run": int,
        "results_found": int,
        "search_results": list of {"query": str, "results": list},
        "article_texts": list of {"url": str, "text": str},
    }
    """
    queries = build_search_queries(company_name)
    all_search_results = []
    all_urls_seen = set()
    article_texts = []

    for i, query in enumerate(queries):
        if progress_callback:
            progress_callback(f"Searching: {query[:60]}...")

        results = search_duckduckgo(query)
        all_search_results.append({"query": query, "results": results})

        # Fetch top articles for deeper analysis (2 per query, skip duplicates)
        fetched = 0
        for r in results:
            if fetched >= 2:
                break
            article_url = r["url"]
            if article_url in all_urls_seen or not article_url.startswith("http"):
                continue
            all_urls_seen.add(article_url)

            if progress_callback:
                progress_callback(f"Reading article: {r['title'][:50]}...")
            text = fetch_article_text(article_url)
            if text:
                article_texts.append({"url": article_url, "text": text})
                fetched += 1

    total_results = sum(len(sr["results"]) for sr in all_search_results)

    return {
        "queries_run": len(queries),
        "results_found": total_results,
        "search_results": all_search_results,
        "article_texts": article_texts,
    }
