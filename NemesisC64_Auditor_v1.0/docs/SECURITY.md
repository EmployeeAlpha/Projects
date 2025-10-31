# SECURITY.md — NemesisC64 Auditor

This document outlines the security model, privacy considerations, and responsible-use policies
for **NemesisC64 Auditor v1.0**.

---

## 1. Security Philosophy

> “A secure tool is one that respects the boundaries of its operator.”

NemesisC64 Auditor is designed for **ethical auditing**, **self-inspection**, and **controlled data review**.
It does *not* perform any hidden transmission or telemetry and operates entirely offline
unless the user explicitly enables a network feature (e.g., webhook).

---

## 2. Data Handling Model

| Element | Storage Location | Persistence | Notes |
|----------|-----------------|--------------|-------|
| Input JSON | `/logs/` | overwritten per run | temporary, plain-text |
| Output JSON | `/logs/` | kept for reference | includes full findings |
| Reports | `/reports/` | permanent until deleted | human-readable summary |
| Logs | `/logs/` | rolling | contains stdout/stderr |
| Webhook POST | remote (user-defined) | one-time transfer | best-effort only |

No encryption is applied by default; local file security depends on the user’s OS permissions.

---

## 3. Execution Boundaries

- **No elevated privileges** are required.
- The WPF process runs in user space.
- The Python bridge only writes within its own working directories.
- No external sockets are opened unless the user supplies a webhook URL.

---

## 4. Network Behavior

| Feature | Enabled By | Action |
|----------|-------------|--------|
| **Webhook delivery** | User provides URL | Single HTTPS POST of result JSON |
| **Tor option** | User enables checkbox | Hint only; vendor decides how to route |
| **Vendor engine** | Copied manually | May perform network scraping, but fully under user control |
| **Email fields** | Placeholder | Not implemented; zero network use |

If the **vendor/robin** engine contains code that performs scraping or crawling, the user assumes full responsibility for its lawful use.

---

## 5. Privacy Principles

1. **Transparency:** No hidden background connections.  
2. **Locality:** All generated data stays on the user’s machine.  
3. **User control:** Network features are opt-in and visible in the UI.  
4. **Minimal collection:** Only requested audit data is processed.  
5. **Ephemerality:** Temporary JSONs can be safely deleted after each run.

---

## 6. Recommendations for Secure Operation

- Store the entire app folder on an **encrypted drive** if handling sensitive data.
- Clean `/logs/` and `/reports/` after external distribution.
- Avoid using personal webhook URLs for public or shared builds.
- If integrating SMTP in the future, use OAuth-based credentials rather than plaintext passwords.
- Keep the Python environment isolated with a dedicated virtualenv.

---

## 7. Code Integrity

- Each build is reproducible; no dynamic downloads occur.
- Verify checksums of any external Python packages (`requirements.txt`) before installation.
- PowerShell scripts (`pack-release.ps1`, `verify-tor.ps1`) are signed or auditable.

---

## 8. Vendor Module Caution

The optional **Robin engine** may introduce its own dependencies.
Before running:
1. Review `vendor/robin/requirements.txt`
2. Read `config.py` for network endpoints
3. Audit any `api_key` or `token` usage
4. Run in a sandboxed environment if uncertain

---

## 9. Responsible Use Disclaimer

NemesisC64 Auditor is provided for lawful research, internal diagnostics, and educational purposes.  
The author and contributors disclaim liability for misuse, unauthorized scanning, or data interception.

---

## 10. Incident Reporting

If you identify a security flaw within this repository or its distributed binaries:

1. Contact **lexdemello@aol.com**
2. Include:
   - Version and build date
   - Description of issue
   - Steps to reproduce
   - Potential impact
3. Please do not publicly disclose before reasonable remediation.

---

© 2025 Lexmilian de Mello / NemesisC64  
*“Where code meets conscience.”*
