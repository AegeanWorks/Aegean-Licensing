"""Bundle the repository's licensing documents into the built Python package."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable, Tuple

RESOURCE_DIRS: Tuple[str, ...] = ("licenses", "policies")
RESOURCE_FILES: Tuple[str, ...] = (".github/workflows/cla-check.yml",)
TARGET_DIR = Path("aegean_licensing") / "resources"


def bundle_documents(repo_root: Path, destination_root: Path) -> int:
    """Copy legal documents under destination_root, returning the number of files copied."""
    target_root = Path(destination_root) / TARGET_DIR
    repo_root = Path(repo_root)
    missing = [directory for directory in RESOURCE_DIRS
               if not _has_files(repo_root / directory)]
    missing += [relative for relative in RESOURCE_FILES
                if not (repo_root / relative).is_file()]
    if missing:
        raise RuntimeError(
            "Incomplete licensing sources, refusing a partial bundle: "
            + ", ".join(missing) + "."
        )
    copied = 0
    for source in _iter_sources(repo_root):
        destination = target_root / source.relative_to(repo_root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        copied += 1
    if copied == 0:
        raise RuntimeError("No licensing documents were found to bundle into the package.")
    return copied


def _has_files(directory: Path) -> bool:
    return directory.is_dir() and any(path.is_file() for path in directory.rglob("*"))


def _iter_sources(repo_root: Path) -> Iterable[Path]:
    for directory in RESOURCE_DIRS:
        source_dir = repo_root / directory
        if source_dir.is_dir():
            for path in sorted(source_dir.rglob("*")):
                if path.is_file():
                    yield path
    for relative in RESOURCE_FILES:
        path = repo_root / relative
        if path.is_file():
            yield path
