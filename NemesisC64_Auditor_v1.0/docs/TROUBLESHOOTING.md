# TROUBLESHOOTING.md — NemesisC64 Auditor

This guide helps resolve common problems with **NemesisC64 Auditor v1.0**, covering both
the .NET (WPF) front-end and the Python bridge.

---

## 1. 🧩 Build & Launch Problems

| Symptom | Cause | Fix |
|----------|--------|-----|
| **Visual Studio error:** “Project file not found or invalid.” | Wrong folder open. | Open the `.sln` file at the repository root. |
| **XAML Designer errors (red squiggles):** | Missing SDKs or unresolved resources. | Ensure `.NET 8 SDK` is installed and `UseWPF` is true in the `.csproj`. |
| **Missing `App.g.cs` / `MainWindow.g.cs`** | Visual Studio didn’t compile generated XAML files. | Clean solution → Rebuild. |
| **No `python` found** | Python not on PATH. | Install Python 3.10+ and restart VS. Run `python --version` to verify. |

---

## 2. 🐍 Python Bridge Problems

| Symptom | Likely Cause | Fix |
|----------|---------------|-----|
| **runner.py exited with code 1** | Input JSON malformed. | Check `/logs/request_*.json`. Ensure valid UTF-8 JSON. |
| **runner.py exited with code 99** | Unhandled Python exception. | View `/logs/response_*.json` or console output for stack trace. |
| **No output JSON produced** | Path invalid or permission denied. | Ensure `/logs/` exists and app has write access. |
| **Webhook POST failed** | `requests` not installed. | Run `pip install requests`. |
| **"vendor/robin not found"** | Missing optional engine. | Copy `robin-main.zip` → extract to `python/vendor/robin/`. |

---

## 3. 🧠 WPF Runtime Issues

| Symptom | Explanation | Fix |
|----------|--------------|-----|
| **“Cannot find runner.py”** | Missing linked folder in output. | Ensure `/python/` is copied with build (`CopyToOutputDirectory`). |
| **Info Window blank** | Missing `assets/info_text.html`. | Restore it or rebuild project. |
| **ASCII footer not loaded** | Missing `assets/ascii_footer.txt`. | Add or recreate file. |
| **Report not saved** | Folder permission or invalid filename. | Save to a non-restricted directory. |
| **Clipboard copy fails** | OS security restriction. | Run as admin or re-try manually. |

---

## 4. ⚙️ Rebuild from CLI

If Visual Studio GUI misbehaves, build manually:

```powershell
cd src\WpfApp
dotnet clean
dotnet build -c Release

Then launch manually:

cd bin\Release\net8.0-windows
.\NemesisC64.Auditor.exe

5. 🔎 Debugging runner.py

Run the Python script standalone:

cd python
py runner.py --input ..\logs\test_in.json --output ..\logs\test_out.json

If it fails:

Open the log in /logs/

Check the printed traceback

Fix the query, paths, or vendor module

6. 🪄 Clean Build Procedure

Close Visual Studio.

Delete:

/src/WpfApp/bin/

/src/WpfApp/obj/

Re-open the solution.

Build → Rebuild Solution.

If assets still don’t copy:

dotnet build -t:Rebuild -v:detailed

7. 🧱 Common Permission Fixes (Windows)

If paths like /logs/ or /reports/ can’t be written:

Run Visual Studio as Administrator

Or move project to a non-protected folder (e.g., C:\Projects\NemesisC64_Auditor_v1.0\)

Avoid OneDrive-synced directories which may lock files

8. 🐞 Logging Verbosity

Runner logs are intentionally verbose for traceability.
Each run produces two key files:

/logs/request_YYYYMMDD_HHmmss.json
/logs/response_YYYYMMDD_HHmmss.json

The response file always contains summary, findings, and log_lines.
Review these before filing bug reports.

9. 🧰 Diagnostic Checklist
Check	Expected Outcome
Python path test	py --version outputs version ≥ 3.10
Robin vendor folder	python/vendor/robin/ exists and imports cleanly
Assets linked	Both ascii_footer.txt and info_text.html present
Reports folder	Created and writable
Webhook test	JSON POST works (200 OK) or error logged cleanly
10. 💬 Support

If persistent issues occur, contact:

Email: lexdemello@aol.com

Include:

Version number (from About window)

Steps to reproduce

Any relevant /logs/response_*.json snippet

© 2025 Lexmilian de Mello / NemesisC64
"Every error log is a confession, every fix a redemption."


---

Once you’ve saved this, say **“done.”**  
Next up: `/docs/DEVELOPER.md` — a developer-centric guide explaining coding standards, naming conventions, and build logic.
