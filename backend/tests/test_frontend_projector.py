"""Check that the Goals page stays focused and the projector uses saved plans."""

import json
from pathlib import Path


FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
APP_SOURCE = (FRONTEND_DIR / "app.js").read_text()
INDEX_SOURCE = (FRONTEND_DIR / "index.html").read_text()
BOOTSTRAP_SOURCE = (FRONTEND_DIR / "bootstrap.js").read_text()
APP_CONFIG = json.loads((FRONTEND_DIR / "app-config.json").read_text())


def test_goals_page_keeps_progress_and_logs_without_chart_code() -> None:
    """Keep the short Goals page focused on progress and monthly updates."""
    goals_start = APP_SOURCE.index("function renderGoalHistoryTable")
    debts_start = APP_SOURCE.index("// This function lists debts")
    goals_code = APP_SOURCE[goals_start:debts_start]

    assert "<canvas" not in goals_code
    assert "window.Chart" not in goals_code
    assert "renderGoalCharts" not in goals_code
    assert "Chance with your plan:" in goals_code
    assert "Chance with your real investments:" in goals_code
    assert "Update this month's investment" in goals_code
    assert "Previous updates" in goals_code
    assert "Download CSV" in goals_code
    assert "Edit goals" in goals_code


def test_projector_has_a_friendly_empty_state_and_saved_plan_controls() -> None:
    """Show the Step 4 link when no plan is saved and expose simple controls."""
    assert "You have not chosen your investments yet." in APP_SOURCE
    assert "Choose my investments" in APP_SOURCE
    assert 'navigate("investment-choices")' in APP_SOURCE
    assert 'apiRequest("/plan", { cache: "no-store" })' in APP_SOURCE
    assert "`/plan/projector?years=${projectorYears}`" in APP_SOURCE
    assert 'id="projector-years"' in APP_SOURCE
    assert 'id="projector-scenario"' in APP_SOURCE
    assert "Each growth number is an assumption, not a promise." in APP_SOURCE


def test_reports_page_has_thirteen_data_sections_and_real_download_actions() -> None:
    """Keep the full report on backend data with chart and file-download controls."""
    for heading in (
        "1. COVER AND SUMMARY",
        "2. YOUR PROFILE TODAY",
        "3. YOUR JOURNEY SO FAR",
        "4. PAST VS PRESENT",
        "5. YOUR INVESTMENT PLAN",
        "6. GOALS",
        "7. DEBTS",
        "8. INVESTMENT LOG",
        "9. FUTURE OUTLOOK",
        "10. WARNINGS AND ALERTS",
        "11. ACTION PLAN",
        "12. MARKET SNAPSHOT",
        "13. HOW WE CALCULATED",
    ):
        assert heading in APP_SOURCE
    assert "`/report/data?period=${encodeURIComponent(reportPeriod)}`" in APP_SOURCE
    assert "`/report/pdf?period=${encodeURIComponent(reportPeriod)}`" in APP_SOURCE
    assert "`/report/csv?period=${encodeURIComponent(reportPeriod)}`" in APP_SOURCE
    assert "Download PDF" in APP_SOURCE
    assert "Download data (CSV)" in APP_SOURCE
    assert "report-meaning" in APP_SOURCE
    assert "report-future-chart" in APP_SOURCE


def test_developer_credit_is_shared_across_login_dashboard_about_and_report() -> None:
    """Keep the one configured credit visible on public and signed-in pages."""
    credit = APP_CONFIG["APP_CREDIT"]
    assert credit == "ArthMitra is developed by CTR-SREC-HUB"
    assert 'id="app-credit"' in INDEX_SOURCE
    assert "config.APP_CREDIT" in BOOTSTRAP_SOURCE
    assert 'class="app-credit">${escapeHtml(APP_CREDIT)}' in APP_SOURCE
    assert 'about: "About ArthMitra"' in APP_SOURCE
    assert "function showAbout()" in APP_SOURCE
    assert 'report.app_credit || APP_CREDIT' in APP_SOURCE
    assert 'document.querySelector(\'meta[name="author"]\').content = config.APP_CREDIT' in BOOTSTRAP_SOURCE
