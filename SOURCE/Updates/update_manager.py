"""
Nexo Studios Update System
Nexo Calculator

Checks published GitHub Releases, downloads verified update assets,
stores pending-update metadata, and installs updates on Windows.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import re
from pathlib import Path
from typing import Optional


GITHUB_OWNER = "Nexo-Studio-s"
GITHUB_REPOSITORY = "nexo-calculator"
RELEASES_API = (
    f"https://api.github.com/repos/"
    f"{GITHUB_OWNER}/{GITHUB_REPOSITORY}/releases?per_page=100"
)
APPLICATION_NAME = "Nexo Calculator"
EXECUTABLE_NAME = "NexoCalculator.exe"
ALLOW_PRERELEASES = True

UPDATE_DIRECTORY = (
    Path(os.environ.get("LOCALAPPDATA", Path.home()))
    / "Nexo Studios"
    / "Nexo Calculator"
    / "Updates"
)
DOWNLOADED_EXECUTABLE = UPDATE_DIRECTORY / EXECUTABLE_NAME
UPDATE_INFO_FILE = UPDATE_DIRECTORY / "update.json"

VERSION_PATTERN = re.compile(
    r"^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?$",
    re.IGNORECASE,
)


def parse_version(version: str) -> Optional[tuple]:
    """Parse Nexo versions, sorting stable releases after prereleases."""
    if not isinstance(version, str):
        return None
    match = VERSION_PATTERN.fullmatch(version.strip())
    if not match:
        return None
    major, year, build = (int(match.group(i)) for i in (1, 2, 3))
    suffix = match.group(4)
    return major, year, build, 1 if suffix is None else 0, (suffix or "").lower()


def is_newer_version(current_version: str, available_version: str) -> bool:
    """Return True when available_version is newer than current_version."""
    current = parse_version(current_version)
    available = parse_version(available_version)
    return current is not None and available is not None and available > current


def _request_json(url: str):
    """Fetch JSON from GitHub's public API."""
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Nexo-Calculator-Update-System",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def get_executable_asset(release):
    """Return the NexoCalculator.exe asset for a release, if present."""
    if not isinstance(release, dict):
        return None
    assets = release.get("assets", [])
    if not isinstance(assets, list):
        return None
    for asset in assets:
        if isinstance(asset, dict) and asset.get("name") == EXECUTABLE_NAME:
            return asset
    return None


def get_latest_release(current_version: str):
    """Find the newest eligible published release with a downloadable EXE."""
    current = parse_version(current_version)
    if current is None:
        return None
    try:
        releases = _request_json(RELEASES_API)
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        OSError,
        json.JSONDecodeError,
    ):
        return None
    if not isinstance(releases, list):
        return None

    candidates = []
    for release in releases:
        if not isinstance(release, dict) or release.get("draft", False):
            continue
        if release.get("prerelease", False) and not ALLOW_PRERELEASES:
            continue
        version = parse_version(release.get("tag_name", ""))
        if version is None or version <= current:
            continue
        if not get_executable_asset(release):
            continue
        candidates.append((version, release))
    return max(candidates, key=lambda candidate: candidate[0])[1] if candidates else None


def _valid_download_url(url: str) -> bool:
    """Only download release assets from HTTPS URLs."""
    try:
        parsed = urllib.parse.urlparse(url)
        return parsed.scheme == "https" and bool(parsed.netloc)
    except (TypeError, ValueError):
        return False


def download_update(release) -> bool:
    """Download and verify the selected release executable atomically."""
    asset = get_executable_asset(release)
    if not asset:
        return False
    download_url = asset.get("browser_download_url")
    if not isinstance(download_url, str) or not _valid_download_url(download_url):
        return False

    UPDATE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    temporary_file = UPDATE_DIRECTORY / f"{EXECUTABLE_NAME}.download"
    temporary_info = UPDATE_DIRECTORY / "update.json.tmp"

    try:
        temporary_file.unlink(missing_ok=True)
        request = urllib.request.Request(
            download_url,
            headers={"User-Agent": "Nexo-Calculator-Update-System"},
        )
        digest = hashlib.sha256()
        downloaded_size = 0
        with urllib.request.urlopen(request, timeout=90) as response, temporary_file.open("wb") as output:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
                digest.update(chunk)
                downloaded_size += len(chunk)

        if downloaded_size <= 0:
            raise OSError("The downloaded update is empty.")
        expected_size = asset.get("size")
        if isinstance(expected_size, int) and expected_size > 0 and downloaded_size != expected_size:
            raise OSError("The downloaded file size does not match the release asset.")
        expected_digest = asset.get("digest")
        if isinstance(expected_digest, str) and expected_digest.startswith("sha256:"):
            if digest.hexdigest().lower() != expected_digest.split(":", 1)[1].lower():
                raise OSError("The downloaded update failed SHA-256 verification.")

        version = release.get("tag_name")
        if not version or parse_version(version) is None:
            raise OSError("The release has an invalid version tag.")

        temporary_file.replace(DOWNLOADED_EXECUTABLE)
        update_information = {
            "version": version,
            "name": release.get("name") or version,
            "release_url": release.get("html_url", ""),
            "downloaded": True,
            "executable": str(DOWNLOADED_EXECUTABLE),
            "sha256": digest.hexdigest(),
            "size": downloaded_size,
        }
        temporary_info.write_text(json.dumps(update_information, indent=4), encoding="utf-8")
        temporary_info.replace(UPDATE_INFO_FILE)
        return True
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        OSError,
        json.JSONDecodeError,
    ):
        temporary_file.unlink(missing_ok=True)
        temporary_info.unlink(missing_ok=True)
        return False


def get_pending_update():
    """Return valid metadata for an update already downloaded to disk."""
    if not UPDATE_INFO_FILE.is_file() or not DOWNLOADED_EXECUTABLE.is_file():
        clear_pending_update()
        return None
    try:
        data = json.loads(UPDATE_INFO_FILE.read_text(encoding="utf-8"))
        version = data.get("version") if isinstance(data, dict) else None
        if not version or parse_version(version) is None:
            raise ValueError("Invalid pending update metadata.")
        expected_digest = data.get("sha256")
        if expected_digest:
            digest = hashlib.sha256()
            with DOWNLOADED_EXECUTABLE.open("rb") as executable:
                for chunk in iter(lambda: executable.read(1024 * 1024), b""):
                    digest.update(chunk)
            if digest.hexdigest().lower() != str(expected_digest).lower():
                raise ValueError("Pending update checksum mismatch.")
        return data
    except (OSError, ValueError, json.JSONDecodeError, AttributeError):
        clear_pending_update()
        return None


def clear_pending_update():
    """Remove pending update files without failing if they are absent."""
    for path in (DOWNLOADED_EXECUTABLE, UPDATE_INFO_FILE, UPDATE_DIRECTORY / "update.json.tmp"):
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass


def install_and_restart() -> bool:
    """Use a separate PowerShell process to replace and restart the packaged EXE."""
    pending = get_pending_update()
    if not pending or not getattr(sys, "frozen", False) or os.name != "nt":
        return False

    downloaded = Path(pending.get("executable", ""))
    current_executable = Path(sys.executable)
    if not downloaded.is_file() or not current_executable.is_file():
        return False

    powershell = shutil.which("powershell.exe") or shutil.which("powershell")
    if not powershell:
        return False

    helper_script = UPDATE_DIRECTORY / "install_update.ps1"
    script = r'''
param(
    [Parameter(Mandatory=$true)][int]$TargetProcessId,
    [Parameter(Mandatory=$true)][string]$SourcePath,
    [Parameter(Mandatory=$true)][string]$TargetPath,
    [Parameter(Mandatory=$true)][string]$MetadataPath,
    [Parameter(Mandatory=$true)][string]$ScriptPath
)
$ErrorActionPreference = "Stop"
while (Get-Process -Id $TargetProcessId -ErrorAction SilentlyContinue) {
    Start-Sleep -Milliseconds 400
}
$installed = $false
for ($attempt = 0; $attempt -lt 20; $attempt++) {
    try {
        Copy-Item -LiteralPath $SourcePath -Destination $TargetPath -Force
        $installed = $true
        break
    } catch {
        Start-Sleep -Milliseconds 500
    }
}
if (-not $installed) { exit 1 }
try {
    Start-Process -FilePath $TargetPath
    Remove-Item -LiteralPath $SourcePath -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $MetadataPath -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $ScriptPath -Force -ErrorAction SilentlyContinue
} catch { exit 1 }
'''
    try:
        UPDATE_DIRECTORY.mkdir(parents=True, exist_ok=True)
        helper_script.write_text(script, encoding="utf-8")
        subprocess.Popen(
            [
                powershell, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                "-WindowStyle", "Hidden", "-File", str(helper_script), str(os.getpid()),
                str(downloaded), str(current_executable), str(UPDATE_INFO_FILE), str(helper_script),
            ],
            close_fds=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except OSError:
        return False
