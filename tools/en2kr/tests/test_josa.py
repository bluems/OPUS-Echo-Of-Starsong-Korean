from tools.en2kr.josa import has_batchim, is_rieul, josa_variants

def test_batchim():
    assert has_batchim("루멘")      # 멘=ㄴ받침
    assert not has_batchim("밴시")  # 시=받침없음
    assert not has_batchim("이그니스")  # 스=받침없음(ㅡ)
    assert has_batchim("타이양")    # 양=ㅇ받침
    assert not has_batchim("")
    assert not has_batchim("Red")   # 비한글

def test_rieul():
    assert is_rieul("태을")         # 을=ㄹ
    assert not is_rieul("루멘")

def test_variants_cons_to_vowel():
    v = dict(josa_variants("흑룡", "밴시"))  # 받침→모음
    assert v["흑룡을"] == "밴시를"
    assert v["흑룡이"] == "밴시가"
    assert v["흑룡은"] == "밴시는"
    assert v["흑룡과"] == "밴시와"
    assert v["흑룡으로"] == "밴시로"
    assert v["흑룡이라는"] == "밴시라는"
    assert v["흑룡이었"] == "밴시였"

def test_variants_vowel_to_cons():
    v = dict(josa_variants("만도", "미리안"))  # 모음→받침
    assert v["만도는"] == "미리안은"
    assert v["만도가"] == "미리안이"
    assert v["만도를"] == "미리안을"
    assert v["만도와"] == "미리안과"
    assert v["만도로"] == "미리안으로"

def test_variants_rieul_dir():
    v = dict(josa_variants("태을", "타이양"))  # ㄹ받침(로)→ㅇ받침(으로)
    assert v["태을로"] == "타이양으로"
    assert v["태을은"] == "타이양은"

def test_variants_same_ending_identity():
    v = dict(josa_variants("용맥", "루멘"))  # 둘 다 받침
    assert v["용맥을"] == "루멘을"
    assert v["용맥으로"] == "루멘으로"
