#!/usr/bin/env python3
"""Update SESSION-STATE/TASKS.md build progress counts from task statuses."""

from __future__ import annotations

from pathlib import Path
import re
import sys


STATUS_ORDER = ("done", "in-review", "in-progress", "needs-fix", "blocked", "pending")
HTML_COMMENT_PATTERN = re.compile(r"<!--.*?-->", re.DOTALL)
ROW_PATTERN = re.compile(
    r"^\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*$",
    re.MULTILINE,
)


def compute_counts(content: str) -> dict[str, int]:
    counts = {status: 0 for status in STATUS_ORDER}
    visible_content = HTML_COMMENT_PATTERN.sub("", content)
    for line in visible_content.splitlines():
        marker = "- Status:"
        if marker not in line:
            continue
        status = line.split(marker, 1)[1].strip()
        if status in counts:
            counts[status] += 1
    return counts


def update_progress_row(content: str, counts: dict[str, int]) -> str:
    total = sum(counts.values())
    new_row = (
        f"| {total} | {counts['done']} | {counts['in-review']} | "
        f"{counts['in-progress']} | {counts['needs-fix']} | {counts['blocked']} | {counts['pending']} |"
    )
    match = ROW_PATTERN.search(content)
    if not match:
        raise RuntimeError("Could not find build progress count row in SESSION-STATE/TASKS.md")
    return content[: match.start()] + new_row + content[match.end() :]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    tasks_path = root / "SESSION-STATE" / "TASKS.md"
    if not tasks_path.exists():
        print("SESSION-STATE/TASKS.md not found. Run /parse-scope first.", file=sys.stderr)
        return 1
    content = tasks_path.read_text(encoding="utf-8")
    counts = compute_counts(content)
    updated = update_progress_row(content, counts)
    tasks_path.write_text(updated, encoding="utf-8")
    print(
        "Updated SESSION-STATE/TASKS.md counts:",
        f"total={sum(counts.values())}",
        f"done={counts['done']}",
        f"in-review={counts['in-review']}",
        f"in-progress={counts['in-progress']}",
        f"needs-fix={counts['needs-fix']}",
        f"blocked={counts['blocked']}",
        f"pending={counts['pending']}",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
