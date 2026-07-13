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
