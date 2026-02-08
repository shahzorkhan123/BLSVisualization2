"""Tests for the data pipeline."""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from scripts.pipeline import config, db, import_csv, export_csv, export_jsonp, export_split, validate


@pytest.fixture
def tmp_db():
    """Create a temporary SQLite database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    conn = db.connect(db_path)
    db.create_schema(conn)
    yield conn
    conn.close()
    db_path.unlink(missing_ok=True)


@pytest.fixture
def populated_db(tmp_db):
    """Import all data into a temporary database."""
    import_csv.import_all(tmp_db, year=2024)
    tmp_db.commit()
    db.compute_complexity_scores(tmp_db)
    return tmp_db


class TestConfig:
    """Test configuration module."""

    def test_countries_defined(self):
        assert "USA" in config.COUNTRIES
        assert config.COUNTRIES["USA"]["code_system"] == "SOC"

    def test_metro_stem(self):
        result = config.metro_stem("new_york_newark_jersey_city_occupational_data.csv")
        assert result == "new_york_newark_jersey_city"

    def test_country_for_us_metro(self):
        assert config.country_for_metro("chicago_naperville_elgin") == "USA"

    def test_country_for_international_metro(self):
        assert config.country_for_metro("london") == "GBR"
        assert config.country_for_metro("mumbai") == "IND"
        assert config.country_for_metro("cairo") == "EGY"

    def test_display_name_for_state(self):
        assert config.display_name_for_state("california") == "California"
        assert config.display_name_for_state("new_york") == "New York"

    def test_display_name_for_metro(self):
        name = config.display_name_for_metro("new_york_newark_jersey_city")
        assert "New York" in name


class TestCodeDetection:
    """Test occupation code system detection."""

    def test_soc_detection(self):
        assert import_csv.detect_code_system("11-0000") == "SOC"
        assert import_csv.detect_code_system("53-7062") == "SOC"

    def test_isco_detection(self):
        assert import_csv.detect_code_system("OC1") == "ISCO"
        assert import_csv.detect_code_system("OC9") == "ISCO"

    def test_unknown_code_raises(self):
        with pytest.raises(ValueError):
            import_csv.detect_code_system("INVALID")


class TestMajorGroupDerivation:
    """Test major group name derivation."""

    def test_soc_major_group(self):
        result = import_csv.derive_major_group("11-0000", "Management", "SOC")
        assert result == "Management"

    def test_soc_lookup(self):
        result = import_csv.derive_major_group("15-1234", "Software Dev", "SOC")
        assert result == "Computer and Mathematical"

    def test_isco_uses_title(self):
        result = import_csv.derive_major_group("OC1", "Managers", "ISCO")
        assert result == "Managers"


class TestDatabase:
    """Test database operations."""

    def test_schema_creation(self, tmp_db):
        tables = tmp_db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        table_names = [t[0] for t in tables]
        assert "countries" in table_names
        assert "regions" in table_names
        assert "occupations" in table_names

    def test_ensure_country(self, tmp_db):
        cid = db.ensure_country(tmp_db, "USA", "United States", "SOC", "USD")
        assert cid > 0
        # Calling again should return same id
        cid2 = db.ensure_country(tmp_db, "USA", "United States", "SOC", "USD")
        assert cid == cid2

    def test_ensure_region(self, tmp_db):
        cid = db.ensure_country(tmp_db, "USA", "United States", "SOC")
        rid = db.ensure_region(tmp_db, cid, "California", "State")
        assert rid > 0

    def test_insert_occupation(self, tmp_db):
        cid = db.ensure_country(tmp_db, "USA", "United States", "SOC")
        rid = db.ensure_region(tmp_db, cid, "United States", "National")
        db.insert_occupation(
            tmp_db, 2024, rid, "11-0000", "Management",
            "Management", 9270, 126480,
        )
        tmp_db.commit()
        row = tmp_db.execute("SELECT gdp FROM occupations").fetchone()
        assert row[0] == 9270 * 126480

    def test_complexity_computation(self, tmp_db):
        cid = db.ensure_country(tmp_db, "USA", "United States", "SOC")
        rid = db.ensure_region(tmp_db, cid, "United States", "National")
        # Insert two records with different GDPs
        db.insert_occupation(tmp_db, 2024, rid, "11-0000", "Mgmt", "Mgmt", 100, 100)
        db.insert_occupation(tmp_db, 2024, rid, "13-0000", "Biz", "Biz", 200, 200)
        tmp_db.commit()
        db.compute_complexity_scores(tmp_db)
        rows = tmp_db.execute(
            "SELECT occupation_code, complexity_score FROM occupations "
            "ORDER BY occupation_code"
        ).fetchall()
        # 11-0000: gdp=10000 (min) -> 0.0
        # 13-0000: gdp=40000 (max) -> 1.0
        assert rows[0][1] == 0.0
        assert rows[1][1] == 1.0


class TestImport:
    """Test CSV import."""

    def test_import_us_national(self, tmp_db):
        count = import_csv.import_national(tmp_db, "USA", 2024)
        tmp_db.commit()
        assert count == 10

    def test_import_states(self, tmp_db):
        count = import_csv.import_national(tmp_db, "USA", 2024)
        count = import_csv.import_states(tmp_db, "USA", 2024)
        tmp_db.commit()
        assert count == 500  # 50 states * 10 occupations

    def test_import_all(self, tmp_db):
        count = import_csv.import_all(tmp_db, 2024)
        tmp_db.commit()
        assert count > 700  # At least US data


class TestExport:
    """Test export functionality."""

    def test_export_csv(self, populated_db):
        results = export_csv.export_all(populated_db)
        assert results["combined_data.csv"] > 0
        assert results["us_national.csv"] == 10
        assert results["us_by_state.csv"] == 500

        # Check files exist
        assert (config.EXPORT_DIR / "combined_data.csv").exists()

    def test_export_jsonp(self, populated_db):
        with tempfile.NamedTemporaryFile(
            suffix=".js", delete=False, mode="w"
        ) as f:
            out_path = Path(f.name)

        try:
            count = export_jsonp.export_jsonp(
                populated_db, ["USA"], out_path
            )
            assert count == 720
            content = out_path.read_text(encoding="utf-8")
            assert "window.BLS_DATA" in content
            assert "jobData:" in content
        finally:
            out_path.unlink(missing_ok=True)


class TestValidation:
    """Test validation checks."""

    def test_validate_db_passes(self, populated_db):
        errors = validate.validate_db(populated_db)
        assert errors == []

    def test_validate_jsonp_passes(self):
        errors = validate.validate_jsonp()
        assert errors == [], f"JSONP validation errors: {errors}"

    def test_validate_db_catches_bad_data(self, tmp_db):
        db.create_schema(tmp_db)
        errors = validate.validate_db(tmp_db)
        assert any("No occupation records" in e for e in errors)


class TestExportSplit:
    """Test split data export (meta.js + per-region files)."""

    def test_export_split_creates_files(self, populated_db):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir)
            stats = export_split.export_split(populated_db, ["USA"], out)
            assert stats["region_count"] == 72
            assert stats["occ_count"] == 10
            assert (out / "meta.js").exists()
            region_files = list((out / "regions").glob("*.data.js"))
            assert len(region_files) == 72

    def test_meta_structure(self, populated_db):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir)
            export_split.export_split(populated_db, ["USA"], out)
            content = (out / "meta.js").read_text(encoding="utf-8")
            assert content.startswith("window.BLS_META = ")
            assert content.rstrip().endswith(";")

            # Parse the JSON portion
            import json
            json_str = content.replace("window.BLS_META = ", "").rstrip().rstrip(";")
            meta = json.loads(json_str)
            assert meta["years"] == [2024]
            assert len(meta["occ"]) == 10
            assert "National" in meta["regions"]
            assert "State" in meta["regions"]
            assert "Metro" in meta["regions"]
            assert len(meta["regions"]["State"]) == 50

    def test_region_file_compact_format(self, populated_db):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir)
            export_split.export_split(populated_db, ["USA"], out)
            # Check a specific region file
            ca_file = out / "regions" / "2024.state-california.us.data.js"
            assert ca_file.exists()
            content = ca_file.read_text(encoding="utf-8")
            assert content.startswith("window.BLS_LOAD(")
            assert content.rstrip().endswith(");")

            # Parse the array
            import json
            json_str = content.replace("window.BLS_LOAD(", "").rstrip().rstrip(";").rstrip(")")
            rows = json.loads(json_str)
            assert len(rows) == 10
            # Each row: [occ_index, employment, wage, gdp, complexity]
            for row in rows:
                assert len(row) == 5
                assert isinstance(row[0], int)  # occ_index

    def test_all_manifest_files_exist(self, populated_db):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir)
            export_split.export_split(populated_db, ["USA"], out)

            import json
            content = (out / "meta.js").read_text(encoding="utf-8")
            json_str = content.replace("window.BLS_META = ", "").rstrip().rstrip(";")
            meta = json.loads(json_str)

            for region_type, entries in meta["regions"].items():
                for slug, _name, country in entries:
                    for year in meta["years"]:
                        filename = f"{year}.{slug}.{country}.data.js"
                        filepath = out / "regions" / filename
                        assert filepath.exists(), f"Missing: {filename}"

    def test_slug_generation(self):
        assert export_split._make_slug("State", "California") == "state-california"
        assert export_split._make_slug("State", "New York") == "state-new_york"
        assert export_split._make_slug("National", "United States") == "national-united_states"
        assert export_split._make_slug("Metro", "Atlanta-Sandy Springs-Alpharetta, GA") == "metro-atlanta"
        assert export_split._make_slug("Metro", "St. Louis, MO-IL") == "metro-st_louis"
        assert export_split._make_slug("Metro", "New York-Newark-Jersey City, NY-NJ-PA") == "metro-new_york"
        assert export_split._make_slug("Metro", "Minneapolis-St. Paul-Bloomington, MN-WI") == "metro-minneapolis"
