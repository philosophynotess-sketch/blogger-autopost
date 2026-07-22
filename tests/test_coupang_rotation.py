from datetime import date, timedelta

from content.coupang_rotation import (
    COUPANG_DISCLOSURE,
    load_coupang_links,
    pick_coupang_link,
    pick_coupang_pair,
)
from render.affiliate import inject_mid_affiliate, render_affiliate_block, render_affiliate_mid


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
    # Align to the start of a rotation round (ordinal % n == 0)
    base = date(2026, 7, 24).toordinal()
    start = date.fromordinal(base - (base % n))
    picked = [pick_coupang_link(start + timedelta(days=i), links) for i in range(n)]
    assert sorted(picked) == sorted(links)
    assert len(set(picked)) == n


def test_same_date_stable():
    d = date(2026, 8, 1)
    assert pick_coupang_link(d) == pick_coupang_link(d)


def test_affiliate_html_includes_required_phrase():
    html = render_affiliate_block(url="https://link.coupang.com/a/fA8QcAjdjU")
    assert COUPANG_DISCLOSURE in html
    assert "f-aff-legal" in html


def test_pair_links_differ():
    mid, footer = pick_coupang_pair(date(2026, 7, 24))
    assert mid.startswith("https://")
    assert footer.startswith("https://")
    assert mid != footer


def test_inject_before_areas():
    body = '<section class="f-timeline">x</section>\n<section class="f-areas"><h2>영역별 운세</h2></section>'
    mid = render_affiliate_mid("https://link.coupang.com/a/fA8QcAjdjU")
    out = inject_mid_affiliate(body, mid)
    assert out.index("f-affiliate-mid") < out.index("f-areas")
    assert "https://link.coupang.com/a/fA8QcAjdjU" in out
