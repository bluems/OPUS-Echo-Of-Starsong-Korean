"""치환 맵 → 규칙 → 단일패스 적용. left-boundary(앞 한글 금지) 지원."""
import re
from tools.en2kr.josa import josa_variants

def build_rules(mapping):
    """returns list of (surface, replacement, left_boundary_bool).
    엔트리에 "boundary":"left" 있으면 그 엔트리의 모든 표면형은 앞 글자가 한글이면 미매치."""
    rules = []
    seen = set()
    def add(surface, repl, lb):
        if surface in seen:
            return
        seen.add(surface)
        rules.append((surface, repl, lb))
    for e in mapping:
        lb = e.get("boundary") == "left"
        if e["type"] == "auto":
            old, new = e["old"], e["new"]
            for o, n in josa_variants(old, new):
                add(o, n, lb)
            add(old, new, lb)  # bare (최후)
        elif e["type"] == "literal":
            for o, n in e["pairs"]:
                add(o, n, lb)
        else:
            raise ValueError(f"unknown type: {e['type']}")
    return rules

def apply_text(text, rules):
    if not rules:
        return text
    ordered = sorted(rules, key=lambda r: len(r[0]), reverse=True)  # 최장 우선
    repl = {s: r for s, r, _ in ordered}
    frags = [("(?<![가-힣])" if lb else "") + re.escape(s) for s, r, lb in ordered]
    pattern = re.compile("|".join(frags))
    return pattern.sub(lambda m: repl[m.group(0)], text)
