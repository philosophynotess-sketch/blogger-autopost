from content.coupang_rotation import COUPANG_DISCLOSURE
from render.affiliate import render_affiliate_block


def test_empty_url_still_shows_disclosure():
    html = render_affiliate_block(url="")
    assert COUPANG_DISCLOSURE in html
    assert "href=" not in html


def test_url_renders_legal_and_link():
    html = render_affiliate_block(
        url="https://link.coupang.com/a/example",
        title="타로 카드 모음",
        description="입문용 타로",
    )
    assert "https://link.coupang.com/a/example" in html
    assert "타로 카드 모음" in html
    assert COUPANG_DISCLOSURE in html
    assert 'rel="sponsored noopener noreferrer"' in html


def test_banner_optional():
    html = render_affiliate_block(
        url="https://link.coupang.com/a/example",
        banner_image_url="https://img.example/banner.jpg",
    )
    assert "https://img.example/banner.jpg" in html
    assert "<img" in html
