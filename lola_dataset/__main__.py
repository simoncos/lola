"""CLI for the LoLA-2016 dataset toolkit."""

import argparse


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="lola_dataset", description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    v = sub.add_parser("validate", help="integrity checks -> JSON report")
    v.add_argument("--db", required=True, help="path to lola.db")
    v.add_argument("--out", help="output JSON path (default: stdout)")

    s = sub.add_parser("stats", help="data-card statistics -> JSON report")
    s.add_argument("--db", required=True, help="path to lola.db")
    s.add_argument("--out", help="output JSON path (default: stdout)")

    e = sub.add_parser("export", help="anonymized Parquet export")
    e.add_argument("--db", required=True, help="path to lola.db")
    e.add_argument("--out", required=True, help="output directory")
    e.add_argument("--salt", required=True, help="private salt for ID hashing (>=8 chars)")

    return p


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "validate":
        from . import validate

        validate.main(args.db, args.out)
    elif args.command == "stats":
        from . import stats

        stats.main(args.db, args.out)
    elif args.command == "export":
        from . import export

        export.main(args.db, args.out, args.salt)


if __name__ == "__main__":
    main()
