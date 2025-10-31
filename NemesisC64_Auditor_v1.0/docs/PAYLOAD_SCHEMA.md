# PAYLOAD_SCHEMA.md — NemesisC64 Auditor

This document specifies the exact **JSON structures** exchanged between the WPF application and the Python bridge.

---

## 1. Overview

Communication is entirely file-based using UTF-8 JSON.  
Two files are passed per run:

- **Input file:** `logs/request_YYYYMMDD_HHmmss.json`
- **Output file:** `logs/response_YYYYMMDD_HHmmss.json`

The WPF app:
1. Builds the input payload (`AuditorRequest`)
2. Runs `python/runner.py --input <path> --output <path>`
3. Reads the resulting output (`AuditorResult`)

---

## 2. AuditorRequest

Sent **from C# → Python**.

```jsonc
{
  "query": "passwords OR tokens OR invoices",
  "use_tor": true,
  "webhook_url": "https://hooks.example.com/abc123",
  "webhook_secret": "optional-shared-secret",
  "email_to": "recipient@example.com",
  "email_subject": "NemesisC64 Auditor Report",
  "attach_report": true
}

Field Reference
Field	Type	Description
query	string / null	Search keywords or logical query string. If empty, Python may substitute a default.
use_tor	bool	Hint for vendor modules that prefer privacy routing.
webhook_url	string / null	Optional URL for POST delivery of JSON results.
webhook_secret	string / null	Optional authentication header sent as X-Auditor-Secret.
email_to	string / null	Placeholder for future SMTP integration (not implemented).
email_subject	string / null	Custom subject for future email feature.
attach_report	bool	If true, report path will be included in the Python log for attachment by external automation.
3. AuditorResult

Returned from Python → C#.

{
  "summary": "Robin search completed. Collected 12 result(s).",
  "findings": [
    {
      "type": "credential",
      "detail": "Found token in config.json",
      "location": "C:\\Projects\\app\\config.json"
    },
    {
      "type": "document",
      "detail": "Detected invoice.pdf",
      "location": "D:\\Docs\\invoice.pdf"
    }
  ],
  "log_lines": [
    "runner.py start: 2025-10-08T14:22:11Z",
    "APP_BASE=python",
    "vendor/robin present: True",
    "Report saved: reports/auditor_report_20251008_142211.txt"
  ]
}

Field Reference
Field	Type	Description
summary	string	Human-readable summary of the scan.
findings	array<object>	List of identified results. Each entry must have type, detail, and location.
log_lines	array<string>	Ordered diagnostic messages for the user interface.

4. Error Handling Payloads

If an error occurs before a proper result can be generated, runner.py outputs a fallback structure:

{
  "summary": "runner.py crashed: FileNotFoundError(...)",
  "findings": [],
  "log_lines": [
    "Traceback (most recent call last): ...",
    "File 'runner.py', line 300, in main"
  ]
}

The C# application simply displays this in the Live Output area and sets status text to “Audit failed.”

5. Report Text Format

Each run also produces /reports/auditor_report_YYYYMMDD_HHmmss.txt with:

NemesisC64 Auditor — Report
Generated at: 2025-10-08 14:22:11

=== SUMMARY ===
Robin search completed. Collected 12 result(s).

=== FINDINGS ===
001. [credential] Found token in config.json   @ C:\Projects\app\config.json
002. [document]   Detected invoice.pdf         @ D:\Docs\invoice.pdf

=== LOG ===
runner.py start: 2025-10-08T14:22:11Z
vendor/robin present: True
Report saved: reports/auditor_report_20251008_142211.txt

6. Data Type Validation Rules
Property	Must Exist	Type	Notes
summary	✓	string	May not exceed 5 KB
findings	✓	array	Zero or more result objects
log_lines	✓	array	Ordered, short strings (≤1 KB each)

Each finding must include:

type (string)

detail (string)

location (string)

7. Compatibility & Versioning

The schema is version-agnostic.
Any field additions should maintain backward compatibility.
Future revisions may introduce an optional schema_version key in both request and response.

Maintainer: Lexmilian de Mello
Authorship: NemesisC64
Last Updated: 2025-10-08


---

When you’ve saved it, say **“done.”**  
Next, we’ll continue with `/docs/SECURITY.md` (privacy, safety, and compliance guidelines).

