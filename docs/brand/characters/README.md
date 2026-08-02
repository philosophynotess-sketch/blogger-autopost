# 운세 인사이트 캐릭터 에셋

벤치마크와 **비슷한 귀여운 톤**, 저작권상 **오리지널** 생성.

## 옵션 팩 (6종)

| 폴더 | 스타일 |
|------|--------|
| `options/option-00-classic` | 클래식 |
| `options/option-01-candy` | 캔디 카와이 |
| `options/option-02-clay` | 클레이 토이 |
| `options/option-03-minimal` | 미니멀 이모지 |
| `options/option-04-lavender` | 라벤더 드림 (별자리 소스) |
| `options/option-05-comic` | 코믹 치비 (띠 소스) |
| **`options/option-fixed-hybrid`** | **픽스 기본: 띠=코믹(05) + 별=라벤더(04)** |
```bash
python -m social.activate_pack --list
python -m social.activate_pack option-04-lavender
python -m social.generate_pack_previews   # docs/social/pack-previews/
```

활성 팩은 `animals/` · `stars/` 에 복사되고 `active_pack.json` 에 기록됩니다.

## 구조

```
characters/
  active_pack.json
  animals/  stars/          # 현재 활성
  options/option-0X-*/
    animals/ stars/ sheets/ meta.json
```

## 주의

- 벤치 캐릭터 복제 금지
- 앱 연동은 나중 (에셋만 재사용 가능)
