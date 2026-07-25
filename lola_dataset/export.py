"""Export ``lola.db`` to a publication-oriented Parquet bundle.

The export is pseudonymized, not anonymous. Player names and raw API JSON are
excluded, player IDs are replaced by keyed hashes, and the source database is
never modified.

``FrameKillEvent`` is normalized into two tables:

* ``kill_events``: one row per ``(match_id, happen, victim)`` event key;
* ``kill_assists``: zero or more distinct assist links for each event key.

This preserves the crawler's one-row-per-assist representation instead of
misclassifying assist rows as duplicate kills.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import platform
import shutil
import sqlite3
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from . import __version__
from .provenance import dependency_versions, git_state, source_tree_identity
from .validate import validate

CHUNK_ROWS = 500_000
HASH_HEX_CHARS = 32  # 128-bit pseudonymous ID; salt remains private.


@dataclass(frozen=True)
class ExportSpec:
    sql: str
    pseudonymize: tuple[str, ...] = ()


EXPORTS: dict[str, ExportSpec] = {
    "matches": ExportSpec("SELECT match_id, version, duration FROM Match"),
    "teams": ExportSpec(
        "SELECT match_id, side, dragon_kills, baron_kills, win FROM Team"
    ),
    "team_bans": ExportSpec("SELECT match_id, side, ban FROM TeamBan"),
    "participants": ExportSpec("SELECT * FROM Participant", ("summoner_id",)),
    "participant_timelines": ExportSpec(
        "SELECT * FROM ParticipantTimeline", ("summoner_id",)
    ),
    "kill_events": ExportSpec(
        """
        SELECT match_id, happen, victim,
               MIN(minute) AS minute, MIN(killer) AS killer
        FROM FrameKillEvent
        GROUP BY match_id, happen, victim
        """
    ),
    "kill_assists": ExportSpec(
        """
        SELECT DISTINCT match_id, happen, victim, assist
        FROM FrameKillEvent
        WHERE assist IS NOT NULL
        """
    ),
    "summoners": ExportSpec("SELECT summoner_id FROM Summoner", ("summoner_id",)),
}


def _anon(value: str | None, salt: str) -> str | None:
    if value is None:
        return None
    return hmac.new(
        salt.encode("utf-8"), str(value).encode("utf-8"), hashlib.sha256
    ).hexdigest()[:HASH_HEX_CHARS]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_parquet_stream(
    conn: sqlite3.Connection,
    spec: ExportSpec,
    target: Path,
    salt: str,
    version_map: pd.DataFrame | None,
) -> tuple[int, list[str]]:
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as exc:  # pragma: no cover - exercised by environment checks
        raise RuntimeError(
            "Parquet export requires pyarrow; install the repository dependencies"
        ) from exc

    writer = None
    schema = None
    rows = 0
    columns: list[str] = []
    try:
        for chunk in pd.read_sql(spec.sql, conn, chunksize=CHUNK_ROWS):
            for column in spec.pseudonymize:
                chunk[column] = chunk[column].map(lambda value: _anon(value, salt))
            if (
                version_map is not None
                and "match_id" in chunk.columns
                and "version" not in chunk.columns
            ):
                chunk["match_id"] = chunk["match_id"].astype(str)
                chunk = chunk.merge(version_map, on="match_id", how="left", validate="many_to_one")
            columns = list(chunk.columns)
            table = pa.Table.from_pandas(chunk, preserve_index=False, schema=schema)
            if writer is None:
                schema = table.schema
                writer = pq.ParquetWriter(target, schema, compression="zstd")
            writer.write_table(table)
            rows += len(chunk)
    finally:
        if writer is not None:
            writer.close()
    return rows, columns


def export(db_path: str, out_dir: str, salt: str, with_version: bool = True) -> None:
    if not salt or len(salt) < 16:
        raise SystemExit("the HMAC key must be at least 16 characters; keep it private")

    db = Path(db_path).expanduser().resolve()
    audit = validate(str(db))
    if not audit["quality_gates"]["ok"]:
        raise RuntimeError(
            "source database failed publication quality gates: "
            + "; ".join(audit["quality_gates"]["errors"])
        )

    out = Path(out_dir).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and any(out.iterdir()):
        raise FileExistsError(f"refusing to overwrite non-empty export directory: {out}")
    if out.exists():
        out.rmdir()

    staging = Path(tempfile.mkdtemp(prefix=f".{out.name}.staging-", dir=out.parent))
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        version_map = None
        if with_version:
            version_map = pd.read_sql("SELECT match_id, version FROM Match", conn)
            version_map["match_id"] = version_map["match_id"].astype(str)

        outputs: dict[str, dict] = {}
        for name, spec in EXPORTS.items():
            target = staging / f"{name}.parquet"
            rows, columns = _write_parquet_stream(
                conn, spec, target, salt=salt, version_map=version_map
            )
            if rows == 0:
                raise RuntimeError(f"required export table is empty: {name}")
            outputs[name] = {
                "file": target.name,
                "rows": rows,
                "columns": columns,
                "sha256": _sha256(target),
            }
            print(f"  {name}: {rows:,} rows -> {target}")

        validation_path = staging / "validation.json"
        validation_path.write_text(
            json.dumps(audit, indent=2, ensure_ascii=False) + "\n"
        )

        state = git_state()
        manifest = {
            "format_version": 2,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "toolkit_version": __version__,
            "git_commit": state["commit"],
            "git_dirty": state["dirty"],
            "git_status_sha256": state["status_sha256"],
            "source_tree": source_tree_identity(),
            "python": platform.python_version(),
            "dependencies": dependency_versions(),
            "source": {
                "file": db.name,
                "bytes": db.stat().st_size,
                "sha256": _sha256(db),
            },
            "pseudonymization": {
                "algorithm": "HMAC-SHA-256",
                "hash_bits": HASH_HEX_CHARS * 4,
                "salt_included": False,
            },
            "quality_gates": audit["quality_gates"],
            "validation_report": {
                "file": validation_path.name,
                "sha256": _sha256(validation_path),
            },
            "outputs": outputs,
        }
        (staging / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
        )
        staging.replace(out)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    finally:
        conn.close()
    print("done. Never publish the salt or the original lola.db.")


def main(db: str, out: str, salt: str) -> None:
    export(db, out, salt)
