"""
Nexo Studios Update System
Nexo Calculator

Checks GitHub Releases on every application startup.

Official version examples:
    v0.2026.00008
    v0.2026.00009-PR
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional
import re


# ============================================================
# Nexo Studios Update Configuration
# ============================================================

GITHUB_OWNER = "Nexo-Studio-s"
GITHUB_REPOSITORY = "nexo-calculator"

RELEASES_API = (
    f"https://api.github.com/repos/"
    f"{GITHUB_OWNER}/{GITHUB_REPOSITORY}/releases"
)

APPLICATION_NAME = "Nexo Calculator"
EXECUTABLE_NAME = "NexoCalculator.exe"

# Tijdens de ontwikkelfase mogen prereleases worden gevonden.
ALLOW_PRERELEASES = True


# ============================================================
# Local Update Storage
# ============================================================

UPDATE_DIRECTORY = (
    Path(os.environ.get("LOCALAPPDATA", Path.home()))
    / "Nexo Studios"
    / "Nexo Calculator"
    / "Updates"
)

DOWNLOADED_EXECUTABLE = (
    UPDATE_DIRECTORY / EXECUTABLE_NAME
)

UPDATE_INFO_FILE = (
    UPDATE_DIRECTORY / "update.json"
)


# ============================================================
# Version Handling
# ============================================================

VERSION_PATTERN = re.compile(
    r"^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?$",
    re.IGNORECASE
)


def parse_version(
    version: str
) -> Optional[tuple[int, int, int, int]]:
    """
    Parse a Nexo version.

    Examples:

        v0.2026.00008
        -> (0, 2026, 8, 1)

        v0.2026.00009-PR
        -> (0, 2026, 9, 0)

    The fourth value represents the channel:

        1 = stable
        0 = prerelease
    """

    if not isinstance(version, str):
        return None

    match = VERSION_PATTERN.fullmatch(
        version.strip()
    )

    if not match:
        return None

    major = int(match.group(1))
    year = int(match.group(2))
    build = int(match.group(3))

    suffix = match.group(4)

    # Stable releases are considered newer than a
    # prerelease with the exact same version number.
    is_stable = (
        1
        if suffix is None
        else 0
    )

    return (
        major,
        year,
        build,
        is_stable
    )


def is_newer_version(
    current_version: str,
    available_version: str
) -> bool:
    """
    Return True only when the available version
    is newer than the installed version.
    """

    current = parse_version(
        current_version
    )

    available = parse_version(
        available_version
    )

    if current is None:
        return False

    if available is None:
        return False

    return available > current


# ============================================================
# GitHub API
# ============================================================

def _request_json(url: str):
    """
    Request JSON from GitHub.

    No authentication is required because the
    Nexo Calculator repository is public.
    """

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": (
                "Nexo-Calculator-Update-System"
            )
        }
    )

    with urllib.request.urlopen(
        request,
        timeout=10
    ) as response:

        return json.loads(
            response.read().decode(
                "utf-8"
            )
        )


# ============================================================
# GitHub Release Detection
# ============================================================

def get_latest_release(
    current_version: str
):
    """
    Find the newest published GitHub Release
    that is newer than the installed version.

    Draft releases are ignored.

    Published prereleases are accepted when
    ALLOW_PRERELEASES is True.
    """

    try:

        releases = _request_json(
            RELEASES_API
        )

    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        OSError,
        json.JSONDecodeError
    ):

        return None

    if not isinstance(
        releases,
        list
    ):
        return None

    current = parse_version(
        current_version
    )

    if current is None:
        return None

    newest_release = None
    newest_version = None

    for release in releases:

        if not isinstance(
            release,
            dict
        ):
            continue

        # Draft releases are not publicly installable.
        if release.get(
            "draft",
            False
        ):
            continue

        # Optional prerelease filtering.
        if (
            release.get(
                "prerelease",
                False
            )
            and not ALLOW_PRERELEASES
        ):
            continue

        tag_name = release.get(
            "tag_name",
            ""
        )

        parsed = parse_version(
            tag_name
        )

        if parsed is None:
            continue

        # This is the actual comparison:
        #
        # Installed:
        # v0.2026.00008
        #
        # GitHub:
        # v0.2026.00009-PR
        #
        # Result:
        # UPDATE AVAILABLE
        if parsed <= current:
            continue

        if (
            newest_version is None
            or parsed > newest_version
        ):
            newest_release = release
            newest_version = parsed

    return newest_release


# ============================================================
# Release Asset
# ============================================================

def get_executable_asset(
    release
):
    """
    Find NexoCalculator.exe inside
    the selected GitHub Release.
    """

    if not release:
        return None

    for asset in release.get(
        "assets",
        []
    ):

        if asset.get(
            "name"
        ) == EXECUTABLE_NAME:

            return asset

    return None


# ============================================================
# Download
# ============================================================

def download_update(
    release
) -> bool:
    """
    Download the executable belonging
    to the selected release.
    """

    asset = get_executable_asset(
        release
    )

    if not asset:
        return False

    download_url = asset.get(
        "browser_download_url"
    )

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
                "User-Agent":
                    "Nexo-Calculator-Update-System"
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

        if (
            temporary_file.stat().st_size
            <= 0
        ):

            temporary_file.unlink(
                missing_ok=True
            )

            return False

        temporary_file.replace(
            DOWNLOADED_EXECUTABLE
        )

        update_information = {

            "version":
                release.get(
                    "tag_name"
                ),

            "name":
                release.get(
                    "name",
                    release.get(
                        "tag_name"
                    )
                ),

            "release_url":
                release.get(
                    "html_url",
                    ""
                ),

            "downloaded":
                True,

            "executable":
                str(
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
    """
    Return information about an update that
    has already been downloaded.
    """

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

    version = data.get(
        "version"
    )

    if (
        not version
        or parse_version(version)
        is None
    ):

        clear_pending_update()

        return None

    return data


def clear_pending_update():
    """
    Remove downloaded update files.
    """

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
    Start the temporary updater.

    The helper waits until the current application
    has exited, replaces the executable and starts
    the new version.
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

    # Self replacement only works for the
    # packaged NexoCalculator.exe.
    if not getattr(
        sys,
        "frozen",
        False
    ):

        return False

    helper_script = (
        UPDATE_DIRECTORY
        / "install_update.py"
    )

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


# Wait for Nexo Calculator to close.
while True:

    try:

        os.kill(
            pid,
            0
        )

        time.sleep(
            0.5
        )

    except OSError:

        break


# Replace the old executable.
try:

    shutil.copy2(
        source,
        target
    )

except Exception:

    sys.exit(1)


# Remove downloaded copy.
try:

    os.remove(
        source
    )

except OSError:

    pass


# Start the new Nexo Calculator.
subprocess.Popen(
    [target],
    close_fds=True
)
""",
        encoding="utf-8"
    )

    creation_flags = 0

    if os.name == "nt":

        creation_flags = (
            subprocess.CREATE_NO_WINDOW
        )

    subprocess.Popen(
        [
            sys.executable,
            str(helper_script),
            str(os.getpid()),
            str(downloaded),
            str(current_executable)
        ],
        creationflags=creation_flags
    )

    return True
