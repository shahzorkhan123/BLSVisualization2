"""Shared test fixtures for BLS visualization tests."""
import json
import re
import subprocess
import time
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent


def parse_job_data_js(filepath):
    """Extract JSON array from JSONP-style job_data.js file."""
    content = filepath.read_text(encoding="utf-8")

    # Extract the jobData array using regex
    match = re.search(r"jobData:\s*(\[.*?\])\s*[,\n]", content, re.DOTALL)
    if not match:
        raise ValueError(f"Could not find jobData array in {filepath}")

    return json.loads(match.group(1))


@pytest.fixture(scope="session")
def project_root():
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def job_data():
    """Load and parse the job_data.js file into a list of dicts."""
    filepath = PROJECT_ROOT / "data" / "job_data.js"
    return parse_job_data_js(filepath)


@pytest.fixture(scope="session")
def local_server():
    """Start a local HTTP server for visual tests."""
    server = subprocess.Popen(
        ["python", "-m", "http.server", "8765"],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(2)  # Wait for server to start
    yield "http://localhost:8765"
    server.terminate()
    server.wait()
