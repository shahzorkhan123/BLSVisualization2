"""CLI orchestrator for the BLS data pipeline."""

import argparse
import sys
from pathlib import Path

# Add project root to path so we can run as script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from scripts.pipeline import config, db, import_csv, export_csv, export_jsonp, export_split, validate


def main():
    parser = argparse.ArgumentParser(
        description="BLS Data Pipeline: CSV -> SQLite -> CSV/JSONP"
    )
    parser.add_argument(
        "--year", type=int, default=2024,
        help="Data year (default: 2024)",
    )
    parser.add_argument(
        "--fresh", action="store_true",
        help="Drop and recreate all tables before import",
    )
    parser.add_argument(
        "--import-only", action="store_true",
        help="Only import CSVs into SQLite (skip export)",
    )
    parser.add_argument(
        "--export-only", action="store_true",
        help="Only export from existing SQLite (skip import)",
    )
    parser.add_argument(
        "--export-country", nargs="+", default=None,
        help="Country codes to include in JSONP export (default: USA only)",
    )
    parser.add_argument(
        "--skip-csv-export", action="store_true",
        help="Skip generating intermediate CSV files",
    )
    parser.add_argument(
        "--db-path", type=str, default=None,
        help=f"SQLite database path (default: {config.DB_PATH})",
    )

    args = parser.parse_args()
    db_path = Path(args.db_path) if args.db_path else config.DB_PATH
    export_countries = args.export_country or ["USA"]

    print(f"=== BLS Data Pipeline ===")
    print(f"  Year: {args.year}")
    print(f"  DB: {db_path}")
    print(f"  Export countries: {', '.join(export_countries)}")
    print()

    conn = db.connect(db_path)

    try:
        # --- IMPORT PHASE ---
        if not args.export_only:
            if args.fresh:
                print("Dropping existing tables...")
                db.drop_all(conn)

            print("Creating schema...")
            db.create_schema(conn)

            print(f"\nImporting data for year {args.year}...")
            total = import_csv.import_all(conn, args.year)
            conn.commit()
            print(f"\nTotal imported: {total} records")

            print("\nComputing complexity scores (GDP normalization)...")
            db.compute_complexity_scores(conn)

            # Validate DB
            print("\nValidating database...")
            errors = validate.validate_db(conn)
            if errors:
                print("  VALIDATION ERRORS:")
                for e in errors:
                    print(f"    - {e}")
            else:
                print("  Database validation passed")

            # Print summary
            print("\nSummary:")
            for row in db.get_summary(conn):
                print(f"  {row['country_code']} {row['region_type']}: "
                      f"{row['record_count']} records")

        if args.import_only:
            print("\n--import-only: skipping export")
            return

        # --- EXPORT PHASE ---
        if not args.skip_csv_export:
            print("\nExporting intermediate CSVs...")
            csv_results = export_csv.export_all(conn)
            for filename, count in csv_results.items():
                print(f"  {filename}: {count} rows")

        print(f"\nExporting JSONP (countries: {', '.join(export_countries)})...")
        record_count = export_jsonp.export_jsonp(conn, export_countries)
        print(f"  {config.JSONP_PATH.name}: {record_count} records")

        print(f"\nExporting split files (meta.js + per-region)...")
        split_stats = export_split.export_split(conn, export_countries)
        print(f"  meta.js: {split_stats['occ_count']} occupations")
        print(f"  regions/: {split_stats['region_count']} files")

        # Validate JSONP output
        print("\nValidating JSONP output...")
        errors = validate.validate_jsonp()
        if errors:
            print("  VALIDATION ERRORS:")
            for e in errors:
                print(f"    - {e}")
            sys.exit(1)
        else:
            print("  JSONP validation passed")

        print(f"\nPipeline complete! {record_count} records in "
              f"{config.JSONP_PATH.name}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
