#!/usr/bin/env python
"""
OPUS: Echo of Starsong — 한국어 폰트 TMP 생성 스크립트 (재사용용)
sharedassets2 안에 Noto Sans CJK KR 기반 TMP_FontAsset을 만들고
FontSettings SO에 KR(language=8) 매핑을 배선한다. 결과 = 주입 베이스(.fontready).

수행 내용:
  1) Font(원본 GlowSansJ, 기본 pid 2184) 클론 → m_FontData 를 Noto CJK KR OTF 로 교체
  2) SDF Atlas Texture(기본 pid 148) 클론
  3) TMP_FontAsset(기본 pid 75388) 클론 → m_SourceFontFile / m_AtlasTextures 를 위 신규 pid로 연결
  4) FontSettings(기본 pid 75398)의 각 매핑에 KR(language=8) 항목 추가(fallbackFonts→신규 TMP)

사용:
  python build_krfont.py <game_data_dir> [out.assets] [noto.otf]
  예: python build_krfont.py "…/OPUS Echo of Starsong/OPUS Echo of Starsong_Data" \
        ../../Trans-Complex2KR/build/sharedassets2.assets.fontready

  - game_data_dir : `OPUS Echo of Starsong_Data` 경로. 여기서 pristine sharedassets2.assets 를
                    읽고, TypeTree 는 game_data_dir 상위(게임 루트)에서 로드한다.
  - out.assets    : 결과 파일. 생략 시 game_data_dir/sharedassets2.assets 에 in-place 덮어씀.
  - noto.otf      : 한글 폰트 소스. 생략 시 Common/Assets/NotoSansCJKkr-Regular.otf.

주의(Common/game-file-structure.md §3, Common/injection-guide.md):
  - 반드시 pristine sharedassets2 에서 ONE PASS. 이미 저장한 파일 재로드-재저장 금지(손상).
  - 게임 업데이트로 pid 가 바뀔 수 있음 → 아래 SRC_* 상수는 이름 기준으로 재확인할 것.
  - 검증은 verify_krfont.py 로 (신규 폰트/아틀라스/TMP + FontSettings KR 매핑 확인).
"""
import UnityPy, os, sys, copy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

# 클론 원본 pid (게임 업데이트 시 이름으로 재확인 — inspect_fonts2 등)
SRC_FONT  = 2184    # Font: GlowSansJ-Normal-Regular
SRC_ATLAS = 148     # Texture2D: SDF Atlas
SRC_TMP   = 75388   # MonoBehaviour: TMP_FontAsset (템플릿)
SRC_FS    = 75398   # MonoBehaviour: River.FontSettings
KR_LANG   = 8       # EnumLanguage.KR

def main(data, out, noto_path):
    noto = open(noto_path, "rb").read()
    print("noto bytes", len(noto))
    gen = TypeTreeGenerator("2020.3.35f1"); gen.load_local_game(os.path.dirname(data))
    tmp = gen.get_nodes_up("Unity.TextMeshPro", "TMPro.TMP_FontAsset")
    fs  = gen.get_nodes_up("River", "River.FontSettings")

    src_path = os.path.join(data, "sharedassets2.assets")
    env = UnityPy.load(src_path)
    sf  = env.file
    objs = {o.path_id: o for o in env.objects}
    maxpid = max(objs)
    pidFont, pidAtlas, pidTmp = maxpid + 1, maxpid + 2, maxpid + 3
    print("new pids Font/Atlas/TMP =", pidFont, pidAtlas, pidTmp)

    def clone(src_pid, new_pid):
        src = objs[src_pid]
        n = copy.copy(src)
        n.path_id = new_pid
        n.set_raw_data(src.get_raw_data())
        sf.objects[new_pid] = n
        return n

    # 1) Font 클론 → Noto CJK KR 로 교체
    nf = clone(SRC_FONT, pidFont)
    d = nf.read(); d.m_FontData = noto; d.m_Name = "NotoSansCJKkr-Regular"; d.save()
    print("Korean Font created len", len(noto))

    # 2) SDF Atlas 텍스처 클론
    na = clone(SRC_ATLAS, pidAtlas)
    dt = na.read(); dt.m_Name = "NotoSansCJKkr-Regular SDF Atlas"; dt.save()
    print("atlas texture created")

    # 3) TMP 클론 → source/atlas 를 신규 pid 로 연결
    nt = clone(SRC_TMP, pidTmp)
    tt = nt.read_typetree(tmp)
    tt["m_Name"] = "NotoSansCJKkr-Regular SDF"
    tt["m_SourceFontFile"] = {"m_FileID": 0, "m_PathID": pidFont}
    tt["m_AtlasTextures"] = [{"m_FileID": 0, "m_PathID": pidAtlas}]
    nt.save_typetree(tt, tmp)
    print("Korean TMP created, source->", pidFont, "atlas->", pidAtlas)

    # 4) FontSettings: 각 매핑에 KR 매핑 추가(Default/Bold 등)
    fso = objs[SRC_FS]
    ft = fso.read_typetree(fs)
    for m in ft["_fontAssetMappings"]:
        lfs = m["languageFonts"]
        if any(x["language"] == KR_LANG for x in lfs):
            continue
        kr = copy.deepcopy(lfs[0])            # CHT 항목 복제(fontAsset=base 유지)
        kr["language"] = KR_LANG
        kr["fallbackFonts"] = [{"m_FileID": 0, "m_PathID": pidTmp}]
        lfs.append(kr)
    fso.save_typetree(ft, fs)
    print("FontSettings KR mappings added")

    raw = sf.save()
    open(out, "wb").write(raw)
    print(f"wrote {out} size {len(raw)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    data = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(data, "sharedassets2.assets")
    noto = sys.argv[3] if len(sys.argv) > 3 else \
        os.path.join(os.path.dirname(__file__), "..", "Assets", "NotoSansCJKkr-Regular.otf")
    main(data, out, noto)
