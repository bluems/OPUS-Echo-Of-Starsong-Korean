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
        cur = start; seen = {start}
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
    with open(GRAPH_PATH, encoding="utf-8") as f:
        graph = json.load(f)
    with open(os.path.join(
            REPO, f"Trans-{args.variant}", "translations", "story_kr.json"), encoding="utf-8") as f:
        story = json.load(f)
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
