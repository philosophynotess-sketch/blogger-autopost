from content.generators import compose_combo_topic, parse_gemini_text, pick_seo_topic


SAMPLE = """
[TAGS: 오늘의운세, 일일운세, 테스트]
[FEATURED_IMAGE_PROMPT: soft morning light over city]

<article>
<h1>2026년 7월 22일 오늘의 운세 — 한눈에 보는 하루 흐름</h1>
<section class="f-summary">
  <p>오늘은 속도보다 정리가 중요한 하루입니다. 작은 정리가 저녁의 여유를 만듭니다.
  오전에는 할 일 목록을 줄이고, 오후에는 회의 전에 한 번 더 확인하는 편이 좋습니다.
  저녁에는 관계 대화를 서두르지 않는 것이 포인트입니다.</p>
</section>
<section class="f-timeline">
  <div class="f-card"><h3>오전</h3><p>집중 구간. 메일은 묶어서 처리하세요.</p></div>
</section>
<section class="f-grid">
  <div class="f-card"><h3>애정</h3><p>솔직한 대화가 도움이 됩니다. 짧은 안부도 좋습니다.</p></div>
</section>
<section class="f-avoid">
  <h2>오늘 피하면 좋은 한 가지</h2>
  <p>충동적인 소비 결정.</p>
</section>
<section class="f-faq">
  <h2>오늘의 Q&amp;A</h2>
  <h3>Q1. 면접이 있는데?</h3>
  <p>준비가 된 부분부터 말하면 리듬이 잡힙니다.</p>
</section>
</article>
"""


def test_parse_extracts_fields():
    post = parse_gemini_text(SAMPLE, fallback_title="fallback", min_body_len=80)
    assert "2026년 7월 22일" in post.title
    assert "f-summary" in post.body_html
    assert "<h1>" not in post.body_html
    assert "오늘의운세" in post.tags
    assert "soft morning light" in post.image_prompt


def test_parse_rejects_too_short():
    try:
        parse_gemini_text(
            "<article><h1>t</h1>x</article>",
            fallback_title="t",
            min_body_len=80,
        )
        assert False, "should raise"
    except ValueError:
        pass


def test_pick_seo_topic_stable():
    topics = ["A", "B", "C"]
    a1 = pick_seo_topic("2026-07-22", topics)
    a2 = pick_seo_topic("2026-07-22", topics)
    assert a1 == a2
    assert a1 in topics


def test_pick_seo_from_json_pool():
    # even day → fixed pool; odd day → combo
    t_even = pick_seo_topic("2026-07-22")
    t_odd = pick_seo_topic("2026-07-23")
    assert isinstance(t_even, str) and len(t_even) > 5
    assert isinstance(t_odd, str) and len(t_odd) > 5
    assert pick_seo_topic("2026-07-22") == t_even


def test_compose_combo_topic():
    t = compose_combo_topic("2026-07-23")
    assert "—" in t or "-" in t
    assert len(t) > 10
