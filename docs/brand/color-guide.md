# 운세 인사이트 브랜드 가이드

**블로그:** https://unseinsight.blogspot.com/  
**영문:** UNSE INSIGHT

## 공식 마크

**메인 심볼:** `logo-mark-ai-concept.jpg` (원본 컨셉)  
→ 실제 배포용 복사본: `logo-mark.png` 및 리사이즈 세트

컨셉: **초승달 + 펼친 책(인사이트) + 스파클**  
정보형 운세 미디어 / “읽다”는 인사이트 브랜드에 맞춤.

## 컬러

| 이름 | HEX | 용도 |
|------|-----|------|
| Violet | `#7C3AED` | 액센트, 영문 워드 |
| Deep Purple | `#4C1D95` | 워드마크, 다크 배경 |
| Pink | `#DB2777` | 포인트 라인 |
| Soft Lilac | 마크 내부 라벤더 | 아이콘 본문 |
| Cream/Soft | `#FAF5FF` | 마크 배경 패널 |
| Ink | `#1F2937` | 보조 텍스트 |

## 파일 맵

| 파일 | 용도 |
|------|------|
| `logo-mark-ai-concept.jpg` | **공식 마크 원본 (최애)** |
| `logo-mark.png` | 공식 마크 PNG |
| `logo-mark-512.png` / `192` | 앱·SNS 아이콘 |
| `favicon-64.png` | 파비콘 |
| `logo-primary.png` | 가로 워드마크 (마크+한글) |
| `logo-primary-dark.png` | 다크 배경용 가로형 |
| `logo-stacked.png` | 세로 스택 |
| `logo-avatar-instagram.png` | 프로필(이름+URL) |
| `logo-avatar-mark.png` | 프로필(마크만, 추천) |

## 채널별 폴더 (프로필·커버)

상세: `README-channels.md`

| 폴더 | 주요 파일 |
|------|-----------|
| `facebook/` | `profile-960.png`, **`cover-1640x624.png`** |
| `instagram/` | `profile-1080.png` |
| `blogger/` | `profile-512.png` |
| `reels/` | `profile-1080.png` (인스타 계정과 동일) |

## 사용 추천

| 채널 | 추천 파일 |
|------|-----------|
| 인스타/스레드 프로필 | `instagram/profile-1080.png` |
| 페북 프로필 | `facebook/profile-960.png` |
| 페북 커버 | `facebook/cover-1640x624.png` |
| 블로거 | `blogger/profile-512.png` |
| 카드뉴스 코너 | `logo-mark.png` 작게 |
| 블로그 헤더 | `logo-primary.png` |

## 재생성

마크 원본을 유지한 채 워드마크만 다시 뽑을 때:

```bash
python docs/brand/generate_logos.py
```

`logo-mark-ai-concept.jpg` 를 바꾸면 전체가 그 심볼 기준으로 다시 합성됩니다.
