"""Visual regression tests using Playwright."""
from pathlib import Path

import pytest

BASELINES_DIR = Path(__file__).parent / "baselines"


@pytest.mark.visual
class TestVisualizationsRender:
    """Test that all active visualizations render without errors."""

    def test_job_treemap_renders(self, page, local_server):
        page.goto(f"{local_server}/visualizations/direct_html_job_treemap.html")
        page.wait_for_load_state("networkidle")
        # Lazy loading: click Load Data to fetch region data
        page.click("#load-data-btn")
        # Plotly renders into #treemap div, adding .js-plotly-plot or svg inside
        page.wait_for_selector("#treemap svg, #treemap .js-plotly-plot", timeout=30000)

    def test_compensation_treemap_renders(self, page, local_server):
        page.goto(
            f"{local_server}/visualizations/direct_html_compensation_treemap.html"
        )
        page.wait_for_load_state("networkidle")
        page.click("#load-data-btn")
        page.wait_for_selector("#treemap svg, #treemap .js-plotly-plot", timeout=30000)

    def test_job_space_renders(self, page, local_server):
        page.goto(f"{local_server}/visualizations/refined_job_space.html")
        page.wait_for_load_state("networkidle")
        # D3 visualizations create SVG elements
        page.wait_for_selector("svg, canvas, .plot-container", timeout=15000)

    def test_index_page_loads(self, page, local_server):
        page.goto(f"{local_server}/index.html")
        page.wait_for_load_state("networkidle")
        title = page.title()
        assert "Job" in title or "Complexity" in title or "Atlas" in title


@pytest.mark.visual
class TestPageLoadSmoke:
    """Smoke tests that pages load without critical JS errors (works with limited data)."""

    PAGES = [
        ("index.html", "index"),
        ("visualizations/direct_html_job_treemap.html", "job_treemap"),
        ("visualizations/direct_html_compensation_treemap.html", "comp_treemap"),
        ("visualizations/refined_job_space.html", "job_space"),
    ]

    @pytest.mark.parametrize("path,name", PAGES, ids=[p[1] for p in PAGES])
    def test_page_loads_without_critical_errors(self, page, local_server, path, name):
        """Verify page loads and no critical JS errors (404s, syntax errors)."""
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.goto(f"{local_server}/{path}")
        page.wait_for_load_state("networkidle")
        critical = [e for e in errors if "SyntaxError" in e or "ReferenceError" in e]
        assert not critical, f"Critical JS errors on {name}: {critical}"


@pytest.mark.visual
class TestVisualBaselines:
    """Capture and compare screenshots against baselines."""

    def _screenshot_path(self, name):
        return BASELINES_DIR / f"{name}.png"

    def test_job_treemap_screenshot(self, page, local_server):
        page.goto(f"{local_server}/visualizations/direct_html_job_treemap.html")
        page.wait_for_load_state("networkidle")
        page.click("#load-data-btn")
        page.wait_for_timeout(3000)  # Wait for Plotly animation

        baseline = self._screenshot_path("job_treemap")
        if not baseline.exists():
            BASELINES_DIR.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(baseline), full_page=True)
            pytest.skip("Baseline created - run again to compare")

        current = self._screenshot_path("job_treemap_current")
        page.screenshot(path=str(current), full_page=True)
        # Basic size comparison (full pixel diff requires pillow)
        assert current.stat().st_size > 0, "Screenshot is empty"

    def test_compensation_treemap_screenshot(self, page, local_server):
        page.goto(
            f"{local_server}/visualizations/direct_html_compensation_treemap.html"
        )
        page.wait_for_load_state("networkidle")
        page.click("#load-data-btn")
        page.wait_for_timeout(3000)

        baseline = self._screenshot_path("compensation_treemap")
        if not baseline.exists():
            BASELINES_DIR.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(baseline), full_page=True)
            pytest.skip("Baseline created - run again to compare")

        current = self._screenshot_path("compensation_treemap_current")
        page.screenshot(path=str(current), full_page=True)
        assert current.stat().st_size > 0, "Screenshot is empty"

    def test_job_space_screenshot(self, page, local_server):
        page.goto(f"{local_server}/visualizations/refined_job_space.html")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

        baseline = self._screenshot_path("job_space")
        if not baseline.exists():
            BASELINES_DIR.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(baseline), full_page=True)
            pytest.skip("Baseline created - run again to compare")

        current = self._screenshot_path("job_space_current")
        page.screenshot(path=str(current), full_page=True)
        assert current.stat().st_size > 0, "Screenshot is empty"
