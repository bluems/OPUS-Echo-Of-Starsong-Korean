# OPUS: Echo of Starsong — 한국어 번역 프로젝트

SIGONO의 *OPUS: Echo of Starsong*(별노래의 메아리, Steam appid 1504500 Full Bloom Edition) **비공식 한국어 패치** 작업 자료. 게임 업데이트·번역 수정 시 재사용을 위한 정리본.

개발사가 Steam에서 언어 패치를 긍정적으로 허용. 패치는 전적으로 `sharedassets2.assets` 내에서 해결(sharedassets0 등 다른 파일 미수정).

## 디렉터리 구조

- **Common/** — **언어 무관** 공통 자료. 어떤 원어(EN/JP/CHT/복합)에서 번역하든 동일하게 쓰이는 게임 파일 구조·주입 방법·추출/툴링.
  - `game-file-structure.md` — 로컬라이제이션 TextAsset 목록·필드 규칙·언어 선택·폰트·화자 매핑.
  - `injection-guide.md` — UnityPy로 `_KR` 필드 주입 절차 + 치명적 함정(재저장 손상, HTML 이스케이프 등).
  - `extraction-and-tooling.md` — 추출·화자 매핑·음차 판별(pypinyin)·워크플로우·소급 교체 함정.

- **Trans-Complex2KR/** — 이번 번역(원어 판단 방식별) 산출물. **중국어(원작·문체 기준)+일본어(뉘앙스)+영어(의미·공식명)를 복합 판단**해 번역했으므로 `Complex`.
  - `decisions/` — 로컬라이제이션 결정 기록(모든 판단·근거).
  - `glossary/` — 마스터 용어집, 고유명 교차언어표, 지명/세력/인물.
  - `characters/` — 인물 페르소나·보이스 프로필, 화자 매핑(uid→화자).
  - `translations/` — 최종 KR 번역 전량(*_kr.json).

- **Trans-EN2KR/**, **Trans-CHT2KR/** — (예약) 특정 단일 원어 기반 번역을 별도로 만들 경우의 자리.

## 번역 원칙 요약 (상세: Trans-Complex2KR/decisions)
- 의미=EN, 문체·register·고유명 한자음=CHT, 뉘앙스=JP 교차 참조.
- 인물 개인명=EN 공식명. 단 李(Lee)가문=한국식 이씨(이준/이현), 신·신화명=한자음(만도·흑룡·을황·태을·영靈…).
- 서양 이름의 한자 음역(음차)은 EN 발음 따름(메이페어·마르세유…).
- 화자별 말투·존댓말·호칭을 대사 분석으로 정의해 적용.

## 최종 상태 (2026-07-12)
전 배치 번역·검수·주입 완료, **인게임 한글 렌더 검증 완료**. UI·지명·아이템·제작법·상점·비밀지점·사건·대사(4728)·메일(51) 전량.
