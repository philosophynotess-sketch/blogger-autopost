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


@dataclass
class GeneratedPost:
    title: str
    body_html: str
    tags: list[str] = field(default_factory=list)
    image_prompt: str = ""
    seo_topic: str = ""


def _load_seo_topics() -> list[str]:
    with open(SEO_TOPICS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list) or not data:
        raise RuntimeError("topics_seo.json 이 비어 있거나 형식이 잘못되었습니다.")
    return [str(x) for x in data]


def pick_seo_topic(post_date_iso: str, topics: list[str] | None = None) -> str:
    """Stable topic pick from date so the same day is reproducible."""
    topics = topics or _load_seo_topics()
    # simple stable hash
    h = sum(ord(c) for c in post_date_iso)
    return topics[h % len(topics)]


def _common_rules(slot: PostSlot) -> str:
    return f"""
당신은 한국어 운세·라이프 정보 미디어 에디터입니다.
톤: 담백하고 신뢰감 있는 정보형. 신비주의 과한 문장, 공포 마케팅, AI 티 나는 서론 금지.
날짜 기준: {slot.date_ko} ({slot.date_iso})
절대 규칙:
- 출력은 HTML 조각만. Markdown(##, **, ``` 등) 금지.
- 점술 결과를 절대적 사실처럼 단정하지 말 것. "~할 수 있어요", "참고해보세요" 수준.
- 의료·법률·투자 조언 금지.
- "안녕하세요", "오늘은 뭘 알려드릴까요" 같은 군더더기 서론 금지. 첫 문장부터 본론.
- 제목과 본문에 날짜 또는 핵심 키워드를 자연스럽게 넣을 것.
"""


def build_prompt(slot: PostSlot) -> tuple[str, str]:
    """Return (prompt, seo_topic_or_empty)."""
    base = _common_rules(slot)
    seo_topic = ""

    if slot.category_id == CAT_DAILY:
        prompt = (
            base
            + f"""
카테고리: 오늘의 종합 운세

아래 구조의 HTML만 출력하세요. 최상단 메타 줄 포함:

[TAGS: 오늘의운세, {slot.post_date.month}월운세, 일일운세]
[FEATURED_IMAGE_PROMPT: ]

<article>
<h1>{slot.date_ko} 오늘의 운세 — 한눈에 보는 하루 흐름</h1>
<section class="f-summary">
  <p>2~3문장 핵심 요약</p>
</section>
<section class="f-grid">
  <div class="f-card"><h3>애정</h3><p>...</p></div>
  <div class="f-card"><h3>금전</h3><p>...</p></div>
  <div class="f-card"><h3>건강</h3><p>...</p></div>
  <div class="f-card"><h3>직장·학업</h3><p>...</p></div>
</section>
<section class="f-lucky">
  <p><strong>행운의 색</strong>: ...</p>
  <p><strong>행운의 숫자</strong>: ...</p>
  <p><strong>오늘의 키워드</strong>: ...</p>
</section>
<section class="f-tip">
  <h2>오늘의 실천 팁</h2>
  <p>구체적 행동 1~2가지</p>
</section>
</article>
"""
        )
    elif slot.category_id == CAT_ANIMALS:
        animals = ", ".join(ZODIAC_ANIMALS)
        prompt = (
            base
            + f"""
카테고리: 띠별 운세 (한국 12띠)

반드시 다음 12띠를 모두 다룰 것: {animals}

[TAGS: 띠별운세, 오늘의띠별운세, 12띠운세]
[FEATURED_IMAGE_PROMPT: ]

<article>
<h1>{slot.date_ko} 띠별 운세 — 쥐부터 돼지까지</h1>
<section class="f-summary"><p>전체 분위기 2문장</p></section>
<section class="f-zodiac-list">
  <!-- 각 띠마다 아래 카드 반복, 12개 -->
  <div class="f-z-card" data-sign="쥐">
    <h3>쥐띠</h3>
    <p class="f-keyword">키워드 한 줄</p>
    <p>2~4문장 운세</p>
  </div>
</section>
</article>
"""
        )
    elif slot.category_id == CAT_STARS:
        signs = ", ".join(STAR_SIGNS)
        prompt = (
            base
            + f"""
카테고리: 별자리 운세 (서양 12궁)

반드시 다음 12별자리를 모두 다룰 것: {signs}

[TAGS: 별자리운세, 오늘의별자리, 12별자리]
[FEATURED_IMAGE_PROMPT: ]

<article>
<h1>{slot.date_ko} 별자리 운세 — 12궁 하루 흐름</h1>
<section class="f-summary"><p>전체 분위기 2문장</p></section>
<section class="f-zodiac-list">
  <div class="f-z-card" data-sign="양자리">
    <h3>양자리</h3>
    <p class="f-keyword">키워드 한 줄</p>
    <p>2~4문장 운세</p>
  </div>
</section>
</article>
"""
        )
    elif slot.category_id == CAT_SEO:
        seo_topic = pick_seo_topic(slot.date_iso)
        prompt = (
            base
            + f"""
카테고리: 테마 심화 SEO 가이드 글
주제: "{seo_topic}"

애드센스·검색 유입을 위한 정보형 장문. 내용이 얇거나 짧으면 안 됨.
분량: 본문 한글 기준 충분히 길게 (대략 1800~2500자 분량 이상 내용 밀도).
구조: H2/H3, 목록, 실전 팁, FAQ 성격 섹션 포함.
키워드를 부자연스럽게 반복하지 말 것.

[TAGS: 운세가이드, 키워드1, 키워드2]
[FEATURED_IMAGE_PROMPT: calm editorial illustration related to the topic, soft light, no text, Korean lifestyle mood]

<article>
<h1>검색에 자연스러운 제목 (주제 반영, 클릭베이트 금지)</h1>
... 본문 ...
<section class="f-faq">
  <h2>자주 묻는 질문</h2>
  <h3>질문1</h3><p>답변</p>
  <h3>질문2</h3><p>답변</p>
  <h3>질문3</h3><p>답변</p>
</section>
</article>
"""
        )
    else:
        raise ValueError(f"알 수 없는 카테고리: {slot.category_id}")

    return prompt, seo_topic


def parse_gemini_text(full_text: str, fallback_title: str) -> GeneratedPost:
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
    # strip accidental markdown fences
    body = re.sub(r"^```(?:html)?\s*", "", body)
    body = re.sub(r"\s*```$", "", body)

    if not body or len(body) < 80:
        raise ValueError("생성된 본문이 너무 짧거나 비어 있습니다.")

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
            "temperature": 0.85,
            "maxOutputTokens": 8192,
        },
    }
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            res = requests.post(
                settings.gemini_url, json=payload, timeout=150
            )
            if res.status_code in (429, 500, 502, 503, 504):
                raise requests.HTTPError(f"retryable {res.status_code}: {res.text[:200]}")
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
    raw = call_gemini(settings, prompt)
    post = parse_gemini_text(raw, fallback_title=fallback_title)
    post.seo_topic = seo_topic
    if slot.label not in post.tags:
        post.tags = [slot.label] + post.tags
    return post
