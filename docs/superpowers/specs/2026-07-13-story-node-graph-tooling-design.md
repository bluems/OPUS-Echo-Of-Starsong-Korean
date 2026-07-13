# 스토리 노드 그래프 툴링 & Guard 말투 교정 — 설계

- 날짜: 2026-07-13
- 대상 변형: Trans-Complex2KR (교정 대상), 그래프 도구는 3개 변형 공통
- 발단: `Trans-Complex2KR/translations/story_kr.json`의 `ccbd8ce6-c8e1-45b3-b6fa-f3868f11efe1`
  (화자 `Actor_Guard`) 대사가 대화 상대(선행 노드)와 말투(존대/반말)가 어긋남.

## 배경 / 데이터 모델

- `translations/story_kr.json` = `uid → 한국어 텍스트` 평면 맵. **노드 선후·씬·분기 정보 없음.**
- 노드 그래프는 **원본 게임 데이터**(`E:\SteamLibrary\steamapps\common\OPUS Echo of Starsong\OPUS Echo of Starsong_Data`)의
  NodeCanvas 기반 `DialogueTree` MonoBehaviour에 직렬화되어 있음.
  - `StatementNode : DTNode` — `statement`(스토리 uid 보유) + `actorRef`(화자 GUID).
  - `MultipleChoiceNode : DTNode` — 분기.
  - `DTNode` 연결(connection) = 대사 진행 간선.
- 화자 매핑은 이미 산출됨: `Common/Characters/uid2speaker.json`(uid→actor/cht/guid),
  `Common/Characters/actor_defs.json`(guid→locKey/cht).
- 참고: `Common/extraction-and-tooling.md` — UnityPy 로드, TypeTreeGenerator(2020.3.35f1),
  화자 매핑 정규식(`"actorRef":{"uid":"…"}.{0,600}?"_UID":"…"`) 등 이전 세션 확립 방식.
- 확정 사실: `ccbd8ce6…` 화자 = `Actor_Guard`(초상 `大魁`). `大魁` = 케이(Kay). 문제 대사는
  반말체("…신경 쓰지 마."), 케이 페르소나는 준에게 `少主/도련님` 존대.

## 목표

1. 전체 스크립트의 uid 노드 그래프를 원본에서 추출해 저장(반복 분석 대비).
2. 임의 uid를 주면 **같은 씬 내 선행/후행 화자·문맥**을 추출하는 조회 도구(탐색 낭비 절감).
3. `Actor_Guard`(케이) 발화체를 페르소나·대화 상대 관계에 맞게 교정(이 씬 + Guard 전수 점검).

비목표(YAGNI): GUI/시각화, 그래프 편집, 다른 캐릭터 전면 말투 감사, 원본 데이터 수정.

## 산출물 위치

- 스크립트: `Common/scripts/` (기존 `check_keys.py`와 동일 위치, git 커밋, 3변형 공통).
- 그래프 산출물: `Common/Characters/node_graph.json` (커밋).
- 교정: `Trans-Complex2KR/translations/story_kr.json`, 규칙은 `decisions/localization_decisions.md`.

## 컴포넌트

### 1. `Common/scripts/build_node_graph.py` — 그래프 추출기(1회성 빌드)

- 입력: 원본 데이터 경로(기본값 위 경로, `--data` 오버라이드) + `uid2speaker.json`.
- 처리:
  1. UnityPy로 `level*` + `sharedassets*.assets` 로드.
  2. TypeTreeGenerator로 `DialogueTree` 및 노드 타입 타입트리 확보.
  3. 각 `DialogueTree`에서 노드 목록·연결 추출.
     - 노드별: `uid`(StatementNode.statement), `type`(statement/choice/timeline/sub/…),
       `actor`(uid2speaker 결합), `text_preview`(선택), `out`(연결된 다음 노드 uid 목록).
     - 분기(MultipleChoiceNode)는 다중 out.
  4. `DialogueTree` = 씬(대화 단위)으로 그룹.
- 출력 스키마(`node_graph.json`):
  ```json
  {
    "scenes": {
      "<tree_id>": {
        "source": "level12",
        "entry": "<uid>",
        "nodes": [
          {"uid": "…", "type": "statement", "actor": "Actor_Guard",
           "cht": "大魁", "out": ["…", "…"]}
        ]
      }
    },
    "uid_index": { "<uid>": {"scene": "<tree_id>", "idx": 12} }
  }
  ```
- 실패 대비: 노드 uid가 story uid를 대다수 커버하는지 커버리지 리포트 출력.
  누락 노드 타입은 경고로 남기고 계속.

### 2. `Common/scripts/scene_context.py` — 씬 컨텍스트 조회기(반복 사용 핵심)

- 입력: `<uid>` (+ `node_graph.json`, variant의 `story_kr.json`).
- 처리: `uid_index`로 씬 찾기 → 그래프상 선행(역간선)·후행(간선) 체인을 N-hop 추적 →
  각 노드에 화자·한국어 텍스트 결합. 분기 표시, 앞뒤 화자 전환 요약.
- CLI: `python Common/scripts/scene_context.py <uid> [--hops N] [--variant Complex2KR] [--json]`
- 출력(사람용 기본): 선행 → **대상 노드** → 후행 순의 `화자 | uid | 텍스트` 목록 + 화자 전환 요약.
  `--json`으로 기계 판독 형태.

### 3. Guard 말투 교정 (part 3)

- 절차:
  1. `Actor_Guard` uid 전부 수집(uid2speaker).
  2. 각 uid를 `scene_context`로 대화 상대(그래프 인접 화자) 파악.
  3. **선결 검증**: `Actor_Guard`(大魁)가 케이 본인인지/별개 단역인지 확정.
     - 별개면 그 단역 페르소나로, 케이면 케이 페르소나로 적용.
  4. 상대별 존대/반말 규칙 적용해 불일치 교정:
     - 준(少主/도련님) → 존대. 에다·본즈·적 등 → 페르소나상 투박/반말 가능.
  5. `story_kr.json` 수정, 조사(받침)·줄바꿈(`\n`, `<p>`) 무결성 유지.
  6. 교정 규칙을 `localization_decisions.md`에 기록.

## 데이터 흐름

```
원본 게임데이터 ──build_node_graph──▶ node_graph.json ──scene_context──▶ 문맥/화자
                                            │                              │
                          uid2speaker.json ─┘                              ▼
                                                            Guard 전수 교정 ▶ story_kr.json
```

## 테스트 / 검증

- `build_node_graph`:
  - 골든: `ccbd8ce6…`가 그래프에 존재, 선행에 `8a9288f1…`("이건... 영해 물건 같은데?") 포함.
  - 커버리지 리포트: story uid 대비 그래프 커버율 출력(대다수 커버 기대).
- `scene_context`:
  - `ccbd8ce6…` 질의 → 앞뒤 화자·텍스트가 story_kr 인접 문맥과 정합.
- 교정:
  - 수정 후 `json.load` 유효, 조사/줄바꿈 무결, 대상 노드 말투가 상대와 정합.

## 핵심 리스크 / 미결

- **NodeCanvas 직렬화 스키마**: 연결(connection) 표현 방식은 실제 파싱으로 확정 필요.
  이전 세션에서 `actorRef…_UID` 인접 정규식이 동작한 정황상 그래프가 JSON 텍스트로
  직렬화돼 있어 추출 가능성 높음. **구현 1단계에서 소규모 feasibility 프로브로 스키마 확정**,
  실패 시 대안(StoryLocalization 선형 순서 + 화자 근사)로 폴백하고 사용자에 보고.
- `Actor_Guard` 정체(케이 vs 단역)는 교정 전 검증 항목.
