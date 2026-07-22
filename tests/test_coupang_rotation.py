from datetime import date, timedelta

from content.coupang_rotation import (
    COUPANG_DISCLOSURE,
    load_coupang_links,
    pick_coupang_link,
)
from render.affiliate import render_affiliate_block


def test_disclosure_text():
    assert "쿠팡 파트너스 활동의 일환" in COUPANG_DISCLOSURE
    assert "수수료" in COUPANG_DISCLOSURE


def test_links_unique_loaded():
    links = load_coupang_links()
    assert len(links) == 7
    assert len(set(links)) == 7


def test_one_full_cycle_uses_each_link_once():
    links = load_coupang_links()
    n = len(links)
    start = date(2026, 7, 24)
    picked = [pick_coupang_link(start + timedelta(days=i), links) for i in range(n)]
    assert sorted(picked) == sorted(links)


def test_same_date_stable():
    d = date(2026, 8, 1)
    assert pick_coupang_link(d) == pick_coupang_link(d)


def test_affiliate_html_includes_required_phrase():
    html = render_affiliate_block(url="https://link.coupang.com/a/fA8QcAjdjU")
    assert COUPANG_DISCLOSURE in html
    assert "f-aff-legal" in html
