"""Run-manifest helpers for research outputs."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from . import __version__


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_PATTERNS = (
    "lola_dataset/**/*.py",
    "benchmarks/**/*.py",
    "analysis/**/*.py",
    "pyproject.toml",
    "uv.lock",
)


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def git_state() -> dict[str, str | bool | None]:
    """Return a non-ambiguous summary when a run uses a dirty worktree."""
    try:
        status = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return {"commit": git_commit(), "dirty": None, "status_sha256": None}
    return {
        "commit": git_commit(),
        "dirty": bool(status),
        "status_sha256": hashlib.sha256(status.encode("utf-8")).hexdigest(),
    }


def source_tree_identity() -> dict[str, str | int | list[str]]:
    """Fingerprint executable project sources, including untracked scripts."""
    paths: set[Path] = set()
    for pattern in SOURCE_PATTERNS:
        paths.update(path for path in PROJECT_ROOT.glob(pattern) if path.is_file())
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.relative_to(PROJECT_ROOT).as_posix()):
        relative = path.relative_to(PROJECT_ROOT).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(sha256_file(path)))
        digest.update(b"\0")
    return {
        "algorithm": "SHA-256(path + file SHA-256)",
        "patterns": list(SOURCE_PATTERNS),
        "files": len(paths),
        "sha256": digest.hexdigest(),
    }


def dependency_versions() -> dict[str, str | None]:
    result: dict[str, str | None] = {}
    for package in ["pandas", "pyarrow", "numpy", "scipy", "scikit-learn", "matplotlib"]:
        try:
            result[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            result[package] = None
    return result


def file_identity(path: str | Path) -> dict:
    resolved = Path(path).expanduser().resolve()
    return {
        "file": resolved.name,
        "bytes": resolved.stat().st_size,
        "sha256": sha256_file(resolved),
    }


def write_run_manifest(
    out_dir: str | Path,
    run_name: str,
    parameters: dict,
    inputs: list[str | Path],
    outputs: list[str | Path],
) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    state = git_state()
    manifest = {
        "run_name": run_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "toolkit_version": __version__,
        "git_commit": state["commit"],
        "git_dirty": state["dirty"],
        "git_status_sha256": state["status_sha256"],
        "source_tree": source_tree_identity(),
        "python": platform.python_version(),
        "dependencies": dependency_versions(),
        "parameters": parameters,
        "inputs": [file_identity(path) for path in inputs],
        "outputs": [file_identity(path) for path in outputs],
    }
    target = out / f"{run_name}.run.json"
    target.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    return target
