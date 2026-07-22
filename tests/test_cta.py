from render.cta import render_cta


def test_cta_with_url_has_link():
    html = render_cta("운세한잔", "https://example.com/app")
    assert "https://example.com/app" in html
    assert "바로가기" in html
    assert "운세한잔" in html


def test_cta_without_url_is_hidden():
    html = render_cta("운세 인사이트", "")
    assert html == ""
    assert "준비 중" not in html


def test_cta_escapes_html():
    html = render_cta("<script>x</script>", "https://x.test")
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
