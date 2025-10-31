#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NemesisC64 Auditor - Python bridge (runner.py)

This script is invoked by the WPF app. It:
  1) Reads an input JSON file (path via --input)
  2) Optionally uses the embedded 'vendor/robin' engine (if present)
  3) Writes a result JSON (path via --output) with:
        { "summary": str, "findings": [{type, detail, location}, ...], "log_lines": [ ... ] }
  4) Emits a human-readable report into /reports/
  5) If a webhook is provided, POSTs the JSON result there (best-effort)
"""

import argparse
import json
import sys
import os
import datetime
import traceback
import uuid

# --- Resolve app base (bin folder) and project-relative folders ---
APP_BASE = os.path.abspath(os.path.dirname(__file__))             # .../python
PROJECT_BASE = os.path.abspath(os.path.join(APP_BASE, os.pardir)) # .../
REPORTS_DIR = os.path.join(PROJECT_BASE, "reports")
LOGS_DIR = os.path.join(PROJECT_BASE, "logs")
ASSETS_DIR = os.path.join(PROJECT_BASE, "assets")
VENDOR_ROBIN_DIR = os.path.join(APP_BASE, "vendor", "robin")

os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# --- Optional requests import (for webhook) ---
try:
    import requests  # type: ignore
    _HAS_REQUESTS = True
except Exception:
    _HAS_REQUESTS = False


def _now_utc_iso():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _safe_read_text(path, fallback=""):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return fallback


def load_input_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_output_json(path: str, payload: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def write_text_report(findings, summary_text, log_lines) -> str:
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fn = f"auditor_report_{ts}.txt"
    report_path = os.path.join(REPORTS_DIR, fn)

    lines = []
    lines.append("NemesisC64 Auditor — Report")
    lines.append(f"Generated at: {datetime.datetime.now().isoformat(sep=' ', timespec='seconds')}")
    lines.append("")
    if summary_text:
        lines.append("=== SUMMARY ===")
        lines.append(summary_text)
        lines.append("")
    lines.append("=== FINDINGS ===")
    if not findings:
        lines.append("(no findings)")
    else:
        for i, f in enumerate(findings, 1):
            f_type = f.get("type") or "unknown"
            f_det = f.get("detail") or ""
            f_loc = f.get("location") or ""
            lines.append(f"{i:03d}. [{f_type}] {f_det}   @ {f_loc}")
    lines.append("")
    if log_lines:
        lines.append("=== LOG ===")
        lines.extend(log_lines)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return report_path


def try_post_webhook(url: str, secret: str | None, payload: dict, log_lines: list[str]):
    if not url:
        return
    if not _HAS_REQUESTS:
        log_lines.append("requests not installed; skipping webhook POST.")
        return
    try:
        headers = {"Content-Type": "application/json"}
        if secret:
            headers["X-Auditor-Secret"] = secret
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        log_lines.append(f"Webhook POST -> {url} [status={r.status_code}]")
    except Exception as ex:
        log_lines.append(f"Webhook POST failed: {ex!r}")


def run_vendor_robin(query: str | None, use_tor: bool, log_lines: list[str]):
    """
    Attempt to use the embedded vendor/robin engine.
    We prefer robin/search.py (and/or scrape.py) if available.
    Returns a tuple: (summary:str, findings:list[dict], extra_logs:list[str])
    """
    # Make both the robin dir and its parent importable
    sys.path.insert(0, VENDOR_ROBIN_DIR)                    # .../python/vendor/robin
    sys.path.insert(0, os.path.join(APP_BASE, "vendor"))    # .../python/vendor

    findings: list[dict] = []
    summary = ""
    extra = []

    try:
        # Try flat-module imports first (robin/search.py directly)
        search = None
        scrape = None

        try:
            import search as _search  # type: ignore
            search = _search
        except Exception as e:
            log_lines.append(f"flat import 'search' failed: {e!r}")

        try:
            import scrape as _scrape  # type: ignore
            scrape = _scrape
        except Exception as e:
            log_lines.append(f"flat import 'scrape' failed: {e!r}")

        # If flat import failed, try package-style imports (robin/search.py with __init__.py)
        if search is None:
            try:
                import robin.search as _search  # type: ignore
                search = _search
            except Exception as e:
                log_lines.append(f"package import 'robin.search' failed: {e!r}")

        if scrape is None:
            try:
                import robin.scrape as _scrape  # type: ignore
                scrape = _scrape
            except Exception as e:
                log_lines.append(f"package import 'robin.scrape' failed: {e!r}")

        # === Diagnostics: which module was imported ===
        if search is not None:
            src_name = getattr(search, "__name__", "?")
            src_file = getattr(search, "__file__", "?")
            log_lines.append(f"Robin import OK: {src_name} @ {src_file}")
        else:
            log_lines.append("Robin import FAILED: no 'search' module available")

        if scrape is not None:
            log_lines.append(f"Robin scrape module: {getattr(scrape,'__name__','?')} @ {getattr(scrape,'__file__','?')}")

        # Verify entry point presence
        entry = getattr(search, "search", None) if search else None
        if entry is None or not callable(entry):
            log_lines.append("Robin entry point missing: expected callable 'search.search(query, use_tor)'.")
        else:
            log_lines.append("Robin entry point OK: search.search(query, use_tor) found.")

        if not query:
            query = "suspicious credentials OR tokens OR invoices OR passwords"

        # Minimal example: call a safe search flow if available
        if entry is not None:
            log_lines.append("Calling vendor.robin.search.search() …")
            try:
                t0 = datetime.datetime.now()
                results = entry(query=query, use_tor=use_tor)  # type: ignore
                dt = (datetime.datetime.now() - t0).total_seconds()
                log_lines.append(f"Robin search() returned {len(results or [])} item(s) in {dt:.2f}s")
            except Exception as ex:
                log_lines.append(f"Robin search() raised: {ex!r}")
                raise

            count = 0
            for item in results or []:
                # Heuristic normalization
                ftype = str(item.get("type", "result"))
                detail = str(item.get("title", item.get("detail", "")))
                loc = str(item.get("url", item.get("location", "")))
                findings.append({"type": ftype, "detail": detail, "location": loc})
                count += 1
                if count >= 50:  # keep it tidy
                    break

            summary = f"Robin search completed. Collected {len(findings)} result(s)."
        else:
            summary = "vendor/robin/search.py not available; skipping Robin search."

    except Exception as ex:
        tb = traceback.format_exc(limit=2)
        log_lines.append(f"Robin exception: {ex!r}")
        log_lines.append(tb)

    return summary, findings, extra


def main():
    parser = argparse.ArgumentParser(description="NemesisC64 Auditor runner")
    parser.add_argument("--input", required=True, help="Path to input JSON")
    parser.add_argument("--output", required=True, help="Path to output JSON")
    args = parser.parse_args()

    log_lines: list[str] = []
    log_lines.append(f"runner.py start: { _now_utc_iso() }")
    log_lines.append(f"APP_BASE={APP_BASE}")
    log_lines.append(f"PROJECT_BASE={PROJECT_BASE}")

    try:
        req = load_input_json(args.input)
    except Exception as ex:
        err = f"Failed to read input JSON: {ex!r}"
        log_lines.append(err)
        out = {
            "summary": "Input error.",
            "findings": [],
            "log_lines": log_lines,
        }
        write_output_json(args.output, out)
        return 1

    # Extract request fields (keep keys aligned with the WPF contracts)
    query = (req.get("query") or "").strip() or None
    use_tor = bool(req.get("use_tor", False))
    webhook_url = (req.get("webhook_url") or "").strip()
    webhook_secret = (req.get("webhook_secret") or "").strip() or None
    email_to = (req.get("email_to") or "").strip()
    email_subject = (req.get("email_subject") or "").strip() or "NemesisC64 Auditor Report"
    attach_report = bool(req.get("attach_report", False))

    log_lines.append(f"Request: query={'<empty>' if not query else query!r}, use_tor={use_tor}, webhook={'yes' if webhook_url else 'no'}, email={'yes' if email_to else 'no'}, attach={attach_report}")

    vendor_present = os.path.isdir(VENDOR_ROBIN_DIR)
    log_lines.append(f"vendor/robin present: {vendor_present}")

    summary = ""
    findings: list[dict] = []

    if vendor_present:
        s, f, extra = run_vendor_robin(query, use_tor, log_lines)
        if s:
            summary = s
        findings.extend(f)
        log_lines.extend(extra)
    else:
        # No vendor found; produce a harmless placeholder so UI flow can be tested
        summary = "Robin vendor engine not found. Performed a local stub scan."
        findings = []

    # Generate a lightweight summary if still empty
    if not summary:
        summary = f"Scan complete at {datetime.datetime.now().isoformat(sep=' ', timespec='seconds')} with {len(findings)} finding(s)."

    # Create/save a plain-text report
    report_path = write_text_report(findings, summary, log_lines)
    log_lines.append(f"Report saved: {report_path}")

    # Build final payload
    result_payload = {
        "summary": summary,
        "findings": findings,
        "log_lines": log_lines,
    }

    # Best-effort webhook
    if webhook_url:
        try_post_webhook(webhook_url, webhook_secret, result_payload, log_lines)

    # NOTE: Email delivery is intentionally not implemented here.
    # Rationale: requires SMTP creds or OS-specific mail APIs.
    # The WPF app already allows saving/exporting reports; hooking SMTP can be added later.

    # Write output JSON
    try:
        write_output_json(args.output, result_payload)
    except Exception as ex:
        # As a last resort, write an emergency file in logs
        emergency = os.path.join(LOGS_DIR, f"runner_emergency_{uuid.uuid4().hex}.json")
        with open(emergency, "w", encoding="utf-8") as f:
            json.dump(result_payload, f, ensure_ascii=False, indent=2)
        print(f"Failed to write output {args.output}: {ex!r}. Emergency dump: {emergency}", file=sys.stderr)
        return 2

    # Also mirror the final payload back to stdout for quick debugging
    print(json.dumps(result_payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit as se:
        raise
    except Exception as e:
        # If something catastrophic happens, emit a minimal JSON so the app can show it
        fallback = {
            "summary": f"runner.py crashed: {e!r}",
            "findings": [],
            "log_lines": [traceback.format_exc(limit=2)],
        }
        try:
            # Try to print to stdout so the app sees something
            print(json.dumps(fallback, ensure_ascii=False, indent=2))
        except Exception:
            pass
        sys.exit(99)
