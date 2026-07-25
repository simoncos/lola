"""CLI for the LoLA-2016 dataset toolkit."""

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="lola_dataset", description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    v = sub.add_parser("validate", help="integrity checks -> JSON report")
    v.add_argument("--db", required=True, help="path to lola.db")
    v.add_argument("--out", help="output JSON path (default: stdout)")
    v.add_argument(
        "--strict",
        action="store_true",
        help="exit non-zero when a publication quality gate fails",
    )

    s = sub.add_parser("stats", help="data-card statistics -> JSON report")
    s.add_argument("--db", required=True, help="path to lola.db")
    s.add_argument("--out", help="output JSON path (default: stdout)")

    e = sub.add_parser("export", help="pseudonymized Parquet export")
    e.add_argument("--db", required=True, help="path to lola.db")
    e.add_argument("--out", required=True, help="output directory")
    salt = e.add_mutually_exclusive_group(required=True)
    salt.add_argument(
        "--salt-file",
        help="private file containing the HMAC key (recommended; >=16 chars)",
    )
    salt.add_argument(
        "--salt",
        help="private HMAC key (>=16 chars; visible in the process list)",
    )

    return p


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "validate":
        from . import validate

        validate.main(args.db, args.out, strict=args.strict)
    elif args.command == "stats":
        from . import stats

        stats.main(args.db, args.out)
    elif args.command == "export":
        from . import export

        secret = args.salt
        if args.salt_file:
            secret = Path(args.salt_file).expanduser().read_text().strip()
        export.main(args.db, args.out, secret)


if __name__ == "__main__":
    main()
