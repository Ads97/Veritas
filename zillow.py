import requests
from Kamthe.firecrawl_scraper import scrape_url_simple
from Kamthe.GoogleSearch import OPENROUTER_API_URL, OPENROUTER_API_KEY
import json 

ZILLOW_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {
            "type": "string",
            "description": "One line reasoning on whether the url has a monthly rent amount in it."
        },
        "monthly_rent_usd": {
            "type": "number",
            "description": "The monthly rent in USD as a plain number (no commas, symbols). If a range is shown, use the lowest currently available advertised monthly rent. if there's no monthly rent mentioned on the page, enter 0. "
        },
    },
    "required": ["sourcreasoninge_title", "monthly_rent_usd"],
    "additionalProperties": False
}


def analyze_zillow(search_results):
    """
    Analyze a list of Zillow search results and extract the monthly rent from each listing page.
    
    Parameters
    ----------
    search_results : list[dict]
        Each dict should look like:
        {
            "title": "...",
            "link": "https://www.zillow.com/...",
            "snippet": "..."  # optional
        }
    
    Returns
    -------
    list[dict]
        List of parsed JSON objects (one per input result) following ZILLOW_OUTPUT_SCHEMA.
    """
    outputs = []

    for sr in search_results:
        print(f"🏠 Analyzing Rentals: {sr.get('title') or sr.get('link')}")

        # Scrape the Zillow URL content
        scraped_content = scrape_url_simple(sr["link"])

        # New analysis prompt (Zillow-focused)
        prompt = f"""
You are a meticulous data extractor. Your job is to read the provided Zillow listing page content and return ONLY the monthly rent as a number in USD.

Follow these rules carefully:
- Target the listing's advertised rent for currently available units.
- If a range is displayed (e.g., "$2,700–$3,100/mo"), return the LOWEST advertised monthly rent.
- Ignore any of the following: Zestimate, mortgage payments, HOA fees, price history, purchase price, sold price, deposit amounts, application fees, pet fees, parking fees, or any non-monthly amounts unless they’re the only rent shown.
- If the rent is presented weekly or daily (rare on Zillow), convert to monthly using:
  - weekly → monthly: multiply by 4.345
  - daily → monthly: multiply by 30.437
  Round to the nearest whole dollar after conversion.
- If multiple floor plans are shown, prefer the lowest monthly rent among units that are marked as available now (or “available” soon). If availability is unclear, choose the lowest listed monthly rent.
- Extract the exact text snippet where the rent is stated for provenance.
- Return strict JSON following the provided JSON schema. DO NOT include any commentary.

Source metadata to include in the JSON:
- source_title: the page title we searched for
- source_url: the URL of the page being analyzed

Zillow Search Result:
Title: {sr.get('title', '')}
URL: {sr['link']}
Snippet: {sr.get('snippet', '')}

Scraped Content (first 3,000 chars):
{scraped_content[:3000]}...
        """.strip()

        # Make API request
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "openai/gpt-4o",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 400,
            "temperature": 0.2,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "zillow_rent_extraction",
                    "schema": ZILLOW_OUTPUT_SCHEMA
                }
            }
        }

        response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
        response.raise_for_status()
        response_data = response.json()

        # The model returns a JSON string in message.content that conforms to ZILLOW_OUTPUT_SCHEMA
        content = response_data["choices"][0]["message"]["content"]

        # Optionally, ensure the source fields are present/overridden from our inputs
        # (Some models adhere strictly, others may omit; we can defensively patch them here.)
        try:
            parsed = json.loads(content)
        except Exception:
            # If the provider already returns a dict-like object, just use it directly
            parsed = content

        parsed.setdefault("source_title", sr.get("title", ""))
        parsed.setdefault("source_url", sr["link"])

        outputs.append(parsed)

    for output in outputs:
        if output['monthly_rent_usd']:
            return output['monthly_rent_usd']
    
    return None
