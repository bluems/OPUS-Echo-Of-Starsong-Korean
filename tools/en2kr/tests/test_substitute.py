from tools.en2kr.substitute import build_rules, apply_text

MAP = [
    {"type":"auto","old":"용맥","new":"루멘"},
    {"type":"auto","old":"흑룡","new":"밴시"},
    {"type":"auto","old":"만도","new":"미리안"},
    {"type":"literal","pairs":[["「곤」","「쿤」"]]},
]

def R():
    return build_rules(MAP)

def test_bare_and_josa():
    r = R()
    assert apply_text("용맥을 따라", r) == "루멘을 따라"
    assert apply_text("흑룡을 쫓는다", r) == "밴시를 쫓는다"
    assert apply_text("흑룡이 나타났다", r) == "밴시가 나타났다"
    assert apply_text("만도는 거대하다", r) == "미리안은 거대하다"

def test_no_cascade():
    # 용맥→루멘 후, '루멘'을 다시 건드리는 규칙 없음
    assert apply_text("용맥", R()) == "루멘"

def test_literal_only_exact():
    r = R()
    assert apply_text("태공선 「곤」에", r) == "태공선 「쿤」에"
    # 리터럴은 bare '곤' 미치환 (곤란 보호)
    assert apply_text("곤란한 상황", r) == "곤란한 상황"

def test_longest_match_first():
    r = R()
    # '흑룡이라는'이 '흑룡이'보다 먼저 매치
    assert apply_text("흑룡이라는 혜성", r) == "밴시라는 혜성"

def test_preserve_tags():
    r = R()
    s = "<color=#fff>용맥</color> {0} 「흑룡」"
    assert apply_text(s, r) == "<color=#fff>루멘</color> {0} 「밴시」"

def test_left_boundary_particle():
    m = [{"type":"auto","old":"만도","new":"미리안","boundary":"left"}]
    r = build_rules(m)
    assert apply_text("만도 촉룡 상회", r) == "미리안 촉룡 상회"
    assert apply_text("만도의 비밀", r) == "미리안의 비밀"
    assert apply_text("만도는 무상", r) == "미리안은 무상"
    # 조사(앞글자 한글) → 미치환
    assert apply_text("것만도 어딘데", r) == "것만도 어딘데"
    assert apply_text("짐승만도 못한", r) == "짐승만도 못한"

def test_no_boundary_still_replaces_after_hangul():
    m = [{"type":"auto","old":"용맥","new":"루멘"}]  # boundary 없음
    r = build_rules(m)
    # boundary 미지정이면 앞이 한글이어도 치환(기존 동작 유지)
    assert apply_text("대용맥", r) == "대루멘"
