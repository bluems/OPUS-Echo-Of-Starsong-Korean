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
