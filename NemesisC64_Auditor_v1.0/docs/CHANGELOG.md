# CHANGELOG.md — NemesisC64 Auditor

All notable changes to **NemesisC64 Auditor** are documented here.  
This project follows a **semantic-like** versioning pattern: *Major.Minor.Revision.*

---

## [1.0.0] — 2025-10-08  
### ✨ Initial Public Build
- First fully structured release of the **NemesisC64 Auditor** project.
- Includes complete WPF interface with:
  - `App.xaml` resource dictionary (dark theme)
  - `MainWindow.xaml` and `InfoWindow.xaml`
  - Status bar, progress bar, and live log output.
- Implements `runner.py` Python bridge with:
  - JSON file-based request/response system.
  - Optional Robin vendor engine integration.
  - Text report generator and optional webhook POST.
- Added core assets:
  - `ascii_footer.txt`
  - `info_text.html`
- Comprehensive documentation:
  - `README.md`, `ARCHITECTURE.md`, `BUILD.md`, `PAYLOAD_SCHEMA.md`,
    `DEVELOPER.md`, `SECURITY.md`, `TROUBLESHOOTING.md`, `CHANGELOG.md`
- Solution configured for Visual Studio 2022+, .NET 8, Python 3.10+.

---

## [0.9.0] — 2025-10-07  
### 🧩 Pre-Release Prototype
- Created early drafts of:
  - `App.xaml` and `MainWindow.xaml`
  - Initial skeleton of `runner.py`
- Verified process launch and placeholder output JSON.

---

## [0.8.0] — 2025-10-06  
### 🧠 Concept Design
- Defined high-level architecture.
- Established folder tree (`NemesisC64_Auditor_v1.0_FileTree.txt`).
- Planned hybrid WPF + Python communication.

---

## [0.7.0] — 2025-10-01  
### 📄 Planning Phase
- Outlined the NemesisC64 Auditor project concept.
- Collected and tested Robin vendor engine (`robin-main.zip`).
- Wrote initial technical documentation drafts.

---

## [0.1.0] — 2025-09-29  
### 🌱 Project Inception
- Declared intent to build a transparent auditor tool with both local and
  network-safe modes.
- Established guiding motto:  
  > “Auditing silence, searching traces.”

---

### 🧭 Versioning Strategy

| Field | Meaning |
|-------|----------|
| **Major** | Architectural or API-level changes |
| **Minor** | Feature additions or refinements |
| **Revision** | Bug fixes, documentation, small tweaks |

---

### 📦 Next Planned Milestone

**v1.1.0 — “Integration Release”**
- Add PDF/HTML export
- Add continuous live Python log streaming
- Add optional settings persistence (JSON config)

---

© 2025 Lexmilian de Mello / NemesisC64  
*"Versioning is memory made explicit."*
