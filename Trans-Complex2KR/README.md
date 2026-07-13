# Trans-Complex2KR — 복합 원어 기반 한국어 번역

원작 **중국어 번체(CHT)를 문체·register·고유명 한자음의 기준**으로, **영어(EN)를 의미·인물 공식명 기준**으로, **일본어(JP)를 뉘앙스 교차 참조**로 삼아 복합 판단한 한국어 번역.

## 파일 맵

### decisions/
- `localization_decisions.md` — **모든 번역 결정과 근거**(§0 대원칙 ~ §11 음차 판정). 재검토·수정 시 여기부터.

### glossary/
- `master_glossary.json` / `.md` — **단일 권위 용어집**: 세계관 용어·신화명·인물·장비·지명(114)·세력(27)·명명 규칙(9). 번역 에이전트/작업의 참조 기준.
- `proper_noun_crosslang.json` / `.md` — 고유명 **교차언어 비교표**(CHT/병음/EN/KR/유형). 영문 기준 비교버전 제작·음차 재검토용. (구 `crosslang_names.json` 53지명 원자료 통합)
- ※ 구 분류별 원자료(`terms`/`places`/`characters`/`characters_kr`/`crosslang_names`.json)는 위 두 마스터로 통합·삭제됨. 단일 권위 = master_glossary + proper_noun_crosslang.

### characters/
- `character_profiles.md` — **대사 번역 기준서**: 화자별 한국어 말투(반말/존댓말/문어체)·1인칭·**존댓말/호칭 매트릭스**(레미→에다=언니, 케이→준=도련님 등)·성격. 대사·메일 수정 시 필수.
- `character_personas.md` — 인물 성별·성격 영어 태그·역할(외부 페르소나 조회/재분석용).
- 화자 매핑 자료(`uid2speaker.json` 4515 매핑, `actor_defs.json` 54 액터 정의)는 세 변형 공통이라 **`Common/Characters/`** 로 이동됨(GUID→locKey→CHT명). 화자별 재번역 시 사용.

### translations/
최종 KR 번역 전량. 주입 시 sharedassets2 각 TextAsset의 `_KR` 필드로 들어감(Common/injection-guide 참조).

| 파일 | 대상 TextAsset | 키 형식 |
|---|---|---|
| `ui_kr.json` (485) | StringDataLocalization | locKey → KR (UI·메뉴·화자이름표 Actor_*) |
| `story_kr.json` (4728) | StoryLocalization | uid → KR (Text_KR) |
| `mail_kr.json` (51) | SheetMailLocalization | id → {title,sender,receiver,job,content} |
| `items_kr.json` | SheetItemsLocalization | "id:Prefix" → KR |
| `loc_kr.json` | SheetLocLocalization | "id:Prefix" → KR |
| `subloc_kr.json` | SheetSubLocLocalization | "id:Prefix" → KR |
| `incident_kr.json` | SheetIncidentLocalization | "id:Prefix" → KR |
| `recipe_kr.json` | SheetRecipeLocalization | "id:Prefix" → KR |
| `store_kr.json` | SheetStoreLocalization | "id:Prefix" → KR |
| `secret_kr.json` | SheetSecretLocLocalization | "id:Prefix" → KR |

## 핵심 결정 (빠른 참조)
- 龍脈=용맥, 龍鳴=별노래, 殘響=메아리, 게임 타이틀=**별노래의 메아리**.
- 汜=**영(靈)** / 汜氣=영기 / 汜水=영수 / 汜晶=영정 (혼이 녹아드는 매질).
- 萬道=만도, 黑龍=흑룡, 燭龍=촉룡, 后土=후토, 乙皇=을황, 太乙=태을, 女巫=무녀 (신화·세계관명 한자음).
- 인물: 에다/레미/케이/본즈/레드/러셀 박사/라마/벤젤. **이씨 가문=이준(李莫)·이현(李玄)**.
- 음차(EN 따름): 메이페어·에펠·마르세유·샘·노미·로댕…  / 신라(Shinra)·백제(Paikje).
- 비공식 번역자 크레딧: **푸른샛별**(Credits_2 최하단, 공식과 분리 표기).

## 재작업 순서 권장
1. (게임 업데이트 시) sharedassets2 새 원본에서 폰트/언어 재설정 → `.fontready` 재생성.
2. TextAsset 항목 id/uid/locKey가 바뀌었는지 확인(대체로 안정적).
3. translations/*_kr.json 주입(injection-guide, ONE PASS).
4. 용어 수정 시 decisions + master_glossary 갱신 후 소급 교체(CHT 대조).
