"""Uses Claude to intelligently extract client/customer names from text content."""

import json
import anthropic


def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic()


def extract_clients_from_text(text: str, company_name: str) -> list[dict]:
    """Send page text to Claude and ask it to extract client names."""
    client = get_client()

    prompt = f"""You are analyzing a webpage belonging to the company "{company_name}".
Your job is to extract every client, customer, partner, or user company mentioned on this page.

Rules:
- Only extract COMPANY/ORGANIZATION names, not individual people
- Do NOT include "{company_name}" itself
- Do NOT include generic terms like "Fortune 500 companies" unless a specific name is given
- Include companies from: client logos, case studies, testimonials, "trusted by", partner pages, integration pages
- For each client, note WHERE on the page you found them (e.g., "logo section", "case study", "testimonial")

Respond with ONLY a JSON array. Each item should have:
- "name": company name (clean, official name)
- "source_context": where/how it was mentioned (e.g., "listed in trusted-by logo section")
- "confidence": "high" if clearly a client/customer, "medium" if likely a partner/integration, "low" if uncertain

Example:
[
  {{"name": "Airbnb", "source_context": "featured in case study section", "confidence": "high"}},
  {{"name": "Shopify", "source_context": "logo in partners section", "confidence": "medium"}}
]

If no clients are found, return an empty array: []

Here is the webpage content:
---
{text[:15000]}
---"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )
        response_text = message.content[0].text.strip()
        # Clean markdown fences if present
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
            response_text = response_text.rsplit("```", 1)[0]
        return json.loads(response_text)
    except (json.JSONDecodeError, IndexError, anthropic.APIError) as e:
        print(f"AI extraction error: {e}")
        return []


def extract_clients_from_search_results(text: str, company_name: str) -> list[dict]:
    """Extract client mentions from search/news results."""
    client = get_client()

    prompt = f"""You are researching clients/customers of the company "{company_name}".
Below are search results and article snippets from the internet.

Extract every company that is mentioned as a CLIENT, CUSTOMER, or USER of {company_name}'s products/services.

Rules:
- Only extract companies that are clearly USING {company_name}'s product — not just mentioned alongside them
- Phrases like "X uses {company_name}" or "X switched to {company_name}" or "X partnered with {company_name}" are signals
- Do NOT include {company_name} itself
- Do NOT include companies that are competitors, investors, or acquirers of {company_name}

Respond with ONLY a JSON array:
[
  {{"name": "Company Name", "source_context": "brief quote or description of how they were mentioned", "confidence": "high/medium/low"}}
]

If nothing found, return: []

Content to analyze:
---
{text[:15000]}
---"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )
        response_text = message.content[0].text.strip()
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
            response_text = response_text.rsplit("```", 1)[0]
        return json.loads(response_text)
    except (json.JSONDecodeError, IndexError, anthropic.APIError) as e:
        print(f"AI search extraction error: {e}")
        return []


def identify_company_name(url: str, page_text: str) -> str:
    """Use Claude to figure out the company name from a URL and page content."""
    client = get_client()

    prompt = f"""Given this website URL: {url}
And the beginning of its homepage content:
---
{page_text[:3000]}
---

What is the company/product name? Respond with ONLY the name, nothing else.
Example: "Stripe" or "Notion" or "Figma"
"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=50,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text.strip().strip('"').strip("'")
    except anthropic.APIError:
        # Fallback: extract from URL
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        return domain.replace("www.", "").split(".")[0].title()
