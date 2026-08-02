# SNS 카드 · 캐릭터 팩 · (반)자동화

앱(saas-template) 연동은 **나중**. 지금은 블로그 + 카드 + 캡션 + Meta 뼈대.

## 캐릭터 옵션 6종 (00~05)

| ID | 이름 | 설명 |
|----|------|------|
| `option-00-classic` | 클래식 | 첫 생성 세트 |
| `option-01-candy` | 캔디 카와이 | **기본 활성** · 반짝 파스텔 |
| `option-02-clay` | 클레이 토이 | 말랑 3D |
| `option-03-minimal` | 미니멀 이모지 | 심플 플랫 |
| `option-04-lavender` | 라벤더 드림 | 보라 브랜드 톤 |
| `option-05-comic` | 코믹 치비 | 액세서리·표정 |

### 팩 목록 / 전환

```bash
python -m social.activate_pack --list
python -m social.activate_pack option-04-lavender
```

### 팩별 미리보기 카드

```bash
python -m social.generate_pack_previews
# → docs/social/pack-previews/option-0X-*.png
```

## 샘플 카드

```bash
python -m social.generate_sample_cards
# → docs/social/samples/
```

## 매일 파이프라인 (main.py)

블로그 생성 후 자동으로:

1. SNS용 12줄 한 줄 카피 (Gemini)
2. `docs/social/out/YYYY-MM-DD/` 에  
   - `feed-animals.png` 또는 `feed-stars.png` 또는 `carousel-0N.png`  
   - `caption.txt` / `threads.txt` / `meta.json`
3. Meta 게시 시도  
   - 기본 **dry-run** (로그만)  
   - `META_PUBLISH=1` + 토큰 있으면 **페북 페이지 사진 게시**  
   - 인스타는 공개 이미지 URL 필요 → 이후 단계

## Meta Secrets

```
META_PUBLISH=1
META_PAGE_ID=
META_PAGE_ACCESS_TOKEN=   # long-lived page token
IG_USER_ID=               # optional, needs hosted image_url
```

## 수동 업로드 (지금 바로)

1. `docs/social/samples/` 또는 `out/` 이미지
2. `caption.txt` 복사
3. IG / FB / Threads 에 붙이기

## 다음 (앱 제외)

- [ ] 인스타: ImgBB 등 호스팅 후 Graph publish
- [ ] 릴스: 세로 줌 영상 템플릿
- [ ] 스레드 API
- [ ] 블로그 포스트 실제 URL 파싱 후 캡션 삽입
