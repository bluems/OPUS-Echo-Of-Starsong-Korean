"""한국어 조사(josa) 종성 인식 교정. 고유명 치환 시 앞말 종성 변화 반영."""

_HANGUL_BASE = 0xAC00
_HANGUL_LAST = 0xD7A3

def _last_hangul(word):
    for ch in reversed(word):
        if _HANGUL_BASE <= ord(ch) <= _HANGUL_LAST:
            return ch
    return None

def has_batchim(word):
    ch = _last_hangul(word)
    if ch is None:
        return False
    return (ord(ch) - _HANGUL_BASE) % 28 != 0

def is_rieul(word):
    ch = _last_hangul(word)
    if ch is None:
        return False
    return (ord(ch) - _HANGUL_BASE) % 28 == 8  # ㄹ

def _dir_form(word):
    # 받침 없음 또는 ㄹ받침 → '로', 그 외 → '으로'
    return "로" if (not has_batchim(word) or is_rieul(word)) else "으로"

# 추상 조사 → (받침형, 모음형). DIR은 특수 처리.
_PAIRS = [
    ("이라는", "라는"), ("이라고", "라고"), ("이란", "란"),
    ("이었", "였"), ("이에요", "예요"), ("이야", "야"), ("이다", "다"),
    ("이나", "나"), ("이며", "며"), ("이자", "자"),
    ("은", "는"), ("이", "가"), ("을", "를"), ("과", "와"),
]

def josa_variants(old, new):
    old_b, new_b = has_batchim(old), has_batchim(new)
    out = []
    for bat, vow in _PAIRS:
        o = bat if old_b else vow
        n = bat if new_b else vow
        out.append((old + o, new + n))
    # 방향격 으로/로 (ㄹ 특수)
    out.append((old + _dir_form(old), new + _dir_form(new)))
    # 최장 조사부터
    out.sort(key=lambda p: len(p[0]), reverse=True)
    return out
