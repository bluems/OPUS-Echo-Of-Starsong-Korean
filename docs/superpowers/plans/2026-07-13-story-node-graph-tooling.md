# 스토리 노드 그래프 툴링 & Guard 말투 교정 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 원본 게임 데이터에서 대사 노드 그래프를 추출·저장하고, uid로 씬 문맥을 조회하는 도구를 만든 뒤, 그 근거로 `Actor_Guard`(케이) 말투를 교정한다.

**Architecture:** 원본 `sharedassets*.assets`에 임베드된 NodeCanvas `DialogueTree` JSON 블록을 원시 바이트에서 추출→파싱해 씬별 방향 그래프(`node_graph.json`)를 만든다. 조회 도구가 이 그래프 + `uid2speaker.json` + variant `story_kr.json`을 결합해 임의 uid의 선행/후행 화자·문맥을 낸다. 교정은 이 도구 산출물을 근거로 진행한다.

**Tech Stack:** Python 3, 표준 라이브러리(json/glob/re)만으로 추출 가능(UnityPy 불필요 — JSON이 평문 임베드). pytest.

## Global Constraints

- 실행 환경: Windows / PowerShell. 파이썬은 `python`.
- 원본 게임 데이터 경로(기본값): `E:\SteamLibrary\steamapps\common\OPUS Echo of Starsong\OPUS Echo of Starsong_Data`. **원본은 읽기 전용 — 절대 수정 금지.** `--data`로 오버라이드 가능.
- DialogueTree 추출 마커: `{"type":"NodeCanvas.DialogueTrees.DialogueTree"`. 스캔 대상: `sharedassets*.assets` + `level*`(`.resS` 제외). 43개 파일에 663 트리, 파싱 실패 0 검증됨.
- 노드 JSON 필드: `$id`(트리 내 로컬), `$type`(마지막 세그먼트가 노드 클래스), `_UID`(스토리 uid, StatementNode만), `actorRef.uid`(화자 GUID), `statement._text`(CHT 원문), `_serialId`. 연결: `connections[].{_sourceNode.$ref → _targetNode.$ref}`.
- 화자 매핑: `Common/Characters/actor_defs.json`(GUID→{locKey,cht}), `Common/Characters/uid2speaker.json`(스토리uid→{actor,cht,guid}). 이미 존재.
- 모든 JSON 출력은 **UTF-8, `ensure_ascii=False`**(한국어/한자 보존).
- 산출물 `Common/Characters/node_graph.json`은 커밋. 스크립트는 `Common/scripts/`에 커밋(3변형 공통).
- 교정 대상은 `Trans-Complex2KR/translations/story_kr.json`. 조사(받침)·줄바꿈(`\n`,`<p>`) 무결성 유지, 수정 후 `json.load` 유효.
- 커버리지 기대치: story uid의 ~96%가 그래프에 존재(미커버는 내레이션/타이틀/UI 계열).

---

### Task 1: `node_graph_lib.py` — 추출·그래프 빌드 라이브러리 + `build_node_graph.py` CLI

**Files:**
- Create: `Common/scripts/node_graph_lib.py`
- Create: `Common/scripts/build_node_graph.py`
- Create: `Common/scripts/tests/test_node_graph_lib.py`
- Produces (committed by CLI): `Common/Characters/node_graph.json`

**Interfaces:**
- Produces (라이브러리 공개 API):
  - `extract_tree_blobs(raw: bytes) -> list[tuple[str, str]]` — `(tree_name, json_text)` 목록. `tree_name`은 블록 앞 64바이트 내 마지막 `[A-Za-z0-9_\-]{3,}` 토큰(없으면 `"?"`).
  - `parse_tree(tree_name: str, json_text: str, actor_defs: dict) -> dict` — 씬 1개를 그래프 dict로:
    `{"name": str, "nodes": [{"id": str, "type": str, "uid": str|None, "actor": str|None, "cht": str|None, "text": str, "out": [str,...]}], "entry": str|None}`.
    `out`은 connections에서 이 노드($id)가 source인 target $id 목록. `actor`/`cht`는 `actor_defs[actorRef.uid]`에서(없으면 None). `entry`는 어떤 연결의 target도 아닌 첫 노드 $id.
  - `build_graph(data_dir: str, actor_defs: dict) -> dict` — 전 파일 스캔 결과
    `{"scenes": {<scene_key>: <parse_tree 결과>}, "uid_index": {<story_uid>: {"scene": <scene_key>, "id": <node $id>}}}`.
    `scene_key`는 `tree_name`; 충돌 시 `f"{name}#{n}"`.
- Consumes: 없음(표준 라이브러리).

- [ ] **Step 1: 실패하는 테스트 작성**

`Common/scripts/tests/test_node_graph_lib.py`:
```python
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import node_graph_lib as lib

# 최소 DialogueTree JSON 블록(마커 포함) — 3노드 선형 체인 + 화자
BLOB = (
    '{"type":"NodeCanvas.DialogueTrees.DialogueTree","nodes":['
    '{"$type":"River.Incident.EventInfoNode","$id":"0"},'
    '{"statement":{"_text":"A"},"actorRef":{"uid":"guid-jun"},"_UID":"uid-a",'
    '"$type":"NodeCanvas.DialogueTrees.StatementNode","$id":"1"},'
    '{"statement":{"_text":"B"},"actorRef":{"uid":"guid-guard"},"_UID":"uid-b",'
    '"$type":"NodeCanvas.DialogueTrees.StatementNode","$id":"2"}],'
    '"connections":['
    '{"_sourceNode":{"$ref":"0"},"_targetNode":{"$ref":"1"},"$type":"x.DTConnection"},'
    '{"_sourceNode":{"$ref":"1"},"_targetNode":{"$ref":"2"},"$type":"x.DTConnection"}]}'
)
ACTOR_DEFS = {"guid-jun": {"locKey": "Actor_Jun", "cht": "李莫"},
              "guid-guard": {"locKey": "Actor_Guard", "cht": "大魁"}}

def test_extract_blob_with_name():
    raw = (b"\x00\x00DT_Test\x08\x00\x00\x00" + BLOB.encode("utf-8") + b"\x00\x00")
    blobs = lib.extract_tree_blobs(raw)
    assert len(blobs) == 1
    name, txt = blobs[0]
    assert name == "DT_Test"
    assert json.loads(txt)["type"] == "NodeCanvas.DialogueTrees.DialogueTree"

def test_parse_tree_chain_and_actors():
    tree = lib.parse_tree("DT_Test", BLOB, ACTOR_DEFS)
    nodes = {n["id"]: n for n in tree["nodes"]}
    assert nodes["1"]["uid"] == "uid-a" and nodes["1"]["actor"] == "Actor_Jun"
    assert nodes["2"]["uid"] == "uid-b" and nodes["2"]["actor"] == "Actor_Guard"
    assert nodes["0"]["out"] == ["1"]
    assert nodes["1"]["out"] == ["2"]
    assert tree["entry"] == "0"

def test_build_graph_uid_index():
    # BLOB을 임시 .assets로 저장 후 build_graph
    import tempfile
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "sharedassets99.assets"), "wb") as f:
        f.write(b"\x00\x00DT_Test\x08\x00\x00\x00" + BLOB.encode("utf-8"))
    g = lib.build_graph(d, ACTOR_DEFS)
    assert "uid-a" in g["uid_index"]
    assert g["uid_index"]["uid-b"]["id"] == "2"
    assert g["uid_index"]["uid-b"]["scene"] in g["scenes"]
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `python -m pytest Common/scripts/tests/test_node_graph_lib.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'node_graph_lib'`

- [ ] **Step 3: 라이브러리 구현**

`Common/scripts/node_graph_lib.py`:
```python
"""원본 게임 데이터의 NodeCanvas DialogueTree를 씬별 방향 그래프로 추출한다."""
import os, glob, json, re

MARKER = b'{"type":"NodeCanvas.DialogueTrees.DialogueTree"'
_NAME_RE = re.compile(rb'([A-Za-z0-9_\-]{3,})')

def extract_tree_blobs(raw):
    """raw 바이트에서 DialogueTree JSON 블록을 균형 중괄호로 추출. (name, json_text) 목록."""
    out = []
    i = 0
    while True:
        j = raw.find(MARKER, i)
        if j < 0:
            break
        depth = 0; k = j; instr = False; esc = False
        while k < len(raw):
            ch = raw[k]
            if esc:
                esc = False
            elif ch == 0x5c:      # backslash
                esc = True
            elif ch == 0x22:      # double quote
                instr = not instr
            elif not instr:
                if ch == 0x7b:    # {
                    depth += 1
                elif ch == 0x7d:  # }
                    depth -= 1
                    if depth == 0:
                        k += 1
                        break
            k += 1
        blob = raw[j:k]
        back = raw[max(0, j - 64):j]
        m = _NAME_RE.findall(back)
        name = m[-1].decode("ascii", "replace") if m else "?"
        out.append((name, blob.decode("utf-8")))
        i = k
    return out

def parse_tree(tree_name, json_text, actor_defs):
    g = json.loads(json_text)
    raw_nodes = g.get("nodes", [])
    # $id -> out targets
    outs = {}
    targets = set()
    for c in g.get("connections", []):
        s = (c.get("_sourceNode") or {}).get("$ref")
        t = (c.get("_targetNode") or {}).get("$ref")
        if s is None or t is None:
            continue
        outs.setdefault(s, []).append(t)
        targets.add(t)
    nodes = []
    for n in raw_nodes:
        nid = n.get("$id")
        actor_uid = (n.get("actorRef") or {}).get("uid")
        ad = actor_defs.get(actor_uid) if actor_uid else None
        nodes.append({
            "id": nid,
            "type": n.get("$type", "").split(".")[-1],
            "uid": n.get("_UID"),
            "actor": ad["locKey"] if ad else None,
            "cht": ad["cht"] if ad else None,
            "text": (n.get("statement") or {}).get("_text", ""),
            "out": outs.get(nid, []),
        })
    entry = next((n["id"] for n in nodes if n["id"] not in targets), None)
    return {"name": tree_name, "nodes": nodes, "entry": entry}

def build_graph(data_dir, actor_defs):
    files = sorted(glob.glob(os.path.join(data_dir, "sharedassets*.assets"))
                   + glob.glob(os.path.join(data_dir, "level*")))
    files = [f for f in files if not f.endswith(".resS") and os.path.isfile(f)]
    scenes = {}
    uid_index = {}
    for f in files:
        with open(f, "rb") as fh:
            raw = fh.read()
        if MARKER not in raw:
            continue
        for name, txt in extract_tree_blobs(raw):
            tree = parse_tree(name, txt, actor_defs)
            key = name
            n = 1
            while key in scenes:
                key = f"{name}#{n}"; n += 1
            tree["source"] = os.path.basename(f)
            scenes[key] = tree
            for nd in tree["nodes"]:
                if nd["uid"]:
                    uid_index[nd["uid"]] = {"scene": key, "id": nd["id"]}
    return {"scenes": scenes, "uid_index": uid_index}
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `python -m pytest Common/scripts/tests/test_node_graph_lib.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: build CLI 구현**

`Common/scripts/build_node_graph.py`:
```python
"""원본 게임 데이터 → Common/Characters/node_graph.json 생성 + 커버리지 리포트."""
import os, json, argparse
import node_graph_lib as lib

DEFAULT_DATA = r"E:\SteamLibrary\steamapps\common\OPUS Echo of Starsong\OPUS Echo of Starsong_Data"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
ACTOR_DEFS = os.path.join(REPO, "Common", "Characters", "actor_defs.json")
OUT = os.path.join(REPO, "Common", "Characters", "node_graph.json")
STORY = os.path.join(REPO, "Trans-Complex2KR", "translations", "story_kr.json")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=DEFAULT_DATA)
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()
    actor_defs = json.load(open(ACTOR_DEFS, encoding="utf-8"))
    graph = lib.build_graph(args.data, actor_defs)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=1)
    scenes = graph["scenes"]; idx = graph["uid_index"]
    print(f"scenes={len(scenes)} node_uids={len(idx)} -> {args.out}")
    if os.path.exists(STORY):
        story = set(json.load(open(STORY, encoding="utf-8")).keys())
        cov = story & set(idx)
        print(f"story uids={len(story)} covered={len(cov)} ({100*len(cov)/len(story):.1f}%) "
              f"uncovered={len(story - set(idx))}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 6: 실제 데이터로 빌드 + 골든 검증**

Run:
```bash
cd "D:/my_projects/OPUS-Echo-Of-Starsong-Korean" && python Common/scripts/build_node_graph.py
python -c "import json; g=json.load(open('Common/Characters/node_graph.json',encoding='utf-8')); t=g['uid_index']['ccbd8ce6-c8e1-45b3-b6fa-f3868f11efe1']; sc=g['scenes'][t['scene']]; print('scene',t['scene']); [print(n['id'],n['type'],n['actor'],repr(n['text'][:20]),'->',n['out']) for n in sc['nodes']]"
```
Expected: `covered` ≈ 96%. 대상 scene = `DT_L2-4_30`, 노드 체인에 `8a9288f1`(이건... 영해 물건 같은데?) → `83833d6a`(......) → `ccbd8ce6`(Guard) 순서와 `out` 연결 확인.

- [ ] **Step 7: 커밋**

```bash
git add Common/scripts/node_graph_lib.py Common/scripts/build_node_graph.py Common/scripts/tests/test_node_graph_lib.py Common/Characters/node_graph.json
git commit -m "feat(scripts): DialogueTree 노드 그래프 추출기 + node_graph.json"
```

---

### Task 2: `scene_context.py` — uid 씬 문맥 조회기

**Files:**
- Create: `Common/scripts/scene_context.py`
- Create: `Common/scripts/tests/test_scene_context.py`

**Interfaces:**
- Consumes: `node_graph.json`(Task 1 산출), `uid2speaker.json`, variant `story_kr.json`.
- Produces:
  - `load_context(uid, graph, story_kr) -> dict` —
    `{"scene": str, "target": <node>, "before": [<node>...], "after": [<node>...]}`.
    각 `<node>`는 `{"id","type","uid","actor","cht","kr","out"}` (kr = `story_kr.get(uid,"")`).
    `before`는 대상까지의 역방향 체인(그래프 in-edge를 거슬러, statement 노드 위주, 최대 hops),
    `after`는 정방향 체인(out을 따라, 분기 시 각 분기 첫 statement 표시), 각각 최대 `hops`개.
  - CLI: `python Common/scripts/scene_context.py <uid> [--hops N=6] [--variant Complex2KR] [--json]`.

- [ ] **Step 1: 실패하는 테스트 작성**

`Common/scripts/tests/test_scene_context.py`:
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import scene_context as sc

GRAPH = {
    "scenes": {"DT_X": {"name": "DT_X", "source": "s.assets", "entry": "0", "nodes": [
        {"id": "0", "type": "EventInfoNode", "uid": None, "actor": None, "cht": None, "text": "", "out": ["1"]},
        {"id": "1", "type": "StatementNode", "uid": "u1", "actor": "Actor_Jun", "cht": "李莫", "text": "A", "out": ["2"]},
        {"id": "2", "type": "StatementNode", "uid": "u2", "actor": "Actor_Guard", "cht": "大魁", "text": "B", "out": ["3"]},
        {"id": "3", "type": "StatementNode", "uid": "u3", "actor": "Actor_Eda", "cht": "艾妲", "text": "C", "out": []},
    ]}},
    "uid_index": {"u1": {"scene": "DT_X", "id": "1"}, "u2": {"scene": "DT_X", "id": "2"},
                  "u3": {"scene": "DT_X", "id": "3"}},
}
STORY = {"u1": "가", "u2": "나", "u3": "다"}

def test_context_before_after():
    ctx = sc.load_context("u2", GRAPH, STORY, hops=6)
    assert ctx["scene"] == "DT_X"
    assert ctx["target"]["kr"] == "나" and ctx["target"]["actor"] == "Actor_Guard"
    assert [n["uid"] for n in ctx["before"]] == ["u1"]
    assert ctx["before"][0]["kr"] == "가"
    assert [n["uid"] for n in ctx["after"]] == ["u3"]
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `python -m pytest Common/scripts/tests/test_scene_context.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scene_context'`

- [ ] **Step 3: 구현**

`Common/scripts/scene_context.py`:
```python
"""임의 story uid의 같은 씬 내 선행/후행 화자·문맥을 추출한다."""
import os, json, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
GRAPH_PATH = os.path.join(REPO, "Common", "Characters", "node_graph.json")

def _view(node, story_kr):
    return {"id": node["id"], "type": node["type"], "uid": node["uid"],
            "actor": node["actor"], "cht": node["cht"],
            "kr": story_kr.get(node["uid"], "") if node["uid"] else "",
            "out": node["out"]}

def load_context(uid, graph, story_kr, hops=6):
    loc = graph["uid_index"][uid]
    scene = graph["scenes"][loc["scene"]]
    nodes = {n["id"]: n for n in scene["nodes"]}
    # in-edge map
    preds = {}
    for n in scene["nodes"]:
        for t in n["out"]:
            preds.setdefault(t, []).append(n["id"])
    def walk(start, nextfn, limit):
        seq = []
        cur = start; seen = set()
        while len(seq) < limit:
            nxts = nextfn(cur)
            if not nxts:
                break
            nid = nxts[0]           # 선형 우선; 분기는 첫 경로
            if nid in seen:
                break
            seen.add(nid)
            nd = nodes[nid]
            cur = nid
            if nd["type"] == "StatementNode":
                seq.append(_view(nd, story_kr))
        return seq
    before = list(reversed(walk(loc["id"], lambda c: preds.get(c, []), hops)))
    after = walk(loc["id"], lambda c: nodes[c]["out"], hops)
    return {"scene": loc["scene"], "target": _view(nodes[loc["id"]], story_kr),
            "before": before, "after": after}

def _fmt(n):
    return f"  {n['actor'] or '-':16s} | {n['uid'] or '':8.8s} | {n['kr'] or n['cht'] or ''}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("uid")
    ap.add_argument("--hops", type=int, default=6)
    ap.add_argument("--variant", default="Complex2KR")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    graph = json.load(open(GRAPH_PATH, encoding="utf-8"))
    story = json.load(open(os.path.join(
        REPO, f"Trans-{args.variant}", "translations", "story_kr.json"), encoding="utf-8"))
    if args.uid not in graph["uid_index"]:
        print(f"uid {args.uid} not in graph (내레이션/타이틀일 수 있음)"); return
    ctx = load_context(args.uid, graph, story, args.hops)
    if args.json:
        print(json.dumps(ctx, ensure_ascii=False, indent=1)); return
    print(f"scene={ctx['scene']}")
    print("[before]")
    for n in ctx["before"]:
        print(_fmt(n))
    print("[TARGET]")
    print(_fmt(ctx["target"]))
    print("[after]")
    for n in ctx["after"]:
        print(_fmt(n))

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `python -m pytest Common/scripts/tests/test_scene_context.py -v`
Expected: PASS

- [ ] **Step 5: 실제 데이터 조회 검증**

Run:
```bash
cd "D:/my_projects/OPUS-Echo-Of-Starsong-Korean" && python Common/scripts/scene_context.py ccbd8ce6-c8e1-45b3-b6fa-f3868f11efe1
```
Expected: `before`에 "이건... 영해 물건 같은데?" 등 선행 대사와 화자, `TARGET`에 Guard 대사가 표시. story_kr 인접(878–884행) 문맥과 정합.

- [ ] **Step 6: 커밋**

```bash
git add Common/scripts/scene_context.py Common/scripts/tests/test_scene_context.py
git commit -m "feat(scripts): uid 씬 문맥 조회기 scene_context.py"
```

---

### Task 3: Actor_Guard(케이) 말투 전수 점검 및 교정

**Files:**
- Modify: `Trans-Complex2KR/translations/story_kr.json`
- Modify: `Trans-Complex2KR/decisions/localization_decisions.md`
- (도구 사용) `Common/scripts/scene_context.py`, `Common/Characters/uid2speaker.json`, `Common/Characters/node_graph.json`

**Interfaces:**
- Consumes: Task 1·2 산출물.
- Produces: 교정된 `story_kr.json`(Complex2KR), 규칙 기록.

- [ ] **Step 1: Actor_Guard 정체 검증**

Run:
```bash
cd "D:/my_projects/OPUS-Echo-Of-Starsong-Korean" && python -c "
import json
u=json.load(open('Common/Characters/uid2speaker.json',encoding='utf-8'))
ad=json.load(open('Common/Characters/actor_defs.json',encoding='utf-8'))
gu=[k for k,v in u.items() if v.get('actor')=='Actor_Guard']
print('Actor_Guard 대사수:', len(gu))
from collections import Counter
print('cht 분포:', Counter(u[k].get('cht') for k in gu))
"
```
확인: `Actor_Guard`의 cht가 `大魁`(케이)인지, 다른 단역과 섞였는지. `character_personas.md`에서 케이 항목(gruff·fiercely-loyal·준에게 少主/도련님 존대) 재확인.
판단 규칙: cht가 大魁면 케이 페르소나 적용. 다른 cht가 섞이면 그 화자는 별도 취급하고 이 태스크에서 제외(사용자에 보고).

- [ ] **Step 2: Guard 전 대사 + 대화 상대 추출**

`scene_context.load_context`를 직접 호출해 모든 `Actor_Guard` 대사의 before/after 화자를 한 번에 수집한다.
Run:
```bash
cd "D:/my_projects/OPUS-Echo-Of-Starsong-Korean" && python -c "
import json, sys
sys.path.insert(0, 'Common/scripts')
import scene_context as sc
u = json.load(open('Common/Characters/uid2speaker.json', encoding='utf-8'))
graph = json.load(open('Common/Characters/node_graph.json', encoding='utf-8'))
story = json.load(open('Trans-Complex2KR/translations/story_kr.json', encoding='utf-8'))
guard = [k for k, v in u.items() if v.get('actor') == 'Actor_Guard']
print(f'Actor_Guard 대사 {len(guard)}건')
for uid in guard:
    if uid not in graph['uid_index']:
        continue
    ctx = sc.load_context(uid, graph, story, hops=2)
    prev = ctx['before'][-1] if ctx['before'] else None
    nxt = ctx['after'][0] if ctx['after'] else None
    print('---', uid, 'scene', ctx['scene'])
    print('  prev:', (prev['actor'], prev['kr'][:30]) if prev else None)
    print('  GUARD:', repr(ctx['target']['kr']))
    print('  next:', (nxt['actor'], nxt['kr'][:30]) if nxt else None)
" > Common/scripts/tests/_guard_audit.txt 2>&1
cat Common/scripts/tests/_guard_audit.txt | head -60
```
Expected: 각 Guard 대사의 직전(prev)·직후(next) 화자와 텍스트가 출력. 이 결과로 `uid | Guard 대사 | 직전 화자 | 직후 화자 | 현재 말투(존/반) | 상대 기준 적정 말투` 표를 정리한다. (`_guard_audit.txt`는 분석용 임시 파일 — 커밋하지 않음.)

- [ ] **Step 3: 불일치 판정 및 교정안 작성**

규칙:
- 상대가 **준(Actor_Jun 계열, 少主/도련님)** → 케이는 **존대체**(예: "~습니다/~하십시오", 도련님 호칭 유지).
- 상대가 **에다·본즈·적/외지인** → 페르소나상 **투박한 반말/거친 어조** 허용.
- 독백/내레이션성(상대 없음) → 기존 톤 유지하되 케이다움(무뚝뚝) 유지.
대상 노드 `ccbd8ce6`("이전에 온 탐사인이 두고 간 거겠지. 신경 쓰지 마.")는 before 화자를 보고, 준 대상이면 "…두고 간 것이겠지요. 신경 쓰지 마십시오." 류로 존대 교정(단, 실제 상대 확인 후 확정).
각 교정 후보를 `uid → 기존 → 교정` 목록으로 만든다.

- [ ] **Step 4: story_kr.json 교정 적용**

교정 목록을 `story_kr.json`(Complex2KR)에 반영. 각 수정 시:
- 조사(받침) 무결성 확인(모음/자음 종결 변화 시 조사 교정).
- 줄바꿈 토큰(`\n`, `<p>`) 원본 유지.
- 오직 판정된 uid만 수정(blind replace 금지).

- [ ] **Step 5: 검증**

Run:
```bash
cd "D:/my_projects/OPUS-Echo-Of-Starsong-Korean" && python -c "import json; json.load(open('Trans-Complex2KR/translations/story_kr.json',encoding='utf-8')); print('JSON OK')"
python Common/scripts/scene_context.py ccbd8ce6-c8e1-45b3-b6fa-f3868f11efe1
```
Expected: JSON 유효. 대상 대사 말투가 before 화자(대화 상대)와 정합. 교정한 다른 Guard 대사도 재조회로 확인.

- [ ] **Step 6: 규칙 기록 + 커밋**

`Trans-Complex2KR/decisions/localization_decisions.md`에 "Actor_Guard(케이) 화자별 존대/반말 규칙" 절 추가(Step 3 규칙 + 교정한 uid 목록 요약).
```bash
git add Trans-Complex2KR/translations/story_kr.json Trans-Complex2KR/decisions/localization_decisions.md
git commit -m "fix(Complex2KR): Actor_Guard(케이) 대화 상대별 말투 교정"
```

---

## 실행 참고

- Task 1·2는 순수 표준 라이브러리 + pytest로 자기완결적. 원본 데이터가 있어야 Step 6(빌드)·조회 검증 가능.
- Task 3은 번역 판단이 포함되므로 도구 산출물을 근거로 진행하고, `Actor_Guard` 정체 검증 결과에 따라 범위가 조정될 수 있다.
