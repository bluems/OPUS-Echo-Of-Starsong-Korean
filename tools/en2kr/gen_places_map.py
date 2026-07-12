# tools/en2kr/gen_places_map.py
"""glossary 지명 KR → EN 개명 「」 리터럴 치환쌍 생성."""
import json, re

# 「」 내부 토큰 개명표 (구KR → EN). spec §2-4.
RENAME = {
    "조산": "마운트 오로라", "철람성": "아이언윈드",
    "주홍": "버밀리온", "다랑": "루시두스", "각신": "콘카",
    "지신": "사라스와티", "귀인": "포르투나", "해국": "오세아니아",
    "대황": "엑시디움", "촉룡": "이그니스", "후토": "테라", "을황": "헬리우스",
    "부생약몽": "드리머스 핏", "대분종": "그레이트 벤저민",
    "서뢰산": "웨스트 마운트 토니트루스", "보제": "파이제", "백제": "파이제",
    "어와": "에르바", "호사": "후샤", "촉룡 1호": "이그니스 1호",
    # spec §2-2 신명(神名) 표기 중, glossary places 카탈로그에 「」 지명/기물
    # 토큰으로도 등장하는 것들(태을=위성명, 흑룡=혜성명). crosslang places
    # type="음차/개명(EN name)"이며 spec §2-2에 KR 확정형이 명시되어 있어 포함.
    "태을": "타이양", "흑룡": "밴시",
    # glossary 원본의 표기 불일치 보정: 「燭龍二」만 "촉룡 2"로 "호" 접미사가
    # 빠져 있음(「燭龍一」은 "촉룡 1호"). 동일 계열이므로 별도 키로 커버.
    "촉룡 2": "이그니스 2",
}
# 철람N(광산 번호): 철람24→아이언윈드24
NUM_RENAME = ("철람", "아이언윈드")

def bracket_tokens(kr_place):
    return re.findall(r"「([^」]+)」", kr_place)

def convert_token(tok):
    if tok in RENAME:
        return RENAME[tok]
    m = re.fullmatch(NUM_RENAME[0] + r"(\d+)", tok)
    if m:
        return NUM_RENAME[1] + m.group(1)
    # 한자 병기 제거형: "조산(朝山)" → "마운트 오로라"
    base = re.sub(r"\([^)]*\)", "", tok)
    if base in RENAME:
        return RENAME[base]
    return None  # 변경 없음(이미 EN 음차/의역/병음)

def main():
    g = json.load(open("Trans-EN2KR/glossary/master_glossary.json", encoding="utf-8"))
    places = g.get("places") or []
    # master_glossary.json 구조 확인 후 지명 리스트 경로 조정 (아래 Step 2에서 검증)
    pairs = []
    seen = set()
    for p in places:
        kr = p["kr"] if isinstance(p, dict) else p
        for tok in bracket_tokens(kr):
            nt = convert_token(tok)
            if nt and f"「{tok}」" not in seen:
                pairs.append([f"「{tok}」", f"「{nt}」"])
                seen.add(f"「{tok}」")
    json.dump([{"type":"literal","pairs":pairs}],
              open("tools/en2kr/places_map.json","w",encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("places pairs:", len(pairs))

if __name__ == "__main__":
    main()
