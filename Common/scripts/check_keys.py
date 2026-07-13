#!/usr/bin/env python
"""
공통 키 매니페스트 검증 — 번역 변형(Trans-*) 간 키 드리프트 탐지.

모든 Trans-*/translations/*_kr.json 은 게임 소스에서 파생된 동일한 키(UUID) 집합을
공유한다(값=한국어 번역만 변형별로 다름). 이 스크립트는 각 변형의 키 집합·순서를
Common/translation_keys.json(공통 매니페스트)과 대조해 다음을 잡는다.

  - 누락 키(missing)   : 매니페스트에 있으나 변형 파일에 없음 → 주입 시 해당 항목 미번역
  - 초과 키(extra)     : 변형 파일에만 있는 키 → 오타/구버전 잔재
  - 순서 어긋남(order) : 키 집합은 같으나 순서가 다름(diff 노이즈 유발; 경고)
  - 파일 누락(file)    : 매니페스트에 있는 *_kr.json 자체가 없음

사용법:
  python Common/scripts/check_keys.py              # 모든 Trans-* 검증
  python Common/scripts/check_keys.py Complex2KR   # 특정 변형만
  python Common/scripts/check_keys.py --strict     # 순서 어긋남도 실패로 간주
  python Common/scripts/check_keys.py --update      # 현 변형 기준으로 매니페스트 재생성
  python Common/scripts/check_keys.py --update --from CHT2KR

종료코드: 0=일치, 1=드리프트(누락/초과/파일누락, --strict 시 순서도), 2=사용오류.
"""
import argparse
import glob
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "Common" / "translation_keys.json"


def norm_project(name: str) -> str:
    name = name.strip().rstrip("/\\")
    return name if name.startswith("Trans-") else f"Trans-{name}"


def load_manifest() -> dict:
    if not MANIFEST.exists():
        sys.exit(f"[fatal] 매니페스트 없음: {MANIFEST}\n        → --update 로 먼저 생성하세요.")
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return data["files"]


def discover_variants() -> list[Path]:
    return sorted(
        p for p in ROOT.glob("Trans-*")
        if p.is_dir() and (p / "translations").is_dir()
        and any((p / "translations").glob("*_kr.json"))
    )


def keys_of(path: Path) -> list[str]:
    return list(json.loads(path.read_text(encoding="utf-8")).keys())


def check_variant(proj: Path, manifest: dict, strict: bool) -> tuple[int, int]:
    """(hard_fail, soft_warn) 개수 반환."""
    trdir = proj / "translations"
    hard = soft = 0
    lines: list[str] = []
    for fname, expected in manifest.items():
        fpath = trdir / fname
        if not fpath.exists():
            lines.append(f"    [file]    {fname}: 파일 없음")
            hard += 1
            continue
        actual = keys_of(fpath)
        exp_set, act_set = set(expected), set(actual)
        missing = [k for k in expected if k not in act_set]
        extra = [k for k in actual if k not in exp_set]
        if missing:
            hard += len(missing)
            lines.append(f"    [missing] {fname}: {len(missing)}개 (예: {missing[0]})")
        if extra:
            hard += len(extra)
            lines.append(f"    [extra]   {fname}: {len(extra)}개 (예: {extra[0]})")
        if not missing and not extra and actual != expected:
            soft += 1
            lines.append(f"    [order]   {fname}: 키 집합 동일하나 순서 다름")
    status = "OK" if hard == 0 and (soft == 0 or not strict) else "FAIL"
    print(f"  {proj.name}: {status}")
    for ln in lines:
        print(ln)
    return hard, soft


def do_update(from_proj: Path) -> int:
    trdir = from_proj / "translations"
    files = sorted(glob.glob(str(trdir / "*_kr.json")))
    if not files:
        sys.exit(f"[fatal] {from_proj.name}/translations 에 *_kr.json 없음")
    manifest = {os.path.basename(p): keys_of(Path(p)) for p in files}
    out = {
        "_comment": (
            "번역 변형(Trans-*) 공통 키 매니페스트. 모든 변형의 translations/*_kr.json 은 "
            "이 키 집합·순서를 따라야 한다. 게임 소스에서 파생된 키이며, 갱신 시 "
            "Common/scripts/check_keys.py --update 로 재생성."
        ),
        "files": manifest,
    }
    MANIFEST.write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    total = sum(len(v) for v in manifest.values())
    print(f"[update] {MANIFEST.relative_to(ROOT)} 재생성 "
          f"(기준: {from_proj.name}, 파일 {len(manifest)}개, 키 {total}개)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="번역 변형 간 공통 키 매니페스트 검증.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("projects", nargs="*", help="검증할 변형(예: Complex2KR). 비우면 전체.")
    ap.add_argument("--strict", action="store_true", help="순서 어긋남도 실패로 간주")
    ap.add_argument("--update", action="store_true", help="매니페스트 재생성")
    ap.add_argument("--from", dest="from_proj", default=None,
                    help="--update 기준 변형(기본: 사용 가능한 첫 변형)")
    args = ap.parse_args(argv)

    available = discover_variants()
    if not available:
        print("검증할 Trans-* 변형이 없습니다.")
        return 2

    if args.update:
        src = ROOT / norm_project(args.from_proj) if args.from_proj else available[0]
        if not (src / "translations").is_dir():
            sys.exit(f"[fatal] {src.name}/translations 없음")
        return do_update(src)

    manifest = load_manifest()
    targets = ([ROOT / norm_project(n) for n in args.projects]
               if args.projects else available)

    print(f"공통 키 매니페스트 검증 ({len(manifest)}개 파일 / "
          f"{sum(len(v) for v in manifest.values())}개 키)")
    total_hard = total_soft = 0
    for proj in targets:
        if not (proj / "translations").is_dir():
            print(f"  {proj.name}: [error] translations/ 없음")
            total_hard += 1
            continue
        hard, soft = check_variant(proj, manifest, args.strict)
        total_hard += hard
        total_soft += soft

    print("-" * 50)
    if total_hard == 0 and total_soft == 0:
        print("모든 변형이 매니페스트와 일치합니다.")
        return 0
    print(f"드리프트: 하드 {total_hard}건, 순서경고 {total_soft}건")
    return 1 if total_hard > 0 or (args.strict and total_soft > 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
