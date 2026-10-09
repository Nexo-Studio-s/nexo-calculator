Nexo Calculator
Calculate As Easy as Never Before! — built by Nexo Studio's.
Nexo Calculator is a lightweight Windows calculator. Version v0.2026.00009 focuses on the Nexo Studios Update System: checking published GitHub releases, downloading an update, and offering to install it on the next step.
Features
Calculator interface for everyday arithmetic.
Checks published releases in the Nexo Calculator GitHub repository.
Shows an update prompt when a newer eligible release includes `NexoCalculator.exe`.
Downloads the release asset and checks its expected size and SHA-256 digest when GitHub supplies them.
Saves pending-update metadata under `%LOCALAPPDATA%\Nexo Studios\Nexo Calculator\Updates`.
Offers Install & Restart after the download completes.
Uses a separate PowerShell helper to wait for the application to exit before replacing the running executable.
Updating
Start Nexo Calculator while connected to the internet.
If a newer eligible release is available, choose Download nu.
Wait for the download to finish.
Choose to install and restart now, or defer installation.
If deferred, the downloaded update remains available the next time the app starts.
The updater works with the packaged Windows executable. Running from source is useful for development, but self-replacement is intentionally disabled in that mode.
Download
Open GitHub Releases and download `NexoCalculator.exe` from the release you want to use.
Run from source
Requirements: Python 3.13 or a compatible Python 3 release.
```powershell
python SOURCE/main.py
```
The application uses Python's built-in Tkinter and standard-library modules for the update system.
Build the Windows executable
The repository includes a GitHub Actions workflow at `.github/workflows/build.yml`.
Open the repository's Actions tab.
Select Build Nexo Calculator.
Choose Run workflow on the intended branch.
Download the `NexoCalculator` artifact after the workflow succeeds.
The workflow uses PyInstaller to create a single-file, windowed Windows executable.
Update-system notes
The updater checks the repository's published GitHub Releases; draft releases are ignored.
Prereleases are currently allowed for development/testing.
A release must contain an asset named exactly `NexoCalculator.exe` to be offered.
Release tags use the Nexo version format, for example `v0.2026.00009`.
To deliver source-code fixes to existing users, publish a release asset built from the fixed source. Updating the repository source alone does not change an already-published `.exe` asset.
Project structure
```text
SOURCE/
├── app.py
├── main.py
├── Calculate/
├── Input/
├── NOTsoDRIVERS/
├── Updates/
│   └── update_manager.py
└── UserInterface/
```
License
See LICENSE for the project's license terms.
---
Nexo Studio's — Building Tomorrow Together.
