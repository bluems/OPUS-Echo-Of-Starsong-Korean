#!/usr/bin/env python
"""
OPUS: Echo of Starsong — 한국어 주입 스크립트 (재사용용)
translations/*.json 을 sharedassets2 의 TextAsset _KR 필드로 주입.

사용:
  python inject_kr.py <base.assets> <translations_dir> <out.assets>
  예: python inject_kr.py sharedassets2.assets.fontready ../Trans-Complex2KR/translations sharedassets2.assets

주의(Common/injection-guide.md):
  - base 는 폰트+KR언어가 적용된 .fontready(또는 pristine + 별도 폰트/언어 처리).
  - 반드시 pristine/fontready 에서 ONE PASS. 이미 저장한 파일 재로드-재저장 금지(손상).
"""
import UnityPy, json, os, sys, re

def load(d, name):
    p = os.path.join(d, name)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}

def main(base, trdir, out):
    kr = {k: load(trdir, f"{k}_kr.json") for k in
          ["loc","items","recipe","store","secret","subloc","incident"]}
    ui   = load(trdir, "ui_kr.json")      # locKey -> KR (UI + Actor_* labels)
    story= load(trdir, "story_kr.json")   # uid -> KR
    mail = load(trdir, "mail_kr.json")    # id(str) -> {title,sender,receiver,job,content}
    tblmap = {"SheetLocLocalization":"loc","SheetItemsLocalization":"items",
        "SheetRecipeLocalization":"recipe","SheetStoreLocalization":"store",
        "SheetSecretLocLocalization":"secret","SheetSubLocLocalization":"subloc",
        "SheetIncidentLocalization":"incident"}
    env = UnityPy.load(base)
    report = {}
    for o in env.objects:
        if o.type.name != "TextAsset": continue
        d = o.read(); nm = d.m_Name
        txt = d.m_Script if isinstance(d.m_Script,str) else bytes(d.m_Script).decode("utf-8","surrogateescape")
        if not txt.strip().startswith("["): continue
        arr = json.loads(txt)
        if nm in tblmap:
            src = kr[tblmap[nm]]
            for e in arr:
                f = e["fields"]
                for p in set(k.rsplit("_",1)[0] for k in list(f) if k.endswith("_CHT")):
                    v = src.get(f'{e["id"]}:{p}')
                    f[f"{p}_KR"] = v if v is not None else f.get(f"{p}_EN","")
        elif nm == "StringDataLocalization":
            for e in arr:
                v = ui.get(e["locKey"]); e["fields"]["KR"] = v if v is not None else e["fields"].get("EN","")
        elif nm == "StoryLocalization":
            for e in arr:
                v = story.get(e["uid"]); e["fields"]["Text_KR"] = v if v is not None else e["fields"].get("Text_EN","")
                e["fields"]["Speech_KR"] = ""
        elif nm == "SheetMailLocalization":
            for e in arr:
                m = mail.get(str(e["id"]), {}); f = e["fields"]
                f["Title_KR"]=m.get("title",f.get("Title_EN",""));       f["SenderName_KR"]=m.get("sender",f.get("SenderName_EN",""))
                f["ReceiverName_KR"]=m.get("receiver",f.get("ReceiverName_EN","")); f["Content_KR"]=m.get("content",f.get("Content_EN",""))
                f["SenderJob_KR"]=m.get("job",f.get("SenderJob_EN",""))
                f["SenderEmail_KR"]=f.get("SenderEmail_EN",""); f["ReceiverEmail_KR"]=f.get("ReceiverEmail_EN","")
        else:
            continue
        # 안전: HTML 이스케이프 복원
        def unesc(x): return x.replace("&lt;","<").replace("&gt;",">").replace("&amp;","&") if isinstance(x,str) else x
        for e in arr:
            for k2,v2 in list(e.get("fields",{}).items()):
                if k2.endswith("_KR") or k2=="KR": e["fields"][k2]=unesc(v2)
        d.m_Script = json.dumps(arr, ensure_ascii=False, indent=2); d.save()
        report[nm] = len(arr)
    with open(out, "wb") as fh:
        fh.write(env.file.save())
    print("주입 테이블:", report)
    sz = os.path.getsize(out)
    print(f"저장 {out}: {sz} bytes ({sz/1e6:.1f}MB) — {'OK' if sz>100_000_000 else 'CORRUPT?!'}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__); sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
