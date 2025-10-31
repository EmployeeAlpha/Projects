# ARCHITECTURE.md — NemesisC64 Auditor

## 1. Overview

**NemesisC64 Auditor** is a hybrid **.NET + Python** desktop application.  
It combines the robustness of a WPF front-end with the flexibility of a Python back-end.

[WPF App] ⇄ [Python Bridge] ⇄ [Vendor Engine (Robin)]


Each layer is self-contained but communicates via JSON.  
This allows cross-language integration without shared dependencies or RPC frameworks.

---

## 2. Component Layers

### 2.1 WPF Front-End (`/src/WpfApp/`)
- **Technology:** .NET 8, C#, WPF  
- **Entry Point:** `App.xaml → MainWindow.xaml`
- **Responsibilities:**
  - User Interface
  - Input validation
  - Displaying progress and logs
  - Reading/writing JSON input/output files
  - Rendering local assets (`ascii_footer.txt`, `info_text.html`)
  - Running the Python script (`runner.py`)
  - Optional: Calling InfoWindow (HTML viewer)

---

### 2.2 Python Bridge (`/python/runner.py`)
- **Technology:** Python 3.10+
- **Role:** Executes local scans or invokes the optional **Robin** vendor engine.
- **Responsibilities:**
  - Read an input JSON (passed from WPF)
  - Optionally call `vendor/robin/search.py` or `scrape.py`
  - Generate structured results:
    ```json
    {
      "summary": "string",
      "findings": [{ "type": "...", "detail": "...", "location": "..." }],
      "log_lines": ["..."]
    }
    ```
  - Write both a JSON response and a formatted text report
  - Optionally POST to a webhook (`requests` library)
  - Operate offline if no vendor is available

---

### 2.3 Vendor Engine (`/python/vendor/robin/`)
- **Optional** module copied from your 2025.10.08 `robin-main.zip`.
- **Expected structure:**

robin/
├─ search.py
├─ scrape.py
├─ config.py
├─ llm.py
├─ llm_utils.py
├─ requirements.txt

- **Expected API:**
```python
results = search.search(query="tokens", use_tor=False)

Returns iterable of dictionaries { "type": ..., "title": ..., "url": ... }.

Benefits:

Modular — replace or upgrade vendor logic without touching the UI.

Sandboxable — Python code can run in isolated virtual environments.

3. Data Flow Diagram

┌────────────────────────────────────┐
│        MainWindow.xaml.cs          │
│   - Gathers user inputs            │
│   - Builds AuditorRequest JSON     │
│   - Calls: python runner.py        │
└────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────┐
│           runner.py                │
│   - Reads input JSON               │
│   - Runs vendor engine             │
│   - Writes output JSON             │
│   - Saves text report              │
│   - POSTs to webhook (optional)    │
└────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────┐
│           WPF UI Update            │
│   - Reads output JSON              │
│   - Updates Findings list          │
│   - Displays log + summary         │
│   - Loads ascii_footer.txt         │
└────────────────────────────────────┘

4. Folder Role Summary
Folder	Purpose
/src/WpfApp	C# WPF application
/python	Python bridge code
/python/vendor/robin	Optional engine (copied externally)
/assets	Static visuals: ASCII footer, HTML info
/reports	Runtime text reports
/logs	JSON input/output and logs
/docs	Documentation for developers
/scripts	PowerShell helpers
5. Communication Protocol

Type: JSON over file system (no sockets or RPC).
Direction: One-way request → response.

Advantages:

Reliable, easy to debug.

Language-agnostic.

Logs persist automatically.

Potential future upgrades:

gRPC or named pipe for faster live feedback.

WebSocket bridge for interactive dashboards.

6. Key Interfaces
C# → Python

Uses System.Diagnostics.Process

Executes one of:

py -3, py, python, or python3

Redirects stdout/stderr

Awaits process completion

Python → C#

Writes an output JSON file

(Optional) prints result to stdout

Returns exit code 0 on success

7. Future Extensibility
Area	Enhancement Ideas
UI	Dark/light theme switcher, drag-drop folder scan
Runner	Async streaming logs via socket
Vendor	LLM-based classification or summarization
Reports	Export to PDF or HTML
Security	Signed reports, checksums, encrypted payloads
Automation	Scheduled background audits
8. Architectural Philosophy

“Keep bridges simple. Let the languages do what they do best.”

C# handles interface, UX, and system integration.

Python handles logic, data processing, and extensibility.

Both sides remain fully replaceable.

© 2025 Lexmilian de Mello / NemesisC64
"Auditing silence, searching traces…"


---

When saved, say **“done.”**  
Then I’ll give you the next doc — `/docs/PAYLOAD_SCHEMA.md`, which details the JSON contract between WPF and Python.
