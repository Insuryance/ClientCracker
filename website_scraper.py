"""Scrapes a company's website to find pages that mention clients/customers."""

import re
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# Pages most likely to list clients
CLIENT_PAGE_KEYWORDS = [
    "customers", "clients", "case-studies", "case_studies", "casestudies",
    "stories", "testimonials", "partners", "who-uses", "trusted-by",
    "portfolio", "success-stories", "references", "logos", "integrations",
    "about", "wall-of-love",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def normalize_url(url: str) -> str:
    """Ensure URL has a scheme."""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def fetch_page(url: str, timeout: int = 15) -> tuple[str, str]:
    """Fetch a page and return (html_content, final_url). Returns ('', url) on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        return resp.text, resp.url
    except requests.RequestException as e:
        print(f"  ⚠ Could not fetch {url}: {e}")
        return "", url


def extract_text(html: str) -> str:
    """Pull readable text from HTML, stripping nav/footer/script noise."""
    soup = BeautifulSoup(html, "lxml")
    # Remove noise elements
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


def find_client_pages(html: str, base_url: str) -> list[str]:
    """Find internal links that likely lead to client/customer pages."""
    soup = BeautifulSoup(html, "lxml")
    base_domain = urlparse(base_url).netloc
    found = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)

        # Only follow internal links
        if parsed.netloc != base_domain:
            continue

        path_lower = parsed.path.lower()
        link_text = a_tag.get_text(strip=True).lower()

        # Check if the link path or text suggests a client page
        for keyword in CLIENT_PAGE_KEYWORDS:
            if keyword in path_lower or keyword in link_text:
                # Clean the URL (remove fragments)
                clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if clean not in found:
                    found.add(clean)
                break

    return list(found)


def scrape_website(url: str, progress_callback=None) -> dict:
    """
    Main scraping function.
    Returns {
        "company_url": str,
        "pages_scraped": list of {"url": str, "text": str},
        "total_pages": int,
    }
    """
    url = normalize_url(url)
    results = {"company_url": url, "pages_scraped": [], "total_pages": 0}

    # Step 1: Fetch homepage
    if progress_callback:
        progress_callback("Fetching homepage...")
    html, final_url = fetch_page(url)
    if not html:
        return results

    homepage_text = extract_text(html)
    results["pages_scraped"].append({"url": final_url, "text": homepage_text})

    # Step 2: Find client-related pages
    if progress_callback:
        progress_callback("Discovering client-related pages...")
    client_pages = find_client_pages(html, final_url)
    if progress_callback:
        progress_callback(f"Found {len(client_pages)} potential client pages")

    # Step 3: Scrape each client page (limit to 8 to stay reasonable)
    for i, page_url in enumerate(client_pages[:8]):
        if progress_callback:
            progress_callback(f"Scraping page {i+1}/{min(len(client_pages), 8)}: {page_url}")
        time.sleep(1)  # Be polite — don't hammer the server
        page_html, _ = fetch_page(page_url)
        if page_html:
            page_text = extract_text(page_html)
            results["pages_scraped"].append({"url": page_url, "text": page_text})

    results["total_pages"] = len(results["pages_scraped"])
    return results
