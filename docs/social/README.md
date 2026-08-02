# SNS 카드 생성 (Phase 0)

## 샘플 생성

```bash
# repo root
python -m social.generate_sample_cards
```

출력: `docs/social/samples/YYYY-MM-DD-animals.png`  
출력: `docs/social/samples/YYYY-MM-DD-stars.png`

## 코드

| 모듈 | 역할 |
|------|------|
| `social/card_renderer.py` | 벤치형 2열×6행 그리드 카드 |
| `social/characters.py` | 캐릭터 경로·라벨 |
| `social/generate_sample_cards.py` | 샘플 실행 |

## 캡션 예시

```
{날짜} 띠별 운세 한 줄 요약 🃏

내 띠만 보고 저장해 두세요.
시간대·영역별 상세는 블로그에 있어요.

🔗 https://unseinsight.blogspot.com/

#오늘의운세 #띠별운세 #운세인사이트
```

## 다음 단계

1. 블로그 Gemini 본문 → 12줄 자동 추출 연결
2. Meta Graph API (페북/IG) 게시
3. 앱(saas-template) 딥링크: `/today`, `/topics/...`

## 앱 연동 (목표)

`C:\Users\user\00.ProjectsSRC\saas-template` (FortuneOne)
- 동일 캐릭터 에셋을 `frontend/public/characters` 로 복사 가능
- SNS CTA: 블로그 대신/추가로 앱 URL
