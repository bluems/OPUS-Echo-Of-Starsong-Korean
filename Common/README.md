# Common — 언어 무관 공통 자료

OPUS: Echo of Starsong 한국어(또는 임의 언어) 번역에 공통으로 쓰이는 게임 구조·주입·툴링 자료.

- **`game-file-structure.md`** — 로컬라이제이션 TextAsset 11개(pid 916–926) 목록·용도, `<Prefix>_<LANG>` 필드 규칙(KR 추가법), 언어 선택(LanguageSettings/EnumLanguage.KR), 폰트 시스템(Noto CJK repurpose), 화자 매핑 원리, 백업 정책.
- **`injection-guide.md`** — UnityPy로 `_KR` 필드 주입 절차 + **치명적 함정**(재로드-재저장 손상, HTML 이스케이프, 태그 보존, 검증법).
- **`extraction-and-tooling.md`** — 텍스트/화자 추출, 音譯 판별(pypinyin), 다중 에이전트 워크플로우, 소급 교체·조사 함정.
- **`Assets/NotoSansCJKkr-Regular.otf`** — 한글 폰트 소스(Noto Sans CJK KR). TMP 폰트 생성 입력. 라이선스: `Assets/LICENSE-OFL.txt`.
- **`scripts/build_krfont.py`** — 폰트 TMP 생성 스크립트. sharedassets2 에 Noto CJK KR TMP_FontAsset 을 만들고 FontSettings 에 KR 매핑 배선 → `.fontready` 생성. `python build_krfont.py <game_data_dir> [out.assets] [noto.otf]`.
- **`scripts/verify_krfont.py`** — 폰트 TMP 검증(신규 Font/Atlas/TMP + FontSettings KR 매핑, 이름 기준 조회). `python verify_krfont.py <game_data_dir> [target.assets]`.
- **`scripts/inject_kr.py`** — 재사용 주입 스크립트. `python inject_kr.py <base.assets> <translations_dir> <out.assets>`.
- **`Characters/`** — 게임 소스에서 추출한 **변형 무관 화자/액터 참조 자료**(한국어 없음, 세 변형 공통).
  - `characters.json` — 액터 다국어 대조표(key/CHT/EN/JP/CHS).
  - `uid2speaker.json` — 대사 uid → 화자(4515 매핑). 화자별 재번역 시 참조.
  - `actor_defs.json` — 액터 54종 정의(GUID→locKey→CHT명).
- **`translation_keys.json`** — **공통 키 매니페스트**. 모든 `Trans-*/translations/*_kr.json` 이 따라야 할 파일별 키(UUID) 집합·순서. 게임 소스 파생.
- **`scripts/check_keys.py`** — 변형 간 **키 드리프트 검증**(누락/초과/순서). `python Common/scripts/check_keys.py [변형...] [--strict]`. 매니페스트 재생성은 `--update`. `build_assets.py` 가 빌드 전 자동 호출(`--no-check` 로 생략).

## 빠른 시작 (게임 업데이트 후 재패치)
1. 새 `sharedassets2.assets` 백업(pristine).
2. `python Common/scripts/build_krfont.py "<...>/OPUS Echo of Starsong_Data" Trans-Complex2KR/build/sharedassets2.assets.fontready` → 폰트/언어 설정 적용된 `.fontready` 생성(game-file-structure §2,§3).
3. `python Common/scripts/verify_krfont.py "<...>/OPUS Echo of Starsong_Data" Trans-Complex2KR/build/sharedassets2.assets.fontready` 로 폰트 배선 확인.
4. TextAsset 항목 키(id/uid/locKey)가 유지됐는지 확인.
5. `python Common/scripts/inject_kr.py Trans-Complex2KR/build/sharedassets2.assets.fontready Trans-Complex2KR/translations sharedassets2.assets`
6. 검증(injection-guide) → 인게임 한글 확인.

## 폰트 출처·라이선스
- **Noto Sans CJK KR** (`Assets/NotoSansCJKkr-Regular.otf`) — © Google / Adobe. **SIL Open Font License 1.1** (전문: `Assets/LICENSE-OFL.txt`).
- OFL 1.1은 원본의 repo 포함·재배포, 소프트웨어(게임 assets) 번들·임베드를 허용. 조건: 복사본에 저작권 고지+라이선스 동봉, 폰트 단독 판매 금지, 수정본은 Reserved Font Name(`Source`/`Noto`) 사용 금지·OFL 유지. 원본을 수정 없이 포함하는 본 repo는 라이선스 파일 동봉으로 요건 충족.
