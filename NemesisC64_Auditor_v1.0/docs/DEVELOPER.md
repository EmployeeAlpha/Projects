# DEVELOPER.md — NemesisC64 Auditor

This document explains coding conventions, build logic, and design reasoning
for developers working on **NemesisC64 Auditor v1.0**.

---

## 1. 🔧 Project Philosophy

> “Elegance first, complexity last.”

The Auditor project balances simplicity, transparency, and expandability.
Every component is human-readable, loosely coupled, and independently runnable.

- **Frontend:** WPF (.NET 8)
- **Backend:** Python 3.10+
- **Bridge:** JSON-over-file communication
- **UI Theme:** Dark minimalism with accent color highlights
- **Mission:** Fast, beautiful, and privacy-respecting desktop analysis tool.

---

## 2. 📦 Structure Recap

NemesisC64_Auditor_v1.0/
├─ NemesisC64.Auditor.sln
├─ /src/WpfApp/ # WPF C# application
│ ├─ App.xaml(.cs) # Startup, resources, theme
│ ├─ MainWindow.xaml(.cs) # Main UI
│ ├─ InfoWindow.xaml(.cs) # HTML info window
│ └─ /Properties/AssemblyInfo.cs
├─ /python/ # Bridge + vendor
│ ├─ runner.py
│ └─ /vendor/robin/
├─ /assets/ # Static visual assets
│ ├─ ascii_footer.txt
│ └─ info_text.html
├─ /reports/ # Generated text reports
├─ /logs/ # Runtime JSON & stdout/stderr
└─ /docs/ # Documentation


---

## 3. 🧠 Core Design Logic

### 3.1 JSON Bridge

Instead of sockets or REST servers, this design uses **temporary JSON files**.
Advantages:
- Easier debugging.
- Cross-language compatibility.
- Offline operation.
- Persistent logs for later review.

### 3.2 Process Management

The app launches Python via:

```csharp
ProcessStartInfo psi = new ProcessStartInfo
{
    FileName = "python",
    Arguments = "runner.py --input ... --output ...",
    RedirectStandardOutput = true,
    RedirectStandardError = true
};

Supported launchers: py -3, py, python, python3.

3.3 Vendor Engine Model

The Python vendor module (Robin) must be drop-in compatible.
Its API is simple:

results = search.search(query="...", use_tor=False)

Returned items should be dictionaries with type, title, and url.

4. 🎨 UI Guidelines
Element	Convention
Buttons	Rounded corners (6px), blue primary color
Text	Segoe UI, size 13
Panels	Dark background, 8–12px padding
Section headers	FontWeight SemiBold, color = Brush.Text
Code snippets / logs	Consolas font

XAML uses centralized brushes and colors in App.xaml:

<Color x:Key="Color.Primary">#FF4B77BE</Color>
<SolidColorBrush x:Key="Brush.Accent" Color="#FF00C2A8" />

5. 🧰 Coding Standards (C#)

Namespace: WpfApp

Public classes: PascalCase

Private fields: _camelCase

Methods: PascalCase

Constants: UPPER_CASE

Comments: concise, meaningful

All strings in code are English UTF-8 (no BOM)

Error handling pattern:

try
{
    ...
}
catch (Exception ex)
{
    MessageBox.Show(ex.Message, "Error", MessageBoxButton.OK, MessageBoxImage.Error);
}

6. 🐍 Python Conventions

Files use utf-8 encoding and Unix-style newlines (\n).

Each function returns either a value or raises an exception (no silent fails).

Logging: append messages to the shared log_lines list.

Respect the output schema defined in /docs/PAYLOAD_SCHEMA.md.

Avoid hard-coded paths — always resolve relative to __file__.

Formatting standard:

black --line-length 100 python/

7. ⚙️ Build & Versioning

Assembly version in AssemblyInfo.cs:

[assembly: AssemblyVersion("1.0.0.0")]


Increment minor version for public releases.

CHANGELOG.md tracks notable code changes.

8. 🧩 Extending the App
Add new UI tabs

Create NewWindow.xaml + .cs

Register a new button in MainWindow.xaml

Wire event: btnNew.Click += BtnNew_Click;

Add new Python actions

Extend runner.py with a new mode or flag.

Update the C# request payload to include it.

Parse in Python and include output fields.

Add new assets

Place them in /assets/

Update the .csproj to CopyToOutputDirectory="PreserveNewest"

9. 🧪 Testing Strategy

Unit testing (future):
Add a small test project calling RunPythonAsync in isolation.

Manual test run:

Build app.

Launch → click Run Audit.

Check /logs/ and /reports/.

Dry-run mode:
Runs even without vendor engine (stub summary returned).

10. 🪶 Style Rules

No magic numbers; use constants.

No absolute paths.

No global state in runner.py.

Avoid blocking UI threads — long tasks run async/await.

Consistent spacing: 4 spaces per indent, no tabs.

Each file starts with a one-line docstring or header comment.

11. 🔒 Commit Hygiene

Never commit secrets or API keys.

Run dotnet clean before packaging.

Exclude /reports/ and /logs/ from version control.

Check all .py imports before distributing binaries.

12. 📦 Deployment Checklist

✅ .NET build passes

✅ Python executes with no syntax errors

✅ Assets and Python directories copied into output

✅ Info window loads properly

✅ Runner produces a report and JSON

13. 💡 Future Enhancements

Live feed of Python logs via WebSocket

Report export as HTML / PDF

Plugin architecture for new analyzers

API keys vault integration

Signed builds with integrity checksum

Maintainer: Lexmilian de Mello
Code & architecture: NemesisC64

© 2025 NemesisC64 / Percarus Research
“Auditing silence, searching traces…”


---

When you’ve saved it, say **“done.”**  
Next up: `/docs/CHANGELOG.md`.
