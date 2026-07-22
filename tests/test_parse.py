from content.generators import parse_gemini_text, pick_seo_topic


SAMPLE = """
[TAGS: 오늘의운세, 일일운세, 테스트]
[FEATURED_IMAGE_PROMPT: soft morning light over city]

<article>
<h1>2026년 7월 22일 오늘의 운세 — 한눈에 보는 하루 흐름</h1>
<section class="f-summary">
  <p>오늘은 속도보다 정리가 중요한 하루입니다. 작은 정리가 저녁의 여유를 만듭니다.</p>
</section>
<section class="f-grid">
  <div class="f-card"><h3>애정</h3><p>솔직한 대화가 도움이 됩니다.</p></div>
</section>
</article>
"""


def test_parse_extracts_fields():
    post = parse_gemini_text(SAMPLE, fallback_title="fallback")
    assert "2026년 7월 22일" in post.title
    assert "f-summary" in post.body_html
    assert "<h1>" not in post.body_html
    assert "오늘의운세" in post.tags
    assert "soft morning light" in post.image_prompt


def test_parse_rejects_too_short():
    try:
        parse_gemini_text("<article><h1>t</h1>x</article>", fallback_title="t")
        assert False, "should raise"
    except ValueError:
        pass


def test_pick_seo_topic_stable():
    topics = ["A", "B", "C"]
    a1 = pick_seo_topic("2026-07-22", topics)
    a2 = pick_seo_topic("2026-07-22", topics)
    assert a1 == a2
    assert a1 in topics
