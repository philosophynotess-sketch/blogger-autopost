"""Gemini-powered content generation per fortune category."""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests

from config.settings import (
    CAT_ANIMALS,
    CAT_DAILY,
    CAT_SEO,
    CAT_STARS,
    STAR_SIGNS,
    ZODIAC_ANIMALS,
    Settings,
)
from content.schedule import PostSlot

ROOT = Path(__file__).resolve().parent
SEO_TOPICS_PATH = ROOT / "topics_seo.json"

# SEO body should feel substantial for AdSense
MIN_BODY_DAILY = 400
MIN_BODY_LIST = 900
MIN_BODY_SEO = 1200


@dataclass
class GeneratedPost:
    title: str
    body_html: str
    tags: list[str] = field(default_factory=list)
    image_prompt: str = ""
    seo_topic: str = ""


def _load_seo_data() -> dict[str, Any]:
    with open(SEO_TOPICS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return {"curated": data, "situational": [], "seasonal": [], "educational": []}
    if not isinstance(data, dict):
        raise RuntimeError("topics_seo.json 형식이 올바르지 않습니다.")
    return data


def _all_fixed_topics(data: dict[str, Any]) -> list[str]:
    topics: list[str] = []
    for key in ("curated", "situational", "seasonal", "educational"):
        block = data.get(key) or []
        topics.extend(str(x) for x in block)
    if not topics:
        raise RuntimeError("SEO 주제 풀이 비어 있습니다.")
    return topics


def compose_combo_topic(post_date_iso: str, data: dict[str, Any] | None = None) -> str:
    """Build long-tail topic from situation × angle × format arrays."""
    data = data or _load_seo_data()
    slots = data.get("combo_slots") or {}
    situations = slots.get("situations") or ["고민이 있을 때"]
    angles = slots.get("angles") or ["운세로 보는 체크포인트"]
    formats = slots.get("formats") or ["가이드"]

    h = sum(ord(c) for c in post_date_iso)
    s = situations[h % len(situations)]
    a = angles[(h // 3) % len(angles)]
    f = formats[(h // 7) % len(formats)]
    return f"{s} {a} — {f}"


def pick_seo_topic(post_date_iso: str, topics: list[str] | None = None) -> str:
    """
    Stable topic pick.
    Even dates → fixed pool (situational / seasonal / educational mix).
    Odd dates → combo long-tail title for endless variety.
    """
    if topics is not None:
        h = sum(ord(c) for c in post_date_iso)
        return topics[h % len(topics)]

    data = _load_seo_data()
    day = int(post_date_iso[-2:])
    # Alternate style so Sunday posts cover both evergreen and long-tail
    if day % 2 == 1:
        return compose_combo_topic(post_date_iso, data)

    fixed = _all_fixed_topics(data)
    h = sum(ord(c) for c in post_date_iso)
    # rotate pool emphasis by month-ish hash
    return fixed[h % len(fixed)]


def _common_rules(slot: PostSlot) -> str:
    return f"""
당신은 한국어 운세 정보 미디어 「운세 인사이트」의 에디터입니다.
톤: 담백·신뢰·정보형. 신비주의 과한 문장, 공포 마케팅, AI 티 나는 서론 금지.
날짜 기준: {slot.date_ko} ({slot.date_iso})
절대 규칙:
- 출력은 HTML 조각만. Markdown(##, **, ``` 등) 금지.
- 점술 결과를 절대적 사실처럼 단정하지 말 것. "~할 수 있어요", "참고해보세요" 수준.
- 의료·법률·투자 수익을 보장하는 표현 금지. 금전 언급은 습관·태도 수준만.
- "안녕하세요", "오늘은 뭘 알려드릴까요" 같은 군더더기 서론 금지. 첫 문장부터 본론.
- 제목과 본문에 날짜 또는 핵심 키워드를 자연스럽게 넣을 것.
- 추상어("좋은 기운")만 쓰지 말고, 회의·대화·소비·이동·휴식 등 구체 상황을 섞을 것.
"""


def build_prompt(slot: PostSlot) -> tuple[str, str]:
    """Return (prompt, seo_topic_or_empty)."""
    base = _common_rules(slot)
    seo_topic = ""

    if slot.category_id == CAT_DAILY:
        prompt = (
            base
            + f"""
카테고리: 오늘의 종합 운세 (밀도 높은 일일 칼럼)

분량 목표: 본문 충분히 알차게 (빈약한 한 줄 카드 금지). 각 섹션 문장 밀도 유지.
아래 구조를 빠짐없이 채운 HTML만 출력:

[TAGS: 오늘의운세, {slot.post_date.month}월운세, 일일운세, 운세인사이트]
[FEATURED_IMAGE_PROMPT: ]

<article>
<h1>{slot.date_ko} 오늘의 운세 — 한눈에 보는 하루 흐름</h1>

<section class="f-summary">
  <p>3~4문장. 하루 전체 톤 + 왜 그런지 한 줄 근거(상징/흐름) + 실천 방향.</p>
</section>

<section class="f-timeline">
  <h2>시간대별 흐름</h2>
  <div class="f-grid">
    <div class="f-card"><h3>오전</h3><p>3~4문장. 업무·학습 시작, 커뮤니케이션 팁.</p></div>
    <div class="f-card"><h3>오후</h3><p>3~4문장. 회의·협업·집중 구간.</p></div>
    <div class="f-card"><h3>저녁</h3><p>3~4문장. 관계·휴식·정리.</p></div>
  </div>
</section>

<section class="f-grid">
  <div class="f-card"><h3>애정</h3><p>4문장 이상. 연애/가족/친구 중 구체 상황 포함.</p></div>
  <div class="f-card"><h3>금전</h3><p>4문장 이상. 소비·계약·충동구매 등 태도 중심 (수익 보장 금지).</p></div>
  <div class="f-card"><h3>건강</h3><p>4문장 이상. 수면·스트레칭·페이스 등 생활 습관 수준.</p></div>
  <div class="f-card"><h3>직장·학업</h3><p>4문장 이상. 회의, 마감, 협업, 발표 등 구체 장면.</p></div>
</section>

<section class="f-lucky">
  <p><strong>행운의 색</strong>: ... (왜 어울리는지 한 줄)</p>
  <p><strong>행운의 숫자</strong>: ...</p>
  <p><strong>오늘의 키워드</strong>: ...</p>
  <p><strong>추천 행동</strong>: 구체 행동 1가지</p>
</section>

<section class="f-avoid">
  <h2>오늘 피하면 좋은 한 가지</h2>
  <p>2~3문장. 충동 결정, 말실수, 과로 등 현실적 주의점.</p>
</section>

<section class="f-tip">
  <h2>오늘의 실천 팁</h2>
  <ul>
    <li>실행 가능한 팁 1</li>
    <li>실행 가능한 팁 2</li>
    <li>실행 가능한 팁 3</li>
  </ul>
</section>

<section class="f-faq">
  <h2>오늘의 Q&amp;A</h2>
  <h3>Q1. (독자가 아침에 검색할 법한 질문)</h3>
  <p>답변 3~4문장</p>
  <h3>Q2. (관계 또는 일 관련 질문)</h3>
  <p>답변 3~4문장</p>
</section>
</article>
"""
        )
    elif slot.category_id == CAT_ANIMALS:
        animals = ", ".join(ZODIAC_ANIMALS)
        prompt = (
            base
            + f"""
카테고리: 띠별 운세 (한국 12띠) — 카드마다 깊이 있게

반드시 다음 12띠를 모두 다룰 것: {animals}
각 띠 카드 규칙:
- 키워드 1줄
- 본문 5~7문장 (짧으면 안 됨)
- 반드시 포함: ①일/학업 장면 1개 ②관계·대화 장면 1개 ③소비·선택 또는 페이스 관리 1개
- 띠마다 내용이 복사·붙여넣기처럼 비슷하면 안 됨. 톤·상황을 차별화.

[TAGS: 띠별운세, 오늘의띠별운세, 12띠운세, 운세인사이트]
[FEATURED_IMAGE_PROMPT: ]

<article>
<h1>{slot.date_ko} 띠별 운세 — 쥐부터 돼지까지 상세 해설</h1>
<section class="f-summary">
  <p>전체 분위기 3~4문장 + 오늘 공통으로 조심할 포인트 1가지.</p>
</section>
<section class="f-highlight">
  <h2>오늘 주목할 띠</h2>
  <p>흐름이 비교적 수월한 띠 2개, 페이스 조절이 필요한 띠 2개를 짧게 언급 (절대 우열 단정 금지).</p>
</section>
<section class="f-zodiac-list">
  <div class="f-z-card" data-sign="쥐">
    <h3>쥐띠</h3>
    <p class="f-keyword">키워드</p>
    <p>5~7문장 상세 운세</p>
  </div>
  <!-- 나머지 11띠 동일 구조로 모두 작성 -->
</section>
<section class="f-tip">
  <h2>띠 공통 실천 팁</h2>
  <ul>
    <li>팁 1</li>
    <li>팁 2</li>
    <li>팁 3</li>
  </ul>
</section>
</article>
"""
        )
    elif slot.category_id == CAT_STARS:
        signs = ", ".join(STAR_SIGNS)
        prompt = (
            base
            + f"""
카테고리: 별자리 운세 (서양 12궁) — 카드마다 깊이 있게

반드시 다음 12별자리를 모두 다룰 것: {signs}
각 별자리 카드 규칙:
- 키워드 1줄
- 본문 5~7문장
- 반드시 포함: ①일/학업 ②관계·대화 ③소비·선택 또는 컨디션 중 구체 상황
- 별자리마다 문장 패턴이 반복되지 않게 차별화

[TAGS: 별자리운세, 오늘의별자리, 12별자리, 운세인사이트]
[FEATURED_IMAGE_PROMPT: ]

<article>
<h1>{slot.date_ko} 별자리 운세 — 12궁 상세 흐름</h1>
<section class="f-summary">
  <p>전체 분위기 3~4문장 + 공통 주의 포인트.</p>
</section>
<section class="f-highlight">
  <h2>오늘 흐름이 또렷한 별자리</h2>
  <p>에너지가 잘 쓰이는 별자리 2개, 쉬어가면 좋은 별자리 2개 (우열 단정 금지).</p>
</section>
<section class="f-zodiac-list">
  <div class="f-z-card" data-sign="양자리">
    <h3>양자리</h3>
    <p class="f-keyword">키워드</p>
    <p>5~7문장 상세 운세</p>
  </div>
  <!-- 나머지 11개 동일 구조 -->
</section>
<section class="f-tip">
  <h2>별자리 공통 실천 팁</h2>
  <ul>
    <li>팁 1</li>
    <li>팁 2</li>
    <li>팁 3</li>
  </ul>
</section>
</article>
"""
        )
    elif slot.category_id == CAT_SEO:
        seo_topic = pick_seo_topic(slot.date_iso)
        prompt = (
            base
            + f"""
카테고리: 테마 심화 SEO 가이드 (운세 인사이트 장기 트래픽용)
주제(반드시 이 검색 의도를 제목·본문에 반영): "{seo_topic}"

목표: 애드센스·검색 유입. 얇은 요약 글 금지.
분량: 본문 한글 기준 2200~3500자 분량의 밀도 (섹션마다 실질 설명).
구성 필수:
1) 도입: 독자 상황/고민을 구체적으로 짚기 (2~3문단)
2) 핵심 개념 설명 (오해 vs 사실)
3) 상황별 체크리스트 또는 단계 가이드 (번호/불릿)
4) 띠·별자리·사주·타로 중 주제에 맞는 관점 1가지 이상 연결
5) 실전 적용 팁 5개 이상
6) 피해야 할 해석 습관
7) FAQ 4개 이상
8) 짧은 결론 + 내일/다음 행동 1줄

제목: 클릭베이트 금지. 검색 의도가 드러나는 정보형 제목.
투자·의료·법률 확정 조언 금지. 오락·참고·자기성찰 프레임 유지.

[TAGS: 운세가이드, 운세인사이트, 키워드1, 키워드2]
[FEATURED_IMAGE_PROMPT: calm editorial illustration related to the topic, soft light, no text, Korean lifestyle mood]

<article>
<h1>검색 의도에 맞는 자연스러운 제목</h1>
... 위 구성 순서대로 본문 ...
<section class="f-faq">
  <h2>자주 묻는 질문</h2>
  <h3>질문1</h3><p>답변</p>
  <h3>질문2</h3><p>답변</p>
  <h3>질문3</h3><p>답변</p>
  <h3>질문4</h3><p>답변</p>
</section>
</article>
"""
        )
    else:
        raise ValueError(f"알 수 없는 카테고리: {slot.category_id}")

    return prompt, seo_topic


def _min_body_len(category_id: str) -> int:
    if category_id == CAT_SEO:
        return MIN_BODY_SEO
    if category_id in (CAT_ANIMALS, CAT_STARS):
        return MIN_BODY_LIST
    return MIN_BODY_DAILY


def parse_gemini_text(
    full_text: str,
    fallback_title: str,
    *,
    min_body_len: int = 80,
) -> GeneratedPost:
    """Extract title, body, tags, image prompt from model output."""
    image_prompt = ""
    m_img = re.search(
        r"\[FEATURED_IMAGE_PROMPT:\s*(.*?)\]", full_text, re.IGNORECASE | re.DOTALL
    )
    if m_img:
        image_prompt = m_img.group(1).strip()

    tags: list[str] = []
    m_tags = re.search(r"\[TAGS:\s*(.*?)\]", full_text, re.IGNORECASE)
    if m_tags:
        tags = [t.strip() for t in m_tags.group(1).split(",") if t.strip()]

    article_start = full_text.find("<article>")
    body = full_text[article_start:] if article_start != -1 else full_text

    title_match = re.search(r"<h1>(.*?)</h1>", body, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else fallback_title
    title = re.sub(r"<[^>]+>", "", title).strip()

    body = re.sub(r"<h1>.*?</h1>", "", body, count=1, flags=re.IGNORECASE | re.DOTALL)
    body = re.sub(
        r"\[FEATURED_IMAGE_PROMPT:.*?\]", "", body, flags=re.IGNORECASE | re.DOTALL
    )
    body = re.sub(r"\[TAGS:.*?\]", "", body, flags=re.IGNORECASE | re.DOTALL)
    body = body.replace("<article>", "").replace("</article>", "").strip()
    body = re.sub(r"^```(?:html)?\s*", "", body)
    body = re.sub(r"\s*```$", "", body)

    if not body or len(body) < min_body_len:
        raise ValueError(
            f"생성된 본문이 너무 짧거나 비어 있습니다. "
            f"(len={len(body) if body else 0}, min={min_body_len})"
        )

    return GeneratedPost(
        title=title or fallback_title,
        body_html=body,
        tags=tags[:5],
        image_prompt=image_prompt,
    )


def call_gemini(settings: Settings, prompt: str, retries: int = 3) -> str:
    payload: dict[str, Any] = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 8192,
        },
    }
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            res = requests.post(settings.gemini_url, json=payload, timeout=180)
            if res.status_code in (429, 500, 502, 503, 504):
                raise requests.HTTPError(
                    f"retryable {res.status_code}: {res.text[:200]}"
                )
            res.raise_for_status()
            data = res.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            if not text or not str(text).strip():
                raise ValueError("Gemini 빈 응답")
            return str(text)
        except Exception as e:
            last_err = e
            wait = 2**attempt
            print(f"⚠️ Gemini 재시도 {attempt + 1}/{retries}: {e} (wait {wait}s)")
            time.sleep(wait)
    raise RuntimeError(f"Gemini 호출 실패: {last_err}")


def generate_post(settings: Settings, slot: PostSlot) -> GeneratedPost:
    print(f"✍️ 콘텐츠 생성 | {slot.label} | {slot.date_ko}")
    prompt, seo_topic = build_prompt(slot)
    fallback_title = f"{slot.date_ko} {slot.label}"
    min_len = _min_body_len(slot.category_id)

    # One regenerate if model returns thin body
    last_err: Exception | None = None
    for attempt in range(2):
        try:
            raw = call_gemini(settings, prompt)
            post = parse_gemini_text(
                raw, fallback_title=fallback_title, min_body_len=min_len
            )
            post.seo_topic = seo_topic
            if slot.label not in post.tags:
                post.tags = [slot.label] + post.tags
            # soft brand tag
            if "운세 인사이트" not in post.tags and "운세인사이트" not in post.tags:
                post.tags = (post.tags + ["운세인사이트"])[:5]
            return post
        except ValueError as e:
            last_err = e
            print(f"⚠️ 본문 품질 미달, 재생성 시도 ({attempt + 1}/2): {e}")
            prompt = (
                prompt
                + "\n\n[재생성 지시] 이전 응답이 너무 짧았습니다. 각 섹션 문장 수를 늘리고 "
                "구체 상황을 더 넣어 분량을 충분히 확보하세요."
            )
    raise RuntimeError(f"콘텐츠 생성 실패(분량 미달): {last_err}")
