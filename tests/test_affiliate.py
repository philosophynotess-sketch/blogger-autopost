from datetime import date

from content.coupang_rotation import COUPANG_DISCLOSURE
from render.affiliate import render_affiliate_block, render_affiliate_mid


def test_empty_url_still_shows_disclosure():
    html = render_affiliate_block(url="")
    assert COUPANG_DISCLOSURE in html
    assert "href=" not in html


def test_url_renders_legal_and_link():
    html = render_affiliate_block(
        url="https://link.coupang.com/a/example",
        title="타로 카드 모음",
        description="입문용 타로",
        post_date=date(2026, 7, 24),
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


def test_mid_and_footer_copy_differ():
    d = date(2026, 7, 24)
    mid = render_affiliate_mid("https://link.coupang.com/a/mid", post_date=d)
    foot = render_affiliate_block(
        url="https://link.coupang.com/a/foot",
        post_date=d,
    )
    assert "f-affiliate-mid" in mid
    assert COUPANG_DISCLOSURE not in mid
    assert COUPANG_DISCLOSURE in foot
    # titles/CTAs should not be identical templates
    assert "영역별 운세 보기 전" in mid or "루틴" in mid or "키워드" in mid or "자주 찾는" in mid
    assert "추천 상품 보러가기" not in mid or "추천 상품 보러가기" not in foot
