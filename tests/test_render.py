from datamonitor.render import render_dashboard


def test_render_dashboard_contains_key_sections(monitor):
    snapshot = monitor.snapshot()

    output = render_dashboard(snapshot, "2026-04-16 09:32:15")

    assert "2026-04-16 09:32:15" in output
    assert "데이터 모니터링 Tool" in output
    assert "RESERVED" in output
    assert "실리콘 웨이퍼-8인치" in output
    assert "고갈" in output
    assert "부족" in output
    assert "여유" in output


def test_render_dashboard_shows_totals(monitor):
    snapshot = monitor.snapshot()

    output = render_dashboard(snapshot, "2026-04-16 09:32:15")

    assert f"{snapshot['sample_count']:>3}종" in output
    assert f"{snapshot['total_orders']:>3}건" in output
