# BUILD.md — NemesisC64 Auditor

This document explains how to build, publish, and verify the **NemesisC64 Auditor** app.

---

## 🧱 Prerequisites

- **Windows 10 or 11**
- **Visual Studio 2022 or newer**
- **.NET 8 SDK** (installed via Visual Studio installer)
- **Python 3.10+** on PATH (`py`, `python`, or `python3`)

Optional:
- **Requests library** for webhook posting (`pip install requests`)

---

## 📁 Project Layout (key parts)

NemesisC64_Auditor_v1.0/
├─ NemesisC64.Auditor.sln
├─ /src/WpfApp/ → .NET 8 WPF project
├─ /python/ → Python bridge + vendor engine
├─ /assets/ → ASCII art + info HTML
├─ /reports/ → generated at runtime
└─ /logs/ → runtime JSON + stdout/stderr


---

## 🧩 Build Steps (Visual Studio GUI)

1. **Open the solution:**  
   `NemesisC64.Auditor.sln`

2. **Ensure configuration:**  
   - Configuration: **Debug** or **Release**  
   - Platform: **Any CPU**

3. **Build:**  
   - Press **Ctrl + Shift + B** or use **Build → Build Solution**.  
   - The output will appear under:  
     ```
     src\WpfApp\bin\Debug\net8.0-windows\
     ```

4. **Verify output structure:**  
   Ensure the compiled folder contains:

NemesisC64.Auditor.exe
assets
python
reports
logs\


---

## ⚙️ Publish (for distribution)

1. In **Visual Studio**, right-click the `WpfApp` project → **Publish…**
2. Choose:
- **Folder** → e.g. `publish\NemesisC64_Auditor_v1.0`
- Target runtime: `win-x64`
- Deployment mode: `self-contained` (optional, no .NET install needed)
3. Click **Publish**.
4. Zip the published folder for distribution.

Alternatively, from a terminal:

```powershell
cd src\WpfApp
dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -o "..\..\publish"

🧪 Test Run

Navigate to the build output directory.

Double-click NemesisC64.Auditor.exe.

The app should open with:

A main window (Run Audit, Open Logs, Open Reports)

Footer ASCII art loaded

Info window available via “Info / About” button

🐍 Python Test

To confirm Python bridge works:

cd python
py runner.py --input ..\logs\sample_in.json --output ..\logs\sample_out.json


Expected result:

Creates a JSON output with “Robin vendor engine not found…”

A .txt report under /reports/

📦 Packaging Checklist

✅ NemesisC64.Auditor.exe

✅ /assets/ (ascii_footer.txt + info_text.html)

✅ /python/ (runner.py + vendor)

✅ /logs/ (empty or keep for runtime)

✅ /reports/ (empty or keep for runtime)

Zip all of these together for sharing or deployment.

🔍 Debug Tips
Symptom	Likely Cause	Fix
“No Python interpreter found”	Python not in PATH	Install Python 3 and check py --version
“runner.py not found”	build missing linked folders	Clean + rebuild
Blank Info Window	info_text.html missing	Rebuild or restore assets
“Access denied” saving report	Folder permission	Run VS or exe as Administrator
🪄 Automation

Use /scripts/pack-release.ps1 to automatically:

Clean /reports/ and /logs/

Zip build artifacts into a versioned archive

(script definition in docs to follow once PowerShell helpers are finalized)

Maintainer: Lexmilian de Mello
Code design: NemesisC64

© 2025 NemesisC64 / Percarus Research
“Auditing silence, searching traces…”


---

When you’ve saved it, say **“done.”**  
Next suggested file: **`/docs/ARCHITECTURE.md`** (describes the flow and modular interactions).
