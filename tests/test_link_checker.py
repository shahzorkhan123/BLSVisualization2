"""Link and dependency checker tests."""
import re
from pathlib import Path

import pytest

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


@pytest.mark.links
class TestLibraryDependencies:
    """Verify all library files exist."""

    def test_plotly_exists(self, project_root):
        assert (project_root / "lib" / "plotly.min.js").exists()

    def test_jquery_exists(self, project_root):
        assert (project_root / "lib" / "jquery.min.js").exists()

    def test_d3_exists(self, project_root):
        assert (project_root / "lib" / "d3.min.js").exists()

    def test_bootstrap_css_exists(self, project_root):
        assert (project_root / "lib" / "bootstrap.min.css").exists()


@pytest.mark.links
class TestSharedComponents:
    """Verify shared component files exist."""

    def test_common_css_exists(self, project_root):
        assert (project_root / "shared" / "common.css").exists()

    def test_utils_js_exists(self, project_root):
        assert (project_root / "shared" / "utils.js").exists()

    def test_treemap_js_exists(self, project_root):
        assert (project_root / "shared" / "treemap.js").exists()


@pytest.mark.links
class TestDataFiles:
    """Verify data files exist."""

    def test_job_data_js_exists(self, project_root):
        assert (project_root / "data" / "job_data.js").exists()

    def test_job_data_js_not_empty(self, project_root):
        f = project_root / "data" / "job_data.js"
        assert f.stat().st_size > 100, "job_data.js is too small"

    def test_meta_js_exists(self, project_root):
        assert (project_root / "data" / "meta.js").exists()

    def test_regions_directory_not_empty(self, project_root):
        regions_dir = project_root / "data" / "regions"
        assert regions_dir.exists(), "data/regions/ directory missing"
        files = list(regions_dir.glob("*.data.js"))
        assert len(files) > 0, "data/regions/ has no .data.js files"


@pytest.mark.links
class TestHtmlDependencies:
    """Verify all script/link tags in active HTML files resolve to existing files."""

    ACTIVE_HTML_FILES = [
        "index.html",
        "visualizations/direct_html_job_treemap.html",
        "visualizations/direct_html_compensation_treemap.html",
        "visualizations/refined_job_space.html",
        "documentation/reproducibility.html",
    ]

    def _extract_local_refs(self, html_path, project_root):
        """Extract local script src and link href references from an HTML file."""
        content = html_path.read_text(encoding="utf-8")
        refs = []

        # Find script src attributes
        for match in re.finditer(r'<script[^>]+src=["\']([^"\']+)["\']', content):
            src = match.group(1)
            if not src.startswith(("http://", "https://", "//")):
                refs.append(src)

        # Find link href attributes (CSS)
        for match in re.finditer(
            r'<link[^>]+href=["\']([^"\']+)["\']', content
        ):
            href = match.group(1)
            if not href.startswith(("http://", "https://", "//")):
                refs.append(href)

        return refs

    def test_all_local_references_resolve(self, project_root):
        """Check that all local script/CSS references in active HTML files exist."""
        broken = []
        for rel_path in self.ACTIVE_HTML_FILES:
            html_path = project_root / rel_path
            if not html_path.exists():
                broken.append(f"HTML file missing: {rel_path}")
                continue

            refs = self._extract_local_refs(html_path, project_root)
            base_dir = html_path.parent

            for ref in refs:
                resolved = (base_dir / ref).resolve()
                if not resolved.exists():
                    broken.append(f"{rel_path} -> {ref} (not found)")

        assert not broken, f"Broken references:\n" + "\n".join(broken)

    def test_index_html_navigation_links(self, project_root):
        """Check that navigation links in index.html point to existing files."""
        content = (project_root / "index.html").read_text(encoding="utf-8")
        broken = []

        # Extract file paths from onclick handlers
        for match in re.finditer(r"showVisualization\('([^']+)'", content):
            path = match.group(1)
            if not (project_root / path).exists():
                broken.append(f"index.html onclick -> {path}")

        # Extract href links to local files
        for match in re.finditer(r'href=["\']([^"\'#]+)["\']', content):
            href = match.group(1)
            if not href.startswith(("http://", "https://", "//", "#", "javascript")):
                if not (project_root / href).exists():
                    broken.append(f"index.html href -> {href}")

        assert not broken, f"Broken links in index.html:\n" + "\n".join(broken)
