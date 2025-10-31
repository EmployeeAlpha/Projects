from .scrape import http_get, result_item, pretty
import os
import time
import urllib.parse
from typing import List, Dict, Any

# Live mode toggle: default OFF for deterministic tests.
# Turn on by setting environment variable: NCA_LIVE=1
_LIVE_DEFAULT = os.getenv("NCA_LIVE", "0").strip().lower() in ("1", "true", "on", "yes")

def _ddg_url(query: str) -> str:
    q = urllib.parse.quote_plus(query)
    # DuckDuckGo Instant Answer API (no key). Good for basic connectivity checks.
    return f"https://api.duckduckgo.com/?q={q}&format=json&no_html=1&no_redirect=1&skip_disambig=1"

def _parse_ddg(data: Dict[str, Any], max_topics: int = 5) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    if not isinstance(data, dict):
        return out
    # Prefer Abstract if present
    abstract = data.get("AbstractText")
    if abstract:
        out.append(result_item(
            type_="abstract",
            detail=abstract,
            location=data.get("AbstractURL") or "N/A",
        ))
        return out
    # Otherwise show a few related topics
    topics = data.get("RelatedTopics") or []
    for item in topics[:max_topics]:
        # Some items are nested with a "Topics" list; handle both shapes.
        if "Text" in item or "FirstURL" in item:
            text = item.get("Text") or "(no text)"
            url  = item.get("FirstURL") or "(no URL)"
            out.append(result_item(type_="topic", detail=text, location=url))
        elif "Topics" in item and isinstance(item["Topics"], list):
            for sub in item["Topics"][:max_topics]:
                text = sub.get("Text") or "(no text)"
                url  = sub.get("FirstURL") or "(no URL)"
                out.append(result_item(type_="topic", detail=text, location=url))
                if len(out) >= max_topics:
                    break
        if len(out) >= max_topics:
            break
    return out

def search(query: str = "", use_tor: bool = False) -> List[Dict[str, str]]:
    """
    Main entry point for the NemesisC64 Auditor's Robin engine.

    Returns a list of normalized dicts with keys:
      - type
      - detail
      - location
    """
    results: List[Dict[str, str]] = []
    start = time.time()

    # Passive mode if no query
    if not query:
        results.append(result_item(
            type_="notice",
            detail="No query provided — Robin ran in passive mode.",
            location="N/A",
        ))
        print("network_mode=offline (no-query)")
        print(f"Robin search() returned {len(results)} item(s) in {round(time.time()-start, 2)}s")
        return results

    # Decide whether to attempt live HTTP
    live_requested = _LIVE_DEFAULT  # flipped via env var
    # We’ll still be safe: http_get will fall back if requests isn’t available.

    if live_requested:
        # 1) Attempt a live call
        url = _ddg_url(query)
        resp = http_get(url, use_tor=use_tor, return_both=False)
        via = resp.get("via")  # "live" or "offline"
        ok  = bool(resp.get("ok"))

        if via == "live" and ok:
            data = resp.get("json")
            parsed = _parse_ddg(data) if isinstance(data, dict) else []
            if parsed:
                results.extend(parsed)
            else:
                # Live worked but nothing meaningful found — still return a success note
                results.append(result_item(
                    type_="example",
                    detail=f"Fetched live data for '{query}'",
                    location=resp.get("url") or "N/A",
                ))
            print("network_mode=live")
        else:
            # Live path failed or was offline — fal
