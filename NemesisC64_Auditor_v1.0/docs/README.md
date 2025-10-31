# NemesisC64 Auditor — v1.0

A desktop **WPF (.NET 8)** app with a **Python bridge** that orchestrates quick investigative searches/collections.  
The UI invokes `python/runner.py`, which optionally leverages an embedded engine located at `python/vendor/robin/`.

---

## Features

- **One-click audit** with live log output and progress bar
- **Findings grid** (Type / Detail / Location)
- **Report export** to `/reports/` (timestamped `.txt`)
- **Webhook delivery** (optional; JSON POST with optional secret header)
- **Email placeholders** (future SMTP integration)
- **Info window** rendering `/assets/info_text.html`
- **Theming** via `App.xaml` resource dictionary
- **Tor hint** flag (forwarded to vendor engine when supported)

---

## Repository Layout

NemesisC64_Auditor_v1.0/
├─ NemesisC64.Auditor.sln
├─ /src/WpfApp/ # WPF application
│ ├─ App.xaml(.cs)
│ ├─ MainWindow.xaml(.cs)
│ ├─ InfoWindow.xaml(.cs)
│ └─ /Properties/AssemblyInfo.cs
├─ /python/ # Python bridge + vendor engine
│ ├─ runner.py
│ └─ /vendor/robin/ # (COPY from 2025.10.08 robin-main.zip)
├─ /assets/
│ ├─ ascii_footer.txt
│ └─ info_text.html
├─ /reports/ # generated at runtime
├─ /logs/ # runtime JSON + stdout/stderr
└─ /docs/
├─ README.md
├─ DEVELOPER.md
├─ ARCHITECTURE.md
├─ PAYLOAD_SCHEMA.md
├─ BUILD.md
├─ SECURITY.md
├─ TROUBLESHOOTING.md
├─ CHANGELOG.md
└─ LICENSE.txt


> The **WpfApp.csproj** links/copies `/assets/` and `/python/` into the app’s output dir during build, so the exe ships with everything beside it.

---

## Requirements

- **Windows 10/11**
- **Visual Studio 2022+** with `.NET 8 SDK` and **Desktop development with C#**
- **Python 3.10+** on PATH (`py -3`, `py`, `python`, or `python3`)  
  (optional, but required to run real audits)

Optional for webhooks:
- `pip install requests` (in whichever interpreter the app finds first)

---

## Build & Run

1. Open `NemesisC64.Auditor.sln` in Visual Studio.
2. Select **Debug | Any CPU** and **Start**.
3. Click **Run Audit**.
   - With no vendor engine present, the app still runs and creates a placeholder report.
   - To enable real collection, copy your **Robin** engine to:  
     `python/vendor/robin/` (e.g., `search.py`, `scrape.py`, `requirements.txt`, etc.)

### Packaging (simple)
Use **Build → Publish** or zip the `bin\Release\net8.0-windows\` folder contents
(ensure it includes `assets\` and `python\` directories).

---

## Workflow Overview

[WPF UI]
├─ creates input JSON
├─ launches: python/runner.py --input ... --output ...
├─ (optional) runner imports vendor/robin modules
├─ writes output JSON + /reports/auditor_report_*.txt
└─ UI reads JSON → updates Live Output + Findings grid


---

## Configuration Notes

- **Tor:** Toggle “Use Tor” to hint the vendor engine to use a Tor-friendly path if it supports it.
- **Webhook:** If provided, `runner.py` JSON-POSTs results; header `X-Auditor-Secret` is included when a secret is set.
- **Email:** UI fields are placeholders for future SMTP—no mail is sent by the default runner.

---

## Safety & Ethics

Use responsibly. Ensure you have **explicit permission** for any data you scan or collect.  
Respect local laws, terms of service, and privacy requirements.

---

## Troubleshooting Quick Tips

- **No Python found** → Install Python 3.10+ and ensure `py`/`python` is on PATH.
- **Vendor not detected** → Confirm the folder exists: `python/vendor/robin/` and contains `search.py`.
- **Webhook POST fails** → Install `requests` (`pip install requests`) or remove the webhook URL.
- **Empty findings** → Try a more specific query or verify vendor engine compatibility.

See `/docs/TROUBLESHOOTING.md` for deeper diagnostics.

---

## License

See `/docs/LICENSE.txt`.

© 2025 **Lexmilian de Mello / NemesisC64** — “Auditing silence, searching traces.”







