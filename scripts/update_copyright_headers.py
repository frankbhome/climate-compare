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
import re
import subprocess
import sys
from pathlib import Path

import requests

CURRENT_YEAR = datetime.datetime.now().year

HEADER_PATTERN = re.compile(r"^# Copyright \(c\) (\d{4})(?:–(\d{4}))? (.+)$")


def get_first_year(file_path: Path) -> str:
    """
    Return the year of the first commit for a file.
    Falls back to the current year if not found or invalid.
    """
    result = subprocess.run(
        ["git", "log", "--follow", "--format=%ad", "--date=format:%Y", str(file_path)],
        capture_output=True,
        text=True,
    )
    years = result.stdout.strip().split("\n")
    return years[-1] if years and years[-1].isdigit() else str(CURRENT_YEAR)


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
    authors = result.stdout.strip().split("\n")
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

    try:
        resp = requests.get(
            "https://api.github.com/repos/frankbhome/climate-compare/license", timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            license_info = data.get("license")
            if isinstance(license_info, dict):
                spdx_id = license_info.get("spdx_id")
                if isinstance(spdx_id, str):
                    return spdx_id
    except Exception:
        pass

    return "NOASSERTION"


def update_header(file_path: Path, license_id: str) -> None:
    """
    Insert or update the copyright header in a file.
    Preserves shebangs and encoding lines at the top.
    """
    lines = file_path.read_text(encoding="utf-8").splitlines()
    first_year = get_first_year(file_path)
    author = get_author(file_path)

    # Find the first non-blank, non-shebang, non-encoding line
    insert_index = 0
    while insert_index < len(lines):
        stripped = lines[insert_index].strip()
        if not stripped or stripped.startswith("#!") or stripped.startswith("# -*-"):
            insert_index += 1
        else:
            break

    # Check if the first "real" line is a copyright header
    if insert_index < len(lines):
        match = HEADER_PATTERN.match(lines[insert_index])
        if match is not None:
            orig_first = match.group(1)
            last_year = match.group(2) or orig_first
            if str(CURRENT_YEAR) != last_year:
                lines[insert_index] = (
                    f"# Copyright (c) {orig_first}–{CURRENT_YEAR} {author}"
                )
            spdx_index = insert_index + 1
            if spdx_index >= len(lines) or not lines[spdx_index].startswith(
                "# SPDX-License-Identifier:"
            ):
                lines.insert(spdx_index, f"# SPDX-License-Identifier: {license_id}")
            else:
                lines[spdx_index] = f"# SPDX-License-Identifier: {license_id}"
        else:
            # No header found — insert before the first real line
            if not first_year.isdigit():
                first_year = str(CURRENT_YEAR)
            year_str = (
                f"{first_year}–{CURRENT_YEAR}"
                if first_year != str(CURRENT_YEAR)
                else first_year
            )
            header = [
                f"# Copyright (c) {year_str} {author}",
                f"# SPDX-License-Identifier: {license_id}",
            ]
            lines = lines[:insert_index] + header + [""] + lines[insert_index:]
    else:
        # Empty file — just insert the header
        header = [
            f"# Copyright (c) {first_year} {author}",
            f"# SPDX-License-Identifier: {license_id}",
        ]
        lines = header

    file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    license_id = get_license_spdx()
    for file in sys.argv[1:]:
        if file.endswith(".py"):
            update_header(Path(file), license_id)
