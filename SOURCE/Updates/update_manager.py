"""
Nexo Studios Update System
Nexo Calculator

Official version format:
v0.2026.00008
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional


# ============================================================
# Nexo Studios Update Configuration
# ============================================================

GITHUB_OWNER = "Nexo-Studio-s"
GITHUB_REPOSITORY = "nexo-calculator"

RELEASES_API = (
    f"https://api.github.com/repos/"
    f"{GITHUB_OWNER}/{GITHUB_REPOSITORY}/releases"
)

VERSION_PATTERN = re.compile(
    r"^v0\.2026\.(\d{5,})$"
)

APPLICATION_NAME = "Nexo Calculator"
EXECUTABLE_NAME = "NexoCalculator.exe"


# ============================================================
# Local Update Storage
# ============================================================

UPDATE_DIRECTORY = (
    Path(os.environ.get("LOCALAPPDATA", Path.home()))
    / "Nexo Studios"
    / "Nexo Calculator"
    / "Updates"
)

DOWNLOADED_EXECUTABLE = UPDATE_DIRECTORY / EXECUTABLE_NAME
UPDATE_INFO_FILE = UPDATE_DIRECTORY / "update.json"


# ============================================================
# Version Handling
# ============================================================

def parse_version(version: str) -> Optional[tuple[int, int, int]]:
    """
    Parse the official Nexo version format.

    Example:
        v0.2026.00008
        -> (0, 2026, 8)
    """

    match = VERSION_PATTERN.fullmatch(version.strip())

    if not match:
        return None

    return (
        0,
        2026,
        int(match.group(1))
    )


def is_newer_version(
    current_version: str,
    available_version: str
) -> bool:
    """Return True when the available Nexo version is newer."""

    current = parse_version(current_version)
    available = parse_version(available_version)

    if current is None or available is None:
        return False

    return available > current


# ============================================================
# GitHub Releases
# ============================================================

def _request_json(url: str):
    """Request JSON from GitHub."""

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Nexo-Calculator"
        }
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def get_latest_release(current_version: str):
    """
    Find the newest valid Nexo 0.2026 release.

    Drafts, prereleases and unrelated versions are ignored.
    """

    try:
        releases = _request_json(RELEASES_API)
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        OSError,
        json.JSONDecodeError
    ):
        return None

    newest = None
    newest_version = None

    for release in releases:

        if release.get("draft"):
            continue

        if release.get("prerelease"):
            continue

        tag_name = release.get("tag_name", "")

        parsed = parse_version(tag_name)

        if parsed is None:
            continue

        if not is_newer_version(
            current_version,
            tag_name
        ):
            continue

        if newest_version is None or parsed > newest_version:
            newest = release
            newest_version = parsed

    return newest


# ============================================================
# Release Asset
# ============================================================

def get_executable_asset(release):
    """Find NexoCalculator.exe in a GitHub release."""

    if not release:
        return None

    for asset in release.get("assets", []):
        if asset.get("name") == EXECUTABLE_NAME:
            return asset

    return None


# ============================================================
# Download
# ============================================================

def download_update(release) -> bool:
    """
    Download the selected Nexo Calculator executable.
    """

    asset = get_executable_asset(release)

    if not asset:
        return False

    download_url = asset.get("browser_download_url")

    if not download_url:
        return False

    UPDATE_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    temporary_file = (
        UPDATE_DIRECTORY
        / f"{EXECUTABLE_NAME}.download"
    )

    try:
        request = urllib.request.Request(
            download_url,
            headers={
                "User-Agent": "Nexo-Calculator"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=60
        ) as response, open(
            temporary_file,
            "wb"
        ) as output:

            shutil.copyfileobj(
                response,
                output
            )

        if not temporary_file.exists():
            return False

        if temporary_file.stat().st_size <= 0:
            temporary_file.unlink(
                missing_ok=True
            )
            return False

        temporary_file.replace(
            DOWNLOADED_EXECUTABLE
        )

        update_information = {
            "version": release.get("tag_name"),
            "name": release.get(
                "name",
                release.get("tag_name")
            ),
            "downloaded": True,
            "executable": str(
                DOWNLOADED_EXECUTABLE
            )
        }

        UPDATE_INFO_FILE.write_text(
            json.dumps(
                update_information,
                indent=4
            ),
            encoding="utf-8"
        )

        return True

    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        OSError
    ):
        temporary_file.unlink(
            missing_ok=True
        )

        return False


# ============================================================
# Pending Update
# ============================================================

def get_pending_update():
    """Return downloaded update information."""

    if not UPDATE_INFO_FILE.exists():
        return None

    if not DOWNLOADED_EXECUTABLE.exists():
        clear_pending_update()
        return None

    try:
        data = json.loads(
            UPDATE_INFO_FILE.read_text(
                encoding="utf-8"
            )
        )
    except (
        OSError,
        json.JSONDecodeError
    ):
        clear_pending_update()
        return None

    version = data.get("version")

    if not version or parse_version(version) is None:
        clear_pending_update()
        return None

    return data


def clear_pending_update():
    """Remove the pending update."""

    DOWNLOADED_EXECUTABLE.unlink(
        missing_ok=True
    )

    UPDATE_INFO_FILE.unlink(
        missing_ok=True
    )


# ============================================================
# Install
# ============================================================

def install_and_restart() -> bool:
    """
    Start a temporary updater process.

    The helper waits until the current application has exited,
    replaces the executable and starts the new version.
    """

    pending = get_pending_update()

    if not pending:
        return False

    downloaded = Path(
        pending["executable"]
    )

    current_executable = Path(
        sys.executable
    )

    if not downloaded.exists():
        clear_pending_update()
        return False

    helper_script = UPDATE_DIRECTORY / "install_update.py"

    helper_script.write_text(
        """
import os
import shutil
import subprocess
import sys
import time

pid = int(sys.argv[1])
source = sys.argv[2]
target = sys.argv[3]

while True:
    try:
        os.kill(pid, 0)
        time.sleep(0.5)
    except OSError:
        break

try:
    shutil.copy2(source, target)
except Exception:
    sys.exit(1)

try:
    os.remove(source)
except OSError:
    pass

subprocess.Popen(
    [target],
    close_fds=True
)
""",
        encoding="utf-8"
    )

    subprocess.Popen(
        [
            sys.executable,
            str(helper_script),
            str(os.getpid()),
            str(downloaded),
            str(current_executable)
        ],
        creationflags=subprocess.CREATE_NO_WINDOW
    )

    return True
