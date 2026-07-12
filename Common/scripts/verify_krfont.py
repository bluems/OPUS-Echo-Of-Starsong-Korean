#!/usr/bin/env python
"""
OPUS: Echo of Starsong — 한국어 폰트 TMP 검증 스크립트
build_krfont.py 결과(.fontready 또는 최종 assets)에 신규 Noto CJK KR
Font/Atlas/TMP 와 FontSettings 의 KR 매핑이 제대로 들어갔는지 확인.

사용:
  python verify_krfont.py <game_data_dir> [target.assets]
  - game_data_dir : `OPUS Echo of Starsong_Data`(TypeTree 로드용).
  - target.assets : 검증 대상. 생략 시 game_data_dir/sharedassets2.assets.

pid 하드코딩 대신 이름으로 조회(게임 업데이트로 pid 가 바뀌어도 동작).
"""
import UnityPy, os, sys
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

KR_LANG = 8
FONT_NM, ATLAS_NM, TMP_NM = ("NotoSansCJKkr-Regular",
                             "NotoSansCJKkr-Regular SDF Atlas",
                             "NotoSansCJKkr-Regular SDF")

def main(data, target):
    gen = TypeTreeGenerator("2020.3.35f1"); gen.load_local_game(os.path.dirname(data))
    tmp = gen.get_nodes_up("Unity.TextMeshPro", "TMPro.TMP_FontAsset")
    fs  = gen.get_nodes_up("River", "River.FontSettings")
    env = UnityPy.load(target)
    objs = {o.path_id: o for o in env.objects}
    print("total objects:", len(objs))

    ok = True
    font = atlas = tmpo = None
    for o in env.objects:
        if o.type.name == "Font":
            d = o.read()
            if d.m_Name == FONT_NM: font = (o.path_id, d)
        elif o.type.name == "Texture2D":
            d = o.read()
            if d.m_Name == ATLAS_NM: atlas = (o.path_id, d)
        elif o.type.name == "MonoBehaviour":
            try: t = o.read_typetree(tmp)
            except Exception: continue
            if t.get("m_Name") == TMP_NM: tmpo = (o.path_id, t)

    if font:
        pid, d = font
        print(f"Font {pid}: {d.m_Name} len {len(d.m_FontData)} magic {bytes(d.m_FontData[:4])}")
    else:
        print("Font MISSING"); ok = False
    if atlas:
        pid, d = atlas
        print(f"Atlas {pid}: {d.m_Name} {d.m_Width}x{d.m_Height} fmt {d.m_TextureFormat}")
    else:
        print("Atlas MISSING"); ok = False
    if tmpo:
        pid, t = tmpo
        print(f"TMP {pid}: {t['m_Name']} APM {t['m_AtlasPopulationMode']} "
              f"src {t['m_SourceFontFile']} atlas {t['m_AtlasTextures']}")
        if font and t["m_SourceFontFile"]["m_PathID"] != font[0]:
            print("  ! TMP source 가 신규 Font 를 가리키지 않음"); ok = False
    else:
        print("TMP MISSING"); ok = False

    # FontSettings KR 매핑
    fso = next((o for o in env.objects
                if o.type.name == "MonoBehaviour" and _is_fontsettings(o, fs)), None)
    if fso:
        ft = fso.read_typetree(fs)
        for m in ft["_fontAssetMappings"]:
            krs = [x for x in m["languageFonts"] if x["language"] == KR_LANG]
            print(f"mapping {m['name']} KR entry:", krs[0] if krs else "MISSING")
            if not krs: ok = False
    else:
        print("FontSettings MISSING"); ok = False

    print("RESULT:", "OK" if ok else "FAIL")
    sys.exit(0 if ok else 1)

def _is_fontsettings(o, fs):
    try:
        return "_fontAssetMappings" in o.read_typetree(fs)
    except Exception:
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    data = sys.argv[1]
    target = sys.argv[2] if len(sys.argv) > 2 else os.path.join(data, "sharedassets2.assets")
    main(data, target)
