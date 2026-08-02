# 운세 인사이트 SNS 유입 · Meta 자동화 전략

**날짜:** 2026-08-02  
**목표:** SNS 팔로워 성장 → 블로그 클릭 → 체류·쿠팡 파트너스 수익  
**블로그:** https://unseinsight.blogspot.com/

## 1. 비즈니스 퍼널 (한 줄)

```
카드뉴스/릴스/스레드 (훅·요약)
    → 프로필·캡션 링크 / 스토리 링크 스티커
    → 블로그 본문 (상세 운세 + 애드센스 + 쿠팡 2곳)
    → 쿠팡 클릭·구매 수수료
```

SNS에 **전문을 다 주지 않는다.**  
SNS = “내 띠/별자리 한 줄 + 궁금하면 블로그”.

## 2. 벤치마크 분석 (`docs/benchmark/`)

참고 스타일: ForceTeller류 **정보 밀도 높은 1장 요약 카드**

| 유형 | 패턴 | 우리 적용 |
|------|------|-----------|
| 일별 별자리 | 제목(날짜) + 12궁 캐릭터 + 한 줄 조언 + 행운 아이템 | 같은 밀도, **우리 로고·보라 톤**, 캐릭터는 직접 제작/이모지/심플 아이콘 (저작권 복제 금지) |
| 일별 띠별 | 제목 + 12띠 + 연도별 한 줄 | 동일. 카드에는 연도 2~3개만 or 띠당 1줄, **상세 연도는 블로그** |
| 테마(태어난 달) | 표지 1장 + 본문 카드(살 유형별 설명) | 주 1회 SEO/테마용 카드뉴스 3~5장 |

**벤치에서 배울 점**
- 흰/파스텔 배경, 큰 제목, 한 줄 카피 (스크롤 스톱)
- 저장·공유 유도되는 “전체표” 포맷
- 하단에 브랜드 마크

**우리가 다르게 할 점 (수익·브랜드)**
- 하단에 **운세 인사이트 로고** + `unseinsight.blogspot.com`
- 캡션 마지막: “전체·시간대·영역별 운세 → 블로그 링크”
- 카드 본문은 **요약만**, 블로그에만 쿠팡·장문

## 3. 콘텐츠 매트릭스 (블로그 요일 ↔ SNS)

| 블로그 슬롯 | SNS 포맷 | 채널 |
|-------------|----------|------|
| 월·목 오늘의 운세 | 1~3장 카드 (키워드·시간대·팁) + 스레드 글 | IG 피드, FB, Threads |
| 화·금 띠별 | **1장 전체표** (벤치 스타일) | IG/FB 메인 성장 엔진 |
| 수·토 별자리 | **1장 전체표** | IG/FB |
| 일 SEO 가이드 | 표지+핵심3 + CTA 카드뉴스 | IG 캐러셀, FB, 릴스 훅 |

**하루 SNS 권장량 (초기)**
- 피드 이미지 1 (또는 캐러셀 3)
- 스레드 1 (텍스트 위주 + 이미지 1)
- 릴스: 주 3~4회만 (품질 우선)
- 페북 페이지: IG와 동일 에셋 크로스포스팅

## 4. Meta 자동화 현실 (개발자 앱 기준)

이미: 메타 페이지 + 개발자 앱 생성.

### 4.1 연결 구조

```
Meta App
  ├─ Facebook Page (운세 인사이트)
  ├─ Instagram Business/Creator (페이지에 연결)
  └─ Threads 프로필 (인스타와 연동된 경우)
```

### 4.2 API 권한 (App Review 필요할 수 있음)

| 채널 | 주요 권한/방식 | 난이도 |
|------|----------------|--------|
| **Facebook Page** | `pages_manage_posts`, `pages_read_engagement`, Page Access Token | 쉬움 |
| **Instagram 피드** | Instagram Graph API `instagram_content_publish`, `instagram_basic` | 중 |
| **Instagram 릴스** | Reels 컨테이너 업로드 (Graph API) | 중~상 |
| **Threads** | Threads API (`threads_content_publish` 등) | 중 (별도 제품) |

### 4.3 단계적 도입 (추천)

| Phase | 기간 | 내용 |
|-------|------|------|
| **0 반자동** | 1주 | 카드 이미지 자동 생성 → 사람이 Meta 앱에서 업로드. 카피·해시태그 템플릿 |
| **1 페북+IG 피드** | 2~3주 | Graph API로 Page + IG 이미지 게시 자동화 |
| **2 스레드** | 이어서 | Threads API 텍스트+이미지 |
| **3 릴스** | 안정 후 | 세로 템플릿 + 자막 영상 or 이미지 줌 영상 |

처음부터 4채널 완전 자동은 권한 심사·정책 리스크가 큼.  
**페북 페이지 + IG 피드**를 먼저 고정하는 것이 안전.

### 4.4 Secrets (나중에 GitHub Actions)

```
META_APP_ID
META_APP_SECRET
META_PAGE_ID
META_PAGE_ACCESS_TOKEN   # long-lived
IG_USER_ID               # Instagram Business account id
THREADS_USER_ID          # optional
BLOG_BASE_URL=https://unseinsight.blogspot.com
```

## 5. 카드 생성 파이프라인 (구현 단위)

```
기존: Gemini → 블로그 HTML → Blogger
추가:
  → social_summary JSON 추출
       { title, date, category, lines[12], hook, cta, blog_url }
  → card renderer (HTML→PNG 또는 Pillow)
       templates: zodiac_grid, animal_grid, daily_3slide, theme_cover
  → assets/social/YYYY-MM-DD/
       feed.png | carousel-01..n.png | story.png | caption.txt | reel-script.txt
  → (Phase1+) publish_meta.py
```

### 5.1 템플릿 스펙 (벤치 반영 · 우리 브랜드)

**A. 띠별/별자리 1장 그리드 (1080×1350 또는 1080×1080)**
- 상단: `MM월 DD일 띠별 운세`
- 본문: 12칸, **한 줄 카피** (15~22자 권장)
- 하단: 로고 마크 + `자세한 내용 unseinsight.blogspot.com`
- 배경: 화이트/크림 (벤치와 유사) 또는 연보라

**B. 오늘의 운세 3장 캐러셀**
1. 훅 + 날짜 + 키워드  
2. 시간대 or 영역 3줄  
3. “전체·영역별·쿠폰 아닌 상세 → 블로그” CTA

**C. 테마/SEO 표지+본문**
- 벤치의 “태어난 달로 보는 N월 운세”형  
- 저장 유도, 2~4장

**저작권:** 벤치 캐릭터·ForceTeller 마크 **복제 금지**.  
우리 마크(달+책) + 심플 아이콘/이모지/추후 자체 캐릭터.

## 6. 캡션·링크 템플릿 (유입용)

```
{날짜} {카테고리} 요약 🃏

{한 줄 훅}

내 띠/별자리만 보고 넘기지 말고
시간대·영역별 상세는 블로그에 적어 두었어요.

🔗 {blog_post_url}

#오늘의운세 #띠별운세 #별자리운세 #운세인사이트
```

- 가능하면 **게시물마다 그날 글 URL** (홈이 아니라 포스트)
- IG는 바이오 링크 or 스토리 스티커 / 나중에 Link in bio 툴
- FB/Threads는 본문에 URL 직접

## 7. KPI (한 달)

| 지표 | 초기 목표 (느슨) |
|------|------------------|
| 주간 SNS 게시 성공률 | 90%+ |
| 게시→블로그 세션 | 추세 상승 |
| 블로그 체류 30초+ | 비율 관찰 |
| 쿠팡 클릭 | 주간 카운트 |
| 팔로워 | 절대수보다 주간 순증 |

## 8. 리스크

- Meta 앱 **미검수** 시 게시 제한 → 개발 모드/테스터만
- 과도한 동일 포맷 스팸 → 도달 감소 (주 1~2회 테마 변형)
- 운세+광고 과다 시 신뢰↓ → SNS에는 쿠팡 넣지 말고 **블로그만**
- 벤치 캐릭터 무단 사용 시 법적 이슈

## 9. 바로 다음 실행 순서 (추천)

1. **Meta 준비 체크리스트**
   - IG를 Business로 전환 + 페이지 연결
   - 앱에 제품: Facebook Login, Instagram Graph API, (Threads)
   - long-lived Page token 발급
2. **카드 렌더러 1종** (띠별 or 별자리 그리드) 먼저 구현
3. **DRY_RUN:** 이미지만 `docs/` 또는 `assets/social/` 저장, 수동 업로드 1주
4. **FB Page API 자동 게시** 연결
5. **IG 피드** 연결
6. Threads → Reels 순

## 10. 성공 정의

- 매일(또는 주 5회) 벤치급 **한 장 요약 카드**가 브랜드 톤으로 나감
- 캡션/바이오로 블로그 포스트 유입
- 블로그에서 쿠팡 블록 클릭이 측정됨
- 팔로워는 천천히, **유입·수수료**가 메인 KPI
