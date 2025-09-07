#!/usr/bin/env python3
# Copyright (c) 2025 Francis Bain
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Automatically inserts or updates dual-year copyright headers in Python files.
# First year is taken from the file's first commit in Git history.
# Last year is the current year and updates automatically when the file changes.
# Author is taken from the file's first commit author.
# License is detected from the LICENSE file or, if not found, from the GitHub API.

import datetime
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import requests as _requests
except Exception:  # pragma: no cover - optional dependency in some environments
    _requests = None  # type: ignore

# Expose a typed name for use below; keep it optional so environments without
# the 'requests' package still work.
requests: Any | None = _requests  # type: ignore

CURRENT_YEAR = datetime.datetime.now().year

HEADER_PATTERN = re.compile(r"^# Copyright \(c\) (\d{4})(?:[-–—](\d{4}))? (.+)$")
ENCODING_PATTERN = re.compile(r"^#.*coding[:=]\s*([-\w.]+)", re.IGNORECASE)


def get_first_year(file_path: Path) -> str:
    """
    Return the year of the first commit for a file.
    Falls back to the current year if not found or invalid.
    """
    result = subprocess.run(
        [
            "git",
            "log",
            "--follow",
            "--reverse",
            "--format=%ad",
            "--date=format:%Y",
            str(file_path),
        ],
        capture_output=True,
        text=True,
    )

    # If git failed, fall back to the current year
    if result.returncode != 0:
        return str(CURRENT_YEAR)

    years = [y for y in result.stdout.strip().split("\n") if y]
    for y in years:
        if y.isdigit():
            return y
    return str(CURRENT_YEAR)


def get_author(file_path: Path) -> str:
    """
    Return the author of the first commit for a file.
    Falls back to 'Unknown Author' if not found.
    """
    result = subprocess.run(
        ["git", "log", "--follow", "--format=%an", "--reverse", str(file_path)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return "Unknown Author"

    authors = [a for a in result.stdout.strip().split("\n") if a.strip()]
    return authors[0].strip() if authors else "Unknown Author"


def get_license_spdx() -> str:
    """
    Detect the SPDX license ID from the LICENSE file or GitHub API.
    Returns 'NOASSERTION' if not found.
    """
    license_file = Path("LICENSE")
    if license_file.exists():
        text = license_file.read_text(encoding="utf-8")
        match = re.search(r"SPDX-License-Identifier:\s*([A-Za-z0-9.\-+]+)", text)
        if match is not None:
            return match.group(1)
        if "GNU GENERAL PUBLIC LICENSE" in text and "Version 3" in text:
            return "GPL-3.0-or-later"

    # Attempt to discover repository owner/name from git remote URL so we can
    # query the GitHub API for the license. If anything fails here (git not
    # available, parsing fails, network error, rate limit), fall back to the
    # local LICENSE parsing above and return 'NOASSERTION' if no SPDX found.
    # If 'requests' is not available in the current environment, skip the
    # network/GitHub API route and fall back to the local LICENSE parsing.
    if requests is None:
        return "NOASSERTION"

    try:
        # Get origin URL from git; this works in forks and renamed repos too.
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )
        remote_url = result.stdout.strip()
        # Extract owner/repo from a variety of git URL formats
        m = re.search(
            r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+)(?:\.git)?", remote_url
        )
        if not m:
            # Could not parse; fall back to local LICENSE parsing result
            return "NOASSERTION"

        owner = m.group("owner")
        repo = m.group("repo")

        api_url = f"https://api.github.com/repos/{owner}/{repo}/license"

        headers = {}
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"token {token}"

        resp = requests.get(api_url, headers=headers or None, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            license_info = data.get("license")
            if isinstance(license_info, dict):
                spdx_id = license_info.get("spdx_id")
                if isinstance(spdx_id, str):
                    return spdx_id
        # Non-200 response - treat as failure and fall through to local fallback
    except subprocess.CalledProcessError:
        # git remote failed — fall back to local LICENSE parsing
        return "NOASSERTION"
    except requests.RequestException:
        # networking issue or rate limit — fall back to local LICENSE parsing
        return "NOASSERTION"
    except Exception:
        # Any other unexpected error should not propagate — fall back
        return "NOASSERTION"

    return "NOASSERTION"


def update_header(file_path: Path, license_id: str) -> None:
    """
    Insert or update the copyright header in a file.
    Preserves shebangs and encoding lines at the top.
    """
    text = file_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    first_year = get_first_year(file_path)
    author = get_author(file_path)

    # Helper: build header lines given year string and author
    def build_header(year_str: str, author_str: str, lic: str) -> list[str]:
        return [
            f"# Copyright (c) {year_str} {author_str}",
            f"# SPDX-License-Identifier: {lic}",
        ]

    # Find insert index: skip shebang, encoding lines and initial blank lines
    insert_index = 0
    while insert_index < len(lines):
        s = lines[insert_index].strip()
        if (
            not s
            or s.startswith("#!")
            or ENCODING_PATTERN.match(s)
            or s.startswith("# -*-")
        ):
            insert_index += 1
            continue
        break

    # If file is empty or only has preamble, insert header
    if insert_index >= len(lines):
        if not first_year.isdigit():
            first_year = str(CURRENT_YEAR)
        year_str = (
            f"{first_year}–{CURRENT_YEAR}"
            if first_year != str(CURRENT_YEAR)
            else first_year
        )
        header_lines = build_header(year_str, author, license_id)
        new_lines = lines[:insert_index] + header_lines + [""] + lines[insert_index:]
        file_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        return

    # Check if existing header present at insert_index
    m = HEADER_PATTERN.match(lines[insert_index])
    if m:
        orig_first = m.group(1)
        existing_last = m.group(2) or orig_first
        existing_author = m.group(3)

        # Update year range if needed
        if str(CURRENT_YEAR) != existing_last:
            new_year = (
                f"{orig_first}–{CURRENT_YEAR}"
                if orig_first != str(CURRENT_YEAR)
                else str(CURRENT_YEAR)
            )
            lines[insert_index] = f"# Copyright (c) {new_year} {existing_author}"

        # SPDX line is expected immediately after header
        spdx_index = insert_index + 1
        has_spdx = spdx_index < len(lines) and lines[spdx_index].startswith(
            "# SPDX-License-Identifier:"
        )
        if license_id != "NOASSERTION":
            if has_spdx:
                lines[spdx_index] = f"# SPDX-License-Identifier: {license_id}"
            else:
                lines.insert(spdx_index, f"# SPDX-License-Identifier: {license_id}")
        else:
            if not has_spdx:
                lines.insert(spdx_index, "# SPDX-License-Identifier: NOASSERTION")

        file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    # No existing header found — insert one before insert_index
    if not first_year.isdigit():
        first_year = str(CURRENT_YEAR)
    year_str = (
        f"{first_year}–{CURRENT_YEAR}"
        if first_year != str(CURRENT_YEAR)
        else first_year
    )
    header_lines = build_header(year_str, author, license_id)
    new_lines = lines[:insert_index] + header_lines + [""] + lines[insert_index:]
    file_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    license_id = get_license_spdx()
    for file in sys.argv[1:]:
        if file.endswith(".py"):
            update_header(Path(file), license_id)
