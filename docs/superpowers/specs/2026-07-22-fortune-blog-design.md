# 운세 블로그 일일 자동 포스팅 설계

**날짜:** 2026-07-22  
**상태:** Approved (사용자: 모듈형 재작성 + 설계·구현 일괄 진행)

## 1. 목표

| 우선순위 | 목표 | 구현 반영 |
|----------|------|-----------|
| 1 | 애드센스 수익 (검색 유입) | 심화 SEO 글 주 1회+, 정보형 톤, 충분한 본문 길이 |
| 2 | 운세 앱/웹 홍보·전환 | CTA 블록 + `APP_URL`/`APP_NAME` 환경변수 (미배포 시 출시 예정) |
| 3 | 구독·재방문 습관 | 매일 KST 07:00 발행, 카테고리 로테이션 |

## 2. 범위

**포함**
- Blogger 유지, GitHub Actions 하루 1회 (KST 07:00)
- 카테고리 메뉴: 오늘의 종합 운세, 띠별, 별자리, 테마 심화 SEO
- Gemini 기반 본문 생성
- 일일 글: CSS 카드 UI / 심화 글: AI 썸네일(실패 시 폴백·스킵)
- 오락 목적 면책 문구
- 모듈형 Python 패키지 구조

**제외 (YAGNI)**
- 앱 본체 개발
- CMS/DB/승인 UI
- 티스토리·자체 블로그 이전
- 하루 2회 이상 발행

## 3. 아키텍처

```
GitHub Actions (cron 0 22 * * * UTC ≈ KST 07:00)
    → main.py
        → schedule: 날짜 → PostSlot(category, mode)
        → generator: Gemini → title, html_body, meta, image_prompt?
        → template: CSS wrap + CTA + disclaimer
        → images: SEO 글만 썸네일 시도
        → blogger: posts.insert + labels
```

### 모듈 책임

| 모듈 | 책임 |
|------|------|
| `config/settings.py` | 환경변수, 카테고리 상수, 로테이션 테이블 |
| `content/schedule.py` | 오늘(Asia/Seoul) → 카테고리 슬롯 |
| `content/generators.py` | 카테고리별 프롬프트·파싱 |
| `content/topics_seo.json` | 심화 SEO 주제 풀 |
| `render/templates.py` | HTML/CSS 레이아웃 |
| `render/cta.py` | 앱 CTA (URL 유무 분기) |
| `publish/blogger.py` | Blogger OAuth·발행 |
| `publish/images.py` | 심화 글 이미지 생성·업로드 |
| `main.py` | 오케스트레이션만 |

## 4. 카테고리 로테이션

요일 기준 (월=0 … 일=6, Asia/Seoul):

| 요일 | 카테고리 ID | 라벨(한글) | 이미지 |
|------|-------------|------------|--------|
| 월 | `daily_overview` | 오늘의 운세 | CSS only |
| 화 | `zodiac_animals` | 띠별 운세 | CSS only |
| 수 | `star_signs` | 별자리 운세 | CSS only |
| 목 | `daily_overview` | 오늘의 운세 | CSS only |
| 금 | `zodiac_animals` | 띠별 운세 | CSS only |
| 토 | `star_signs` | 별자리 운세 | CSS only |
| 일 | `seo_deep` | 운세 가이드 | AI 썸네일 시도 |

심화 주제는 `topics_seo.json`에서 미사용 주제를 고르고, 사용 이력은 `published_seo.json`에 기록(로컬/워크플로 아티팩트 없이 동작 가능하도록 파일 기반; Actions에서는 checkout 후 커밋하지 않아도 중복은 제목 기반 Blogger 조회로 완화 가능). 1차 구현: SEO 주제는 날짜 해시로 안정 선택 + 선택적으로 published 파일.

## 5. 콘텐츠 포맷

**공통**
- 톤: 깔끔한 정보 미디어 (과장·신비 드립 최소화)
- 출력: HTML only (Markdown 금지)
- 면책: 하단에 오락/참고용 고지
- CTA: 앱 URL 있으면 링크, 없으면 “앱 출시 예정”

**daily_overview**  
날짜 종합 운세, 애정/금전/건강/직장, 행운의 색·숫자, 오늘의 한 줄 조언. CSS 섹션 카드.

**zodiac_animals**  
쥐~돼지 12띠 각각 2~4문장 + 한 줄 키워드. 카드 그리드.

**star_signs**  
양~물고기 12별자리 동일 구조.

**seo_deep**  
1500자 이상 상당의 정보형 가이드(H2/H3, 리스트, FAQ 느낌 섹션). 검색 키워드 자연 삽입. 썸네일 프롬프트 포함.

## 6. 데이터 흐름

1. `load_settings()` — 필수 env 검증 (`GEMINI_API_KEY`, Blogger OAuth, `BLOGGER_BLOG_ID`)
2. `resolve_slot(today)` — 카테고리·라벨·needs_image
3. `generate_post(slot)` — Gemini 호출, title/body/tags/image_prompt 파싱
4. `render_html(...)` — 템플릿 + CTA + disclaimer
5. `maybe_image(slot, prompt)` — SEO만
6. `publish_post(title, html, labels)` — Blogger insert `isDraft=False`
7. 실패 시 non-zero exit (Actions 실패로 표시)

## 7. 에러 처리

| 상황 | 동작 |
|------|------|
| 필수 env 누락 | 시작 시 즉시 실패, 메시지 명확히 |
| Gemini 5xx/타임아웃 | 최대 3회 지수 백오프 후 실패 |
| Gemini 응답 파싱 실패 | 실패 (빈 글 발행 금지) |
| 이미지 실패 | 로그 후 기본 Unsplash/그라데이션 없이 텍스트만 발행 가능 (hero 생략 또는 정적 폴백 URL) |
| Blogger API 실패 | 예외 전파, exit 1 |
| DRY_RUN=1 | 발행 생략, 제목/라벨/본문 일부 로그 |

## 8. 설정 (환경변수)

| 변수 | 필수 | 설명 |
|------|------|------|
| `GEMINI_API_KEY` | Y | 본문 생성 |
| `G_CLIENT_ID` | Y | OAuth |
| `G_CLIENT_SECRET` | Y | OAuth |
| `G_REFRESH_TOKEN` | Y | OAuth |
| `BLOGGER_BLOG_ID` | Y | 대상 블로그 |
| `APP_NAME` | N | 기본 "운세 앱" |
| `APP_URL` | N | 비어 있으면 출시 예정 CTA |
| `HF_TOKEN` | N | 심화 썸네일 |
| `IMGBB_API_KEY` | N | 이미지 호스팅 |
| `DRY_RUN` | N | `1`이면 미발행 |
| `FORCE_CATEGORY` | N | 테스트용 카테고리 ID 강제 |

## 9. 테스트

- `schedule` 요일→카테고리 단위 테스트
- `cta` URL 유무 분기 테스트
- `generators` 파싱 헬퍼 테스트 (샘플 LLM 문자열)
- 로컬 `DRY_RUN=1 python main.py` 스모크 (키 있을 때)

## 10. 마이그레이션

- 기존 Vibe Coding `topics.json` / 기술 블로그 프롬프트 폐기(아카이브 가능)
- `main.py` 단일 파일 로직 → 모듈로 이전
- workflow: 하루 1회, 새 의존성 설치, 동일 secrets + optional APP_*
- OAuth 헬퍼 (`get_token.py`) 유지

## 11. 성공 기준

- Actions가 매일 KST 07:00 성공 시 Blogger에 운세 글 1건
- 라벨이 카테고리 메뉴와 일치
- 앱 URL 없이도 CTA 깨지지 않음
- 이미지 실패해도 SEO 글 본문은 발행됨
- 로컬 DRY_RUN으로 파이프라인 검증 가능
