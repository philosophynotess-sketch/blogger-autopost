from social.lines import _clean_line, extract_lines_from_html


def test_clean_line_truncates():
    s = _clean_line("가" * 50, max_len=10)
    assert len(s) <= 10


def test_extract_from_cards():
    html = "".join(
        f'<div class="f-z-card"><h3>t{i}</h3>'
        f'<p class="f-keyword">키워드{i}</p><p>긴설명{i}</p></div>'
        for i in range(12)
    )
    lines = extract_lines_from_html(html, [])
    assert len(lines) == 12
    assert "키워드" in lines[0]
