"""치환 맵 → 규칙 → 단일패스 적용."""
import re
from tools.en2kr.josa import josa_variants

def build_rules(mapping):
    rules = {}
    for e in mapping:
        if e["type"] == "auto":
            old, new = e["old"], e["new"]
            for o, n in josa_variants(old, new):
                rules.setdefault(o, n)
            rules.setdefault(old, new)  # bare (최후)
        elif e["type"] == "literal":
            for o, n in e["pairs"]:
                rules.setdefault(o, n)
        else:
            raise ValueError(f"unknown type: {e['type']}")
    return rules

def apply_text(text, rules):
    if not rules:
        return text
    # 최장 표면형 우선 정렬 → 알터네이션 순서 보장
    keys = sorted(rules.keys(), key=len, reverse=True)
    pattern = re.compile("|".join(re.escape(k) for k in keys))
    return pattern.sub(lambda m: rules[m.group(0)], text)
