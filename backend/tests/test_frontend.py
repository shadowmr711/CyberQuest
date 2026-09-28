def test_index_route(client):
    """Test that index page loads successfully and contains CyberQuest elements."""
    res = client.get("/")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "CyberQuest" in html
    assert "Command Center Telemetry" in html
    assert "data-view=\"dashboard\"" in html
    assert "data-view=\"learning-path\"" in html
    assert "data-view=\"practice-lab\"" in html
    assert "data-view=\"labs\"" in html
    assert "data-view=\"analytics\"" in html
    assert "data-view=\"projects\"" in html
    assert "data-view=\"profile\"" in html

def test_static_assets_served(client):
    """Test that CSS and JS files are served with proper MIME types."""
    css_res = client.get("/static/css/main.css")
    assert css_res.status_code == 200
    assert "CyberQuest" in css_res.get_data(as_text=True)

    js_res = client.get("/static/js/app.js")
    assert js_res.status_code == 200
    assert "DIAGNOSTIC_QUESTIONS" in js_res.get_data(as_text=True)
