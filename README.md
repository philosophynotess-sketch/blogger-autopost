# 운세 블로그 일일 자동 포스팅

Blogger에 **하루 1회(한국시간 오전 7시)** 운세 콘텐츠를 자동 발행합니다.  
Gemini로 본문을 만들고, 카테고리 메뉴 로테이션으로 애드센스·습관 재방문·(향후) 앱 홍보를 함께 노립니다.

## 카테고리 로테이션

| 요일 | 카테고리 | 이미지 |
|------|----------|--------|
| 월·목 | 오늘의 운세 (종합) | CSS 카드 |
| 화·금 | 띠별 운세 | CSS 카드 |
| 수·토 | 별자리 운세 | CSS 카드 |
| 일 | 운세 가이드 (SEO 심화) | AI 썸네일 시도 |

## 구조

```
main.py                 # 오케스트레이터
config/settings.py      # 환경변수·카테고리
content/schedule.py     # 날짜 → 슬롯
content/generators.py   # Gemini 생성·파싱
content/topics_seo.json # 심화 주제 풀
render/templates.py     # HTML/CSS
render/cta.py           # 앱 CTA (URL 없으면 출시 예정)
publish/blogger.py      # Blogger API
publish/images.py       # SEO 썸네일
.github/workflows/      # 매일 UTC 22:00
```

설계 문서: `docs/superpowers/specs/2026-07-22-fortune-blog-design.md`

## 로컬 설정

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# .env 값 채우기
```

OAuth 리프레시 토큰이 없으면 `get_token.py` / `get_refresh_token.py`로 발급합니다.

### 테스트

```bash
# 단위 테스트
pytest -q

# 생성만 (발행 안 함)
# .env 에 GEMINI_API_KEY 필요
set DRY_RUN=1
set FORCE_CATEGORY=daily_overview
python main.py
```

### 실제 발행

```bash
python main.py
```

## GitHub Actions Secrets

필수:

- `GEMINI_API_KEY`
- `G_CLIENT_ID`
- `G_CLIENT_SECRET`
- `G_REFRESH_TOKEN`
- `BLOGGER_BLOG_ID`

선택:

- `APP_NAME`, `APP_URL` — 앱 배포 후 설정
- `HF_TOKEN`, `IMGBB_API_KEY` — 일요일 SEO 썸네일
- `COUPANG_PARTNERS_URL` — 글 하단 쿠팡 파트너스 링크 (없으면 블록 숨김)
- `COUPANG_TITLE`, `COUPANG_DESCRIPTION`, `COUPANG_BANNER_URL` — 파트너스 문구/배너(선택)

수동 실행: Actions → **Daily Fortune Blog Post** → Run workflow  
`force_category`, `dry_run` 입력 가능.

## 앱 연동

앱이 아직 없어도 CTA는 “출시 예정”으로 렌더됩니다.  
배포 후 Secrets에 `APP_URL`(및 필요 시 `APP_NAME`)만 넣으면 링크 CTA로 바뀝니다.

## 라이선스

MIT
