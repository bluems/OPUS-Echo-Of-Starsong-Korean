# tools/en2kr/apply.py
"""EN2KR 치환 적용. JSON은 값만, MD는 전체."""
import json, sys, glob
from tools.en2kr.substitute import build_rules, apply_text

def load_rules():
    mapping = json.load(open("tools/en2kr/substitution_map.json", encoding="utf-8"))
    mapping += json.load(open("tools/en2kr/places_map.json", encoding="utf-8"))
    return build_rules(mapping)

def walk(obj, rules):
    if isinstance(obj, str):
        return apply_text(obj, rules)
    if isinstance(obj, list):
        return [walk(x, rules) for x in obj]
    if isinstance(obj, dict):
        return {k: walk(v, rules) for k, v in obj.items()}  # 키 불변
    return obj

def convert_json(path, rules):
    data = json.load(open(path, encoding="utf-8"))
    out = walk(data, rules)
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def convert_md(path, rules):
    t = open(path, encoding="utf-8").read()
    open(path, "w", encoding="utf-8").write(apply_text(t, rules))

def main():
    rules = load_rules()
    for f in glob.glob("Trans-EN2KR/translations/*.json"):
        convert_json(f, rules); print("json:", f)
    for f in ["Trans-EN2KR/characters/character_profiles.md",
              "Trans-EN2KR/characters/character_personas.md"]:
        convert_md(f, rules); print("md:", f)

if __name__ == "__main__":
    main()
