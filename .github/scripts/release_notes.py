"""Derive a GitHub Release title and body for a tag from a package's CHANGELOG.

Adapted from bootstack's script of the same name, with one difference: this
repository publishes eighteen distributions, so the changelog is passed in
rather than assumed to be ``./CHANGELOG.md``, and the release title carries the
distribution name. Seventeen releases titled only ``1.1.0`` would be unreadable
on a shared releases page.

Changelogs use ``## [<version>] — <descriptive title>`` headings. The release
shows ``<distribution> <version> — <descriptive title>`` as its *title*, and the
section content *without* its heading as the *body* — so the title is not
repeated and the ``[<version>]`` heading does not render as a broken self-link.

Usage::

    python release_notes.py <changelog> <version> <body_out> <github_output> [dist]

Writes the body to ``<body_out>`` and ``title=<...>`` to ``<github_output>``
(i.e. ``$GITHUB_OUTPUT``). A version with no changelog section falls back to a
bare title and an empty body, and the workflow then relies on GitHub's
auto-generated notes.
"""
from __future__ import annotations

import re
import sys


def extract(version: str, changelog: str) -> tuple[str, str]:
    """Return ``(descriptive title, body)`` for one version's section.

    The title is the heading's suffix only — the caller prepends the
    distribution name and version.
    """
    lines = changelog.splitlines()
    start = None
    heading = ""
    for i, line in enumerate(lines):
        if line.startswith(f"## [{version}]"):
            start, heading = i, line
            break

    if start is None:
        return "", ""

    # Descriptive suffix after "## [version]", dropping a leading dash separator
    # (em-dash, en-dash, or hyphen) and surrounding whitespace.
    m = re.match(r"^## \[" + re.escape(version) + r"\]\s*[—–-]*\s*(.*)$", heading)
    suffix = m.group(1).strip() if m else ""

    body_lines: list[str] = []
    for line in lines[start + 1:]:
        if line.startswith("## ["):
            break
        body_lines.append(line)
    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)
    while body_lines and not body_lines[-1].strip():
        body_lines.pop()

    return suffix, "\n".join(body_lines)


def main() -> None:
    changelog_path, version, body_path, gh_output = sys.argv[1:5]
    dist = sys.argv[5] if len(sys.argv) > 5 else ""

    try:
        with open(changelog_path, encoding="utf-8") as f:
            suffix, body = extract(version, f.read())
    except FileNotFoundError:
        suffix, body = "", ""

    title = f"{dist} {version}".strip()
    if suffix:
        title = f"{title} — {suffix}"

    with open(body_path, "w", encoding="utf-8") as f:
        f.write(body + ("\n" if body else ""))
    with open(gh_output, "a", encoding="utf-8") as f:
        f.write(f"title={title}\n")


if __name__ == "__main__":
    main()
