"""Data validation tests for BLS job data."""
import re
from pathlib import Path

import pytest

REQUIRED_FIELDS = [
    "year",
    "Region_Type",
    "Region",
    "SOC_Code",
    "OCC_TITLE",
    "SOC_Major_Group_Name",
    "TOT_EMP",
    "A_MEAN",
    "GDP",
    "complexity_score",
]

VALID_REGION_TYPES = {"National", "State", "Metro"}


@pytest.mark.data
class TestJobDataFileFormat:
    """Test that job_data.js file is properly formatted."""

    def test_file_exists(self, project_root):
        assert (project_root / "data" / "job_data.js").exists()

    def test_file_contains_window_bls_data(self, project_root):
        content = (project_root / "data" / "job_data.js").read_text()
        assert "window.BLS_DATA" in content

    def test_file_contains_job_data_array(self, project_root):
        content = (project_root / "data" / "job_data.js").read_text()
        assert "jobData:" in content

    def test_data_parses_successfully(self, job_data):
        assert isinstance(job_data, list)
        assert len(job_data) > 0


@pytest.mark.data
class TestRequiredFields:
    """Test that all records have required fields."""

    def test_all_required_fields_present(self, job_data):
        for i, record in enumerate(job_data):
            for field in REQUIRED_FIELDS:
                assert field in record, (
                    f"Record {i} missing field '{field}': {record.get('OCC_TITLE', 'unknown')}"
                )

    def test_no_null_required_fields(self, job_data):
        for i, record in enumerate(job_data):
            for field in REQUIRED_FIELDS:
                assert record[field] is not None, (
                    f"Record {i} has null '{field}': {record.get('OCC_TITLE', 'unknown')}"
                )


@pytest.mark.data
class TestFieldTypes:
    """Test that fields have correct types."""

    def test_year_is_integer(self, job_data):
        for record in job_data:
            assert isinstance(record["year"], int), f"year should be int: {record['year']}"

    def test_region_type_is_string(self, job_data):
        for record in job_data:
            assert isinstance(record["Region_Type"], str)

    def test_tot_emp_is_number(self, job_data):
        for record in job_data:
            assert isinstance(record["TOT_EMP"], (int, float))

    def test_a_mean_is_number(self, job_data):
        for record in job_data:
            assert isinstance(record["A_MEAN"], (int, float))

    def test_gdp_is_number(self, job_data):
        for record in job_data:
            assert isinstance(record["GDP"], (int, float))

    def test_complexity_score_is_number(self, job_data):
        for record in job_data:
            assert isinstance(record["complexity_score"], (int, float))


@pytest.mark.data
class TestNumericRanges:
    """Test that numeric fields are within valid ranges."""

    def test_year_range(self, job_data):
        for record in job_data:
            assert 2015 <= record["year"] <= 2030, f"year out of range: {record['year']}"

    def test_employment_positive(self, job_data):
        for record in job_data:
            assert record["TOT_EMP"] > 0, (
                f"TOT_EMP should be positive: {record['OCC_TITLE']}"
            )

    def test_wage_positive(self, job_data):
        for record in job_data:
            assert record["A_MEAN"] > 0, (
                f"A_MEAN should be positive: {record['OCC_TITLE']}"
            )

    def test_gdp_positive(self, job_data):
        for record in job_data:
            assert record["GDP"] > 0, f"GDP should be positive: {record['OCC_TITLE']}"

    def test_complexity_score_range(self, job_data):
        for record in job_data:
            assert 0 <= record["complexity_score"] <= 1, (
                f"complexity_score should be 0-1: {record['OCC_TITLE']} = {record['complexity_score']}"
            )


@pytest.mark.data
class TestBusinessLogic:
    """Test business logic and data integrity."""

    def test_region_type_values(self, job_data):
        for record in job_data:
            assert record["Region_Type"] in VALID_REGION_TYPES, (
                f"Invalid Region_Type: {record['Region_Type']}"
            )

    def test_soc_code_format(self, job_data):
        pattern = re.compile(r"^\d{2}-\d{4}$")
        for record in job_data:
            assert pattern.match(record["SOC_Code"]), (
                f"Invalid SOC_Code format: {record['SOC_Code']}"
            )

    def test_gdp_approximately_correct(self, job_data):
        """GDP should approximately equal TOT_EMP * A_MEAN (allow 10% tolerance for rounding)."""
        for record in job_data:
            expected_gdp = record["TOT_EMP"] * record["A_MEAN"]
            tolerance = expected_gdp * 0.10
            assert abs(record["GDP"] - expected_gdp) <= tolerance, (
                f"GDP mismatch for {record['OCC_TITLE']}: "
                f"expected ~{expected_gdp}, got {record['GDP']}"
            )

    def test_no_duplicate_records(self, job_data):
        seen = set()
        for record in job_data:
            key = (record["year"], record["Region"], record["SOC_Code"])
            assert key not in seen, f"Duplicate record: {key}"
            seen.add(key)
