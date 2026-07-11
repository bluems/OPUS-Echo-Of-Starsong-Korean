# Common — 언어 무관 공통 자료

OPUS: Echo of Starsong 한국어(또는 임의 언어) 번역에 공통으로 쓰이는 게임 구조·주입·툴링 자료.

- **`game-file-structure.md`** — 로컬라이제이션 TextAsset 11개(pid 916–926) 목록·용도, `<Prefix>_<LANG>` 필드 규칙(KR 추가법), 언어 선택(LanguageSettings/EnumLanguage.KR), 폰트 시스템(Noto CJK repurpose), 화자 매핑 원리, 백업 정책.
- **`injection-guide.md`** — UnityPy로 `_KR` 필드 주입 절차 + **치명적 함정**(재로드-재저장 손상, HTML 이스케이프, 태그 보존, 검증법).
- **`extraction-and-tooling.md`** — 텍스트/화자 추출, 音譯 판별(pypinyin), 다중 에이전트 워크플로우, 소급 교체·조사 함정.
- **`scripts/inject_kr.py`** — 재사용 주입 스크립트. `python inject_kr.py <base.assets> <translations_dir> <out.assets>`.

## 빠른 시작 (게임 업데이트 후 재패치)
1. 새 `sharedassets2.assets` 백업 → 폰트/언어 설정 적용해 `.fontready` 생성(game-file-structure §2,§3).
2. TextAsset 항목 키(id/uid/locKey)가 유지됐는지 확인.
3. `python Common/scripts/inject_kr.py sharedassets2.assets.fontready Trans-Complex2KR/translations sharedassets2.assets`
4. 검증(injection-guide) → 인게임 한글 확인.
