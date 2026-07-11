# OPUS: Echo of Starsong — 게임 파일 구조 (한국어 번역 관점)

> 언어 무관, 모든 KR 번역 작업에 공통. Steam appid **1504500** (Full Bloom Edition). Unity **2020.3.35f1** Mono 빌드, Addressables, TextMeshPro(Dynamic SDF), NodeCanvas DialogueTrees.
> 게임 루트: `…/steamapps/common/OPUS Echo of Starsong/`, 데이터: `OPUS Echo of Starsong_Data/`

## 1. 로컬라이제이션 텍스트 = sharedassets2.assets 의 TextAsset

번역 대상 텍스트는 **전부 `sharedassets2.assets` 안의 TextAsset 11개**에 들어 있다. 내용은 **JSON 배열**.

| pid | 이름 | 항목수 | 구조(키) | 용도 |
|---|---|---|---|---|
| 916 | SheetMailLocalization | 51 | id, fields | 인게임 메일(편지) |
| 917 | StoryLocalization | 4728 | uid, fields | **본편 대사 전체** (Text_/Speech_) |
| 918 | SheetIncidentLocalization | 615 | id, fields | 사건/이벤트 (NonDT, AsOptionTitle 등) |
| 919 | SheetLocLocalization | 118 | id, fields | 지명·용맥 정보 (Name, InfoDesc, ViewDesc, Mass) |
| 920 | SheetStoreLocalization | 12 | id, fields | 상점 대사 (EnterMsg, SelectMsg…) |
| 921 | StringDataLocalization | 492 | **locKey**, fields | **UI·메뉴·화자이름표**(Actor_*) |
| 922 | SheetItemsLocalization | 283 | id, fields | 아이템 (Name, Description, ShopDesc, MaterialHint) |
| 923 | SheetRecipeLocalization | 17 | id, fields | 제작법 (Name, BuildDescription) |
| 924 | SheetSubLocLocalization | 75 | id, fields | 부지명 (Name, SubLocContent) |
| 925 | StringDataNative | 492 | locKey, fields | OS-native 문자열(번역 불필요) |
| 926 | SheetSecretLocLocalization | 8 | id, fields | 비밀 지점 (SecretName, SecretInfoDesc) |

### 필드 명명 규칙 (★핵심)
각 항목의 `fields` 는 `<Prefix>_<LANG>` 형태. 언어 코드: `CHT`(번체·원작 기준), `EN`, `JP`, `CHS`(간체).
- 일반 시트/스토리/메일: `Name_CHT`, `Name_EN`, `Text_CHT`, `Title_EN` …
- **StringDataLocalization만 예외**: prefix 없이 `CHT`/`EN`/`JP`/`CHS` (locKey가 곧 의미).

**한국어 추가 = 각 항목에 `<Prefix>_KR` 필드(또는 StringData는 `KR` 필드)를 넣기만 하면 됨.** 게임이 KR 선택 시 `fields[prefix + "KR"]`를 찾는다(데이터 기반 조회, 코드 수정 불필요).

## 2. 언어 선택 메커니즘

- `EnumLanguage`(Sigono.Utilities)에 **KR이 index 8로 이미 존재**. 필드 조회는 `fields[prefix + lang.ToString()]` → `lang=KR` → `..._KR`.
- 현재 언어는 **OptionSaveData**에서 옴 (`hasSelectedLanguage ? saved : systemLanguage`). PlayerPrefs 아님.
- **KR을 옵션 언어 목록에 노출**하려면: `LanguageSettings` ScriptableObject(sharedassets2 MonoBehaviour, 예 pid **75401**)에 KR 항목 추가 — `lang=8, txtLang="한국어", steamEnable=1`. 이걸 넣어야 설정 메뉴에서 한국어를 고를 수 있다.

## 3. 폰트 시스템

- TMP Dynamic SDF. 한글 글리프가 있는 폰트가 필요.
- **검증된 방법: 기존 폰트 오브젝트를 clone 해 KR 전용 TMP_FontAsset 을 신설**하고 FontSettings 로 배선. 구현·자동화는 `Common/scripts/build_krfont.py`. 세 오브젝트를 clone(=기존 로드 가능한 오브젝트의 raw data 복사 + 새 `path_id` 부여, `maxpid+1/2/3`)한다:
  1. **Font** `2184`(원래 GlowSansJ-Normal-Regular) → clone 후 `m_FontData`를 **Noto Sans CJK KR** OTF 로 교체, 이름 `NotoSansCJKkr-Regular`.
  2. **SDF Atlas Texture** `148` → clone, 이름 `NotoSansCJKkr-Regular SDF Atlas`.
  3. **TMP_FontAsset** `75388`(템플릿) → clone 후 `m_SourceFontFile`→신규 Font, `m_AtlasTextures`→신규 Atlas 로 연결, 이름 `NotoSansCJKkr-Regular SDF`.
- `FontSettings` SO(예 pid `75398`)의 각 `_fontAssetMappings`(Default/Bold 등) 항목에 **KR(`language=8`) 매핑**을 추가 — 기존 CHT 항목을 복제해 `fallbackFonts`를 신규 TMP(위 3)로 지정.
- **주의**: 아무 필드나 채운 Font 를 맨바닥에서 "새로 만들어" 추가하면 Unity 가 로드하지 못해 렌더 실패할 수 있다. 반드시 게임이 실제로 로드하는 기존 오브젝트를 **clone**(raw data 복사)해 구조를 보존할 것. (초기엔 sharedassets0 의 Font 를 in-place 교체하는 방식도 썼으나, TMP 파이프라인은 위 clone 방식으로 정착.)
- JP 글리프는 Noto CJK KR 에 포함되어 기능 손실 없음.
- 검증: `Common/scripts/verify_krfont.py`(신규 Font/Atlas/TMP + FontSettings KR 매핑을 이름 기준 확인). 위 구성으로 인게임 한글 렌더 정상 확인됨.
- 게임 업데이트 시 pid(`2184/148/75388/75398`)가 바뀔 수 있음 → `build_krfont.py` 상단 `SRC_*` 상수를 이름으로 재확인.

## 4. 화자(Actor) 매핑 — 대사 번역의 핵심

StoryLocalization은 uid만 있고 **화자 필드가 없다**. 화자는 대화 그래프에서 얻는다.

- NodeCanvas DialogueTree 그래프는 **압축 번들이 아니라 `level*` / `sharedassets*.assets` 에 그대로**(uncompressed) 들어 있음.
- 각 대사 노드 두 형태:
  - 캐릭터: `"actorRef":{"uid":"<ACTOR_GUID>"} … "_UID":"<STORY_UID>"`
  - 내레이션: `"_actorName":"Narrator" … "_UID":"<STORY_UID>"`
- **ACTOR_GUID → 이름**: 각 액터는 sharedassets2의 **개별 ActorSetup MonoBehaviour**(예 pid 75452)에 `Actor_<Role>`(locKey) + uid + CHT명(艾妲 등) 보관.
- 조인: STORY_UID → ACTOR_GUID → (locKey, CHT명) → 화자 이름. 커버리지 4515/4728(95%).
- 화자 표시 이름표는 **StringDataLocalization의 `Actor_*` locKey**(예 Actor_Man=李莫). 이것도 KR 번역 대상(대사 위에 뜨는 이름).

## 5. 백업·안전

- `sharedassets2.assets.bak` = 원본(pristine).
- `sharedassets2.assets.fontready` = 폰트+KR언어 설정만 적용, 텍스트 없음(주입 베이스).
- 게임 업데이트 시 sharedassets2가 바뀔 수 있으므로, 업데이트 후에는 **새 원본에서 폰트/언어 설정 + 텍스트 주입을 다시** 수행. (structure는 대체로 동일하나 pid는 달라질 수 있으니 이름으로 조회할 것.)
