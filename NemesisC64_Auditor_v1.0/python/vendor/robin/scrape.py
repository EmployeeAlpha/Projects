"""
scrape.py — Helper utilities for Robin engine.
You can import these from search.py, e.g.:
    from .scrape import http_get, result_item, pretty
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional, Tuple

# Try to use 'requests' if installed; otherwise keep an offline-safe stub.
try:
    import requests  # type: ignore
except Exception:
    requests = None  # sentinel: allows module import to succeed without the dep


DEFAULT_TIMEOUT = 15
DEFAULT_UA = (
    "NemesisC64-Auditor/1.0 (+https://example.local) "
    "Python-requests-compatible"
)


def _build_proxies(use_tor: bool) -> Optional[Dict[str, str]]:
    if not use_tor:
        return None
    # Requires: pip install "requests[socks]" and a local Tor (SOCKS) at 127.0.0.1:9050
    return {
        "http": "socks5h://127.0.0.1:9050",
        "https": "socks5h://127.0.0.1:9050",
    }


def http_get(
    url: str,
    *,
    timeout: int = DEFAULT_TIMEOUT,
    use_tor: bool = False,
    headers: Optional[Dict[str, str]] = None,
    return_both: bool = False,
) -> Dict[str, Any]:
    """
    HTTP GET helper.

    - If 'requests' is available, performs a live network call.
    - If not, returns an offline stub payload (no exception).
    - Tries JSON first; if not JSON, returns text body.

    Args:
        url: Target URL or API endpoint.
        timeout: Socket timeout in seconds.
        use_tor: If True, route via local Tor SOCKS (127.0.0.1:9050).
        headers: Extra HTTP headers to merge with the default UA.
        return_both: If True, include both 'json' (if parsed) and 'text' in result.

    Returns (dict):
        {
          "ok": bool,
          "status_code": int | None,
          "url": str,
          "via": "live" | "offline",
          "headers": {...},             # only for live
          "json": {...} | None,
          "text": "..." | None,
          "error": "..." | None
        }
    """
    # Offline-safe fallback if requests isn’t available
    if requests is None:
        return {
            "ok": True,
            "status_code": None,
            "url": url,
            "via": "offline",
            "headers": None,
            "json": None,
            "text": None,
            "error": "requests-not-installed (offline stub)",
        }

    # Live path
    _headers = {"User-Agent": DEFAULT_UA}
    if headers:
        _headers.update(headers)

    proxies = _build_proxies(use_tor)

    try:
        resp = requests.get(url, headers=_headers, proxies=proxies, timeout=timeout)
        status = resp.status_code
        ok = 200 <= status < 300

        parsed_json = None
        text_body = None

        # Attempt JSON parse; fall back to text
        try:
            parsed_json = resp.json()
        except Exception:
            text_body = resp.text

        # If caller wants both, ensure both keys exist (json/text)
        if return_both and text_body is None:
            # If JSON succeeded, still provide text for caller convenience
            text_body = resp.text
        if return_both and parsed_json is None:
            # If JSON failed, still provide a JSON key set to None
            parsed_json = None

        return {
            "ok": ok,
            "status_code": status,
            "url": resp.url,
            "via": "live",
            "headers": dict(resp.headers),
            "json": parsed_json,
            "text": text_body if (return_both or parsed_json is None) else None,
            "error": None if ok else f"http_error_{status}",
        }

    except Exception as e:
        return {
            "ok": False,
            "status_code": None,
            "url": url,
            "via": "live",
            "headers": None,
            "json": None,
            "text": None,
            "error": str(e),
        }


def result_item(*, type_: str, detail: str, location: str) -> Dict[str, str]:
    """Small helper to build a normalized result dict."""
    return {"type": type_, "detail": detail, "location": location}


def pretty(obj: Any) -> str:
    """Pretty JSON for logs/diagnostics."""
    return json.dumps(obj, ensure_ascii=False, indent=2)
