# 추출·분석·툴링 (언어 무관)

## 텍스트 테이블 추출
sharedassets2의 TextAsset 11개는 JSON이라 그대로 파싱:
```python
import UnityPy, json
env = UnityPy.load("sharedassets2.assets")   # 또는 .bak
for o in env.objects:
    if o.type.name=="TextAsset":
        d=o.read()
        if d.m_Name=="StoryLocalization":
            arr=json.loads(d.m_Script if isinstance(d.m_Script,str) else bytes(d.m_Script).decode("utf-8","surrogateescape"))
```
- 시트 항목 키: `id`(정수). StringData: `locKey`. Story: `uid`(GUID).
- 4개 언어 병렬(CHT/EN/JP/CHS)이 한 항목에 다 있어 **교차 대조가 쉬움**(번역 품질·의미 판별에 활용).

## 화자 매핑 추출 (대사)
`level*` + `sharedassets*.assets`를 바이트로 읽어 정규식(latin-1):
```python
char = re.compile(rb'"actorRef":\{"uid":"([0-9a-f\-]{36})"\}.{0,600}?"_UID":"([0-9a-f\-]{36})"', re.S)
narr = re.compile(rb'"_actorName":"Narrator".{0,600}?"_UID":"([0-9a-f\-]{36})"', re.S)
```
→ (STORY_UID, ACTOR_GUID) / Narrator. ACTOR_GUID→이름은 sharedassets2의 개별 ActorSetup MB에서 Unity length-prefixed 문자열 파싱(`Actor_<Role>` + uid + CHT명). 결과 산출물: `Common/Characters/uid2speaker.json`, `Common/Characters/actor_defs.json`(세 변형 공통).

## 音譯(음차) 판별 — pypinyin
중국어판은 서양 고유명도 한자 음역(예 梅費爾=Mayfair). `pip install pypinyin`:
```python
from pypinyin import lazy_pinyin
py = "".join(lazy_pinyin("梅費爾"))   # meifeier ≈ EN "Mayfair" → 음차 → EN 따름
```
CHT 병음 vs EN 대조로 ①음차(EN 따름) ②의역 ③병음 ④신·라틴 개명(한자음 유지)을 분류. 상세 규칙은 Trans-Complex2KR/decisions §11.

## 다중 에이전트 워크플로우 (대량 번역/교체)
- 슬라이스 파일(연속 문맥 포함)로 나눠 병렬 에이전트가 각자 처리 → 결과 병합.
- **함정**:
  - 워크플로우 스크립트에 데이터를 **임베드하면 U+2028/U+2029(비ASCII 줄 구분자)로 파싱 실패**. → 에이전트가 슬라이스 파일을 Read 하게 하거나 `ensure_ascii=True`.
  - 에이전트가 일부 항목을 누락 → **커버리지 검사 후 누락분만 재실행**.
  - 지출 한도(spend limit) 도달 시 부분 완료 → 부분 저장 후 크레딧 추가/리셋 후 재개.
- 대사는 **StoryLocalization JSON 순서 = 서사 순**이라 연속 슬라이스로 문맥 유지 가능.

## 흔한 소급 교체 함정
- **흔한 음절 고유명(예 汜=사)을 다른 말로 바꿀 때 blind replace 금지**: "사"는 사람/사실/역사/사기꾼/사수(射手)/사정(事情)과 겹침 → **CHT 대조 에이전트 교체**로만.
- **조사(받침) 교정**: 모음종결↔자음종결이 바뀌면 조사도 바꿔야 함(예 사→영: 사를→영을, 사가→영이). 병기 형태(예 「을황」은)의 조사도 확인.

## 스크린샷(진단용)
`Graphics.CopyFromScreen`은 D3D 창모드에서 동작(PrintWindow는 검은 화면). 창모드 전환: 레지스트리 `Screenmanager Fullscreen mode_h3630240806=3`.

## 파일명 주의
`inspect.py` 등 stdlib 이름과 겹치는 스크립트명 금지(import 충돌).
