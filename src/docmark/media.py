"""Helpers for writing media next to the Markdown output."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

IMAGE_LINK_RE = re.compile(
    r"!\[([^\]]*)\]\(([^)]+)\)",
    re.MULTILINE,
)


def unique_image_name(output_dir: Path, stem: str, index: int, suffix: str) -> str:
    """Return a filename that does not collide with existing files."""
    suffix = suffix if suffix.startswith(".") else f".{suffix}"
    candidate = f"{stem}_{index:03d}{suffix.lower()}"
    counter = index
    while (output_dir / candidate).exists():
        counter += 1
        candidate = f"{stem}_{counter:03d}{suffix.lower()}"
    return candidate


def write_image_bytes(
    data: bytes,
    output_dir: Path,
    *,
    stem: str,
    index: int,
    suffix: str,
) -> Path:
    """Write image bytes into ``output_dir`` and return the saved path."""
    output_dir.mkdir(parents=True, exist_ok=True)
    name = unique_image_name(output_dir, stem, index, suffix)
    path = output_dir / name
    path.write_bytes(data)
    return path


def flatten_extracted_media(
    markdown: str,
    media_root: Path,
    output_dir: Path,
    stem: str,
) -> tuple[str, list[Path]]:
    """Move pandoc/extracted media into ``output_dir`` and rewrite links.

    All images end up beside the Markdown file, referenced by filename only.
    """
    if not media_root.exists():
        return markdown, []

    saved: list[Path] = []
    mapping: dict[str, str] = {}
    index = 1

    for path in sorted(media_root.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower() or ".bin"
        target_name = unique_image_name(output_dir, stem, index, suffix)
        target = output_dir / target_name
        shutil.copy2(path, target)
        saved.append(target)
        # Map several path forms pandoc may emit in Markdown.
        rel = path.relative_to(media_root).as_posix()
        mapping[rel] = target_name
        mapping[path.as_posix()] = target_name
        mapping[str(path)] = target_name
        mapping[f"media/{path.name}"] = target_name
        mapping[path.name] = target_name
        index += 1

    def _replace(match: re.Match[str]) -> str:
        alt, target = match.group(1), match.group(2).strip()
        # Drop optional title: path "title"
        path_part = target.split()[0].strip("\"'")
        normalized = path_part.replace("\\", "/")
        for key, name in mapping.items():
            if normalized.endswith(key) or normalized == key:
                return f"![{alt}]({name})"
        # Already a bare filename in the output dir.
        if "/" not in normalized and "\\" not in normalized:
            return match.group(0)
        # Fallback: keep basename if file was copied.
        base = Path(normalized).name
        if (output_dir / base).exists():
            return f"![{alt}]({base})"
        return match.group(0)

    rewritten = IMAGE_LINK_RE.sub(_replace, markdown)
    return rewritten, saved


def rewrite_image_links(markdown: str, mapping: dict[str, str]) -> str:
    """Rewrite image destinations using an explicit old->new filename map."""

    def _replace(match: re.Match[str]) -> str:
        alt, target = match.group(1), match.group(2).strip()
        path_part = target.split()[0].strip("\"'")
        new_name = mapping.get(path_part) or mapping.get(Path(path_part).name)
        if new_name:
            return f"![{alt}]({new_name})"
        return match.group(0)

    return IMAGE_LINK_RE.sub(_replace, markdown)
