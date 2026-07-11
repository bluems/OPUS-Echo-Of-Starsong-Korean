# 한국어 텍스트 주입 가이드 (sharedassets2.assets)

> 언어 무관. UnityPy로 TextAsset에 `_KR` 필드를 넣는 방법 + 함정.

## 환경
- Python + **UnityPy 1.25.2** (`pip install UnityPy`). Windows에서 `python`(Store 스텁 `python3` 아님).
- MonoBehaviour(폰트/언어 SO) 편집 시 typetree 필요: `TypeTreeGeneratorAPI`(pip) + `UnityPy.helpers.TypeTreeGenerator("2020.3.35f1").load_local_game(gameRoot)` → `.get_nodes_up(assembly, fullname)` → `o.read_typetree(nodes)`/`o.save_typetree(tree, nodes)`. (릴리스 빌드라 MB에 typetree 미포함.)
- TextAsset은 **built-in 타입이라 typetree 불필요** — `o.read()` 후 `d.m_Script` 문자열 교체.

## 주입 절차 (검증된 방법)

```python
import UnityPy, json, os
env = UnityPy.load("sharedassets2.assets.fontready")   # 폰트+KR언어 베이스에서 시작
for o in env.objects:
    if o.type.name != "TextAsset": continue
    d = o.read()
    txt = d.m_Script if isinstance(d.m_Script, str) else bytes(d.m_Script).decode("utf-8","surrogateescape")
    if not txt.strip().startswith("["): continue
    arr = json.loads(txt)
    for e in arr:
        f = e["fields"]
        # 일반 시트: 각 prefix(_CHT 존재)마다 _KR 추가, 없으면 _EN 폴백
        for p in set(k.rsplit("_",1)[0] for k in list(f) if k.endswith("_CHT")):
            f[f"{p}_KR"] = my_kr.get(key_for(e,p), f.get(f"{p}_EN",""))
        # StringData: f["KR"] = ...   /  Story: f["Text_KR"]=..., f["Speech_KR"]=""
    d.m_Script = json.dumps(arr, ensure_ascii=False, indent=2)
    d.save()
with open("sharedassets2.assets","wb") as fh:
    fh.write(env.file.save())
```

## ★★ 치명적 함정 (반드시 지킬 것)

1. **주입은 반드시 `.fontready`(또는 pristine)에서 ONE PASS로.**
   이미 저장한 `sharedassets2.assets`를 **다시 로드해서 `env.file.save()`를 또 호출하면 파일이 ~2.5MB로 손상**된다(UnityPy 재저장 버그). 추가 수정이 필요하면 처음부터 전체를 한 번에 다시 주입할 것. (실제로 이 버그로 한 번 파일이 깨졌고 백업으로 복구함.)

2. **HTML 이스케이프 금지.** 번역 에이전트/LLM이 `<`/`>`를 `&lt;`/`&gt;`로 바꾸는 일이 잦다 → TMP rich-text 태그(`<p>`, `<color=..>`)와 `<email>`, `<3` 하트가 깨진다. 주입 전 반드시 un-escape: `&lt;→<`, `&gt;→>`, `&amp;→&` 후 태그 개수 대조.

3. **태그·플레이스홀더 원형 보존**: `<p>`, `#ACTION#`/`#ITEM#`/`#LOC#`/`#AVATAR:..#`, `#NONAME#`, 선행 `#`(선택지 마커), `<color=..></color>`, `@..@`, `{0}` `{1}`, `[Puzzle_x/y]` 류, `\n`. 원문 CHT의 개수와 KR 개수 대조로 검증.

4. **이메일 주소는 번역 안 함**: SheetMail의 `<user@domain>` → `_KR = _EN`(그대로).

5. **미번역 폴백은 `_EN`**: 번역 누락 필드는 EN으로 채워 공란(□)/blank 방지. 개발 노트("遊戲不顯示", "未使用Flag" 등, EN="-")는 그대로 두면 됨(인게임 미표시).

## 검증 (주입 후 필수)
- `env` 재로드 → 객체수 동일한지(94892 근처).
- 각 TextAsset의 `_KR` 채움 수 = 원본 필드 수(빈 필드 제외).
- **story 4728건 등 원본 kr.json과 1:1 대조 → 불일치 0** 확인(잘림 방지).
- 파일 크기 ~106MB(정상), 2.5MB면 손상.
- `한국어`(utf-8) 문자열 존재(LanguageSettings), `Noto` 폰트 마커 존재.

## 최종 인게임 검증
게임 실행 → 설정 → 한국어 선택 → 메뉴/대사 한글 렌더 + □(두부) 없음 확인. (자동화 불가, 수동.)
