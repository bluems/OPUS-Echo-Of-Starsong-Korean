# Trans-EN2KR — 영문 원문 우선 한국어 번역

원작 **영어(EN, 공식 영어판)를 의미 전반과 고유명(세계관·신화·지명·인물) 기준**으로 삼고, **중국어 번체(CHT)는 문체·register 보정**에, **일본어(JP)는 뉘앙스 교차 참조**에만 쓰는 한국어 번역. 자매 프로젝트 Trans-Complex2KR은 반대로 고유명 한자음을 우선한다.

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
- `uid2speaker.json` — 대사 uid → 화자(4515 매핑). 화자별 재번역 시 사용.
- `actor_defs.json` — 액터 54종 정의(GUID→locKey→CHT명).

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
- 龍脈=루멘, 龍鳴=별노래, 殘響=메아리, 게임 타이틀=**별노래의 메아리**.
- 汜=**루멘**(龍脈과 통합, EN "Lumen" 표기 수용) / 汜氣=루미움 / 汜水=루메나이드 / 汜晶=루메나이트.
- 萬道=미리안, 黑龍=밴시, 燭龍=이그니스, 后土=테라, 乙皇=헬리우스, 太乙=타이양, 女巫=무녀 (영문판 신명/용어 수용).
- 인물: 에다/레미/케이/본즈/레드/러셀 박사/라마/벤젤. **로댕 가문=준(李莫)·셴 리(李玄)**.
- 음차(EN 따름): 메이페어·에펠·마르세유·샘·노미·로댕…  / 신라(Shinra)·백제(Paikje).
- 비공식 번역자 크레딧: **푸른샛별**(Credits_2 최하단, 공식과 분리 표기).

## 재작업 순서 권장
1. (게임 업데이트 시) sharedassets2 새 원본에서 폰트/언어 재설정 → `.fontready` 재생성.
2. TextAsset 항목 id/uid/locKey가 바뀌었는지 확인(대체로 안정적).
3. translations/*_kr.json 주입(injection-guide, ONE PASS).
4. 용어 수정 시 decisions + master_glossary 갱신 후 소급 교체(CHT 대조).
