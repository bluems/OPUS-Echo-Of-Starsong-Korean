#!/usr/bin/env python
"""
OPUS: Echo of Starsong — 패치 에셋 빌드 자동화 (repo 루트)

각 Trans-* 프로젝트의 translations/ 를 sharedassets2 에 주입해
해당 프로젝트의 build/sharedassets2.assets 를 생성한다.
주입 로직은 Common/scripts/inject_kr.py 를 재사용한다.

에셋 배치(README·Common/game-file-structure 참조):
  Origin/sharedassets0.assets.origin  — 중국어/영어 참고용 원본 (빌드에 미사용, 대조 전용)
  Origin/sharedassets2.assets.origin  — 수정 대상 원본(2번 에셋)의 pristine 백업
  Trans-<X>/build/sharedassets2.assets.fontready
                                      — 2번 원본 + KR 폰트(Noto CJK)/언어 항목이 적용된 '주입 베이스'.
                                        재생성이 어려워 보존(§decisions 4). 실제 빌드는 이걸 베이스로 함.
  Trans-<X>/build/sharedassets2.assets — 최종 산출물(베이스 + KR 번역 주입). 게임 폴더에 덮어써 적용.

사용법:
  python build_assets.py Complex2KR              # 특정 프로젝트 빌드
  python build_assets.py Trans-Complex2KR        # 풀 폴더명도 허용
  python build_assets.py Complex2KR CHT2KR       # 여러 개
  python build_assets.py --all                   # translations 가 있는 모든 Trans-* 빌드
  python build_assets.py Complex2KR --base <path> # 베이스 .fontready 직접 지정
  python build_assets.py --list                  # 빌드 가능한 프로젝트 나열

베이스 해석 순서:
  1) --base 로 지정한 경로
  2) <프로젝트>/build/sharedassets2.assets.fontready (프로젝트 전용)
  3) 없으면 다른 Trans-*/build 의 .fontready 를 공유 KR 폰트베이스로 재사용(경고 출력)
     — 모든 *2KR 은 동일한 KR 폰트 베이스를 쓰므로 안전.

주의(inject_kr): 베이스는 반드시 pristine/.fontready 여야 하며, 이미 저장한
산출물(.assets)을 다시 베이스로 쓰면 손상된다. 이 스크립트는 산출물을 베이스로
지정하면 거부한다.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INJECT_DIR = ROOT / "Common" / "scripts"
ORIGIN_DIR = ROOT / "Origin"
FONTREADY_NAME = "sharedassets2.assets.fontready"
OUT_NAME = "sharedassets2.assets"

sys.path.insert(0, str(INJECT_DIR))
try:
    import inject_kr  # Common/scripts/inject_kr.py
except ImportError as e:  # pragma: no cover
    sys.exit(f"[fatal] inject_kr.py 를 불러올 수 없음 ({INJECT_DIR}): {e}")
try:
    import check_keys  # Common/scripts/check_keys.py — 공통 키 매니페스트 검증
except ImportError as e:  # pragma: no cover
    sys.exit(f"[fatal] check_keys.py 를 불러올 수 없음 ({INJECT_DIR}): {e}")


def norm_project(name: str) -> str:
    """'Complex2KR' 또는 'Trans-Complex2KR' 모두 허용."""
    name = name.strip().rstrip("/\\")
    return name if name.startswith("Trans-") else f"Trans-{name}"


def has_translations(proj: Path) -> bool:
    trdir = proj / "translations"
    return trdir.is_dir() and any(trdir.glob("*_kr.json"))


def discover() -> list[Path]:
    """translations 가 있는 모든 Trans-* 프로젝트."""
    return sorted(p for p in ROOT.glob("Trans-*") if p.is_dir() and has_translations(p))


def find_base(proj: Path, override: str | None) -> tuple[Path | None, bool]:
    """(base_path, is_shared) 반환. 없으면 (None, False)."""
    if override:
        return Path(override).expanduser().resolve(), False
    own = proj / "build" / FONTREADY_NAME
    if own.exists():
        return own, False
    # 공유 폰트베이스 폴백: 다른 프로젝트의 .fontready
    for sib in sorted(ROOT.glob(f"Trans-*/build/{FONTREADY_NAME}")):
        return sib, True
    return None, False


def check_keys_for(targets: list[Path], strict: bool) -> bool:
    """빌드 전 공통 키 매니페스트 검증. 통과 시 True."""
    manifest = check_keys.load_manifest()
    total_hard = total_soft = 0
    print("[check] 공통 키 매니페스트 검증")
    for proj in targets:
        if not (proj / "translations").is_dir():
            continue
        hard, soft = check_keys.check_variant(proj, manifest, strict)
        total_hard += hard
        total_soft += soft
    if total_hard == 0 and (total_soft == 0 or not strict):
        return True
    print(f"        → 키 드리프트 감지(하드 {total_hard}, 순서 {total_soft}). "
          f"수정하거나 --no-check 로 건너뛰세요.")
    return False


def build_one(proj: Path, override: str | None) -> bool:
    if not has_translations(proj):
        print(f"[skip]  {proj.name}: translations/*_kr.json 없음")
        return False

    base, shared = find_base(proj, override)
    if base is None or not base.exists():
        print(f"[error] {proj.name}: 베이스 .fontready 를 찾을 수 없음.\n"
              f"        → --base <경로> 로 지정하거나 {proj.name}/build/{FONTREADY_NAME} 를 준비하세요.")
        return False

    build_dir = proj / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    out = build_dir / OUT_NAME

    if base.resolve() == out.resolve():
        print(f"[error] {proj.name}: 베이스가 산출물({OUT_NAME})을 가리킴 — 손상 위험으로 거부. "
              f".fontready 를 베이스로 쓰세요.")
        return False

    tag = "  (공유 KR 폰트베이스)" if shared else ""
    try:
        rel_base = base.relative_to(ROOT)
    except ValueError:
        rel_base = base
    print(f"[build] {proj.name}")
    print(f"        base : {rel_base}{tag}")
    print(f"        trans: {(proj / 'translations').relative_to(ROOT)}")
    print(f"        out  : {out.relative_to(ROOT)}")
    inject_kr.main(str(base), str(proj / "translations"), str(out))
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Trans-* 프로젝트별 sharedassets2.assets 빌드 (KR 번역 주입).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("projects", nargs="*", help="빌드할 프로젝트 (예: Complex2KR). 비우면 --all 또는 --list 필요.")
    ap.add_argument("--all", action="store_true", help="translations 가 있는 모든 Trans-* 빌드")
    ap.add_argument("--list", action="store_true", help="빌드 가능한 프로젝트 목록만 출력")
    ap.add_argument("--base", default=None, help="베이스 .fontready 경로 직접 지정(단일 프로젝트 빌드용)")
    ap.add_argument("--no-check", action="store_true", help="빌드 전 공통 키 매니페스트 검증 건너뛰기")
    ap.add_argument("--strict", action="store_true", help="키 순서 어긋남도 검증 실패로 간주")
    args = ap.parse_args(argv)

    available = discover()
    if args.list:
        print("빌드 가능한 프로젝트:")
        for p in available:
            own = (p / "build" / FONTREADY_NAME).exists()
            print(f"  - {p.name}  (전용 폰트베이스: {'있음' if own else '없음 → 공유 폴백'})")
        if not available:
            print("  (없음)")
        return 0

    if args.all:
        targets = available
    elif args.projects:
        if args.base and len(args.projects) != 1:
            ap.error("--base 는 단일 프로젝트 빌드에만 사용할 수 있습니다.")
        targets = [ROOT / norm_project(n) for n in args.projects]
    else:
        ap.error("프로젝트를 지정하거나 --all / --list 를 사용하세요.")

    if not targets:
        print("빌드 대상이 없습니다. (translations/*_kr.json 를 갖춘 Trans-* 필요)")
        return 1

    if not args.no_check:
        existing = [p for p in targets if p.exists()]
        if existing and not check_keys_for(existing, args.strict):
            print("빌드 중단. (--no-check 로 무시 가능)")
            return 1

    ok = 0
    for proj in targets:
        if not proj.exists():
            print(f"[error] {proj.name}: 폴더 없음 ({proj})")
            continue
        print("-" * 60)
        if build_one(proj, args.base):
            ok += 1
    print("-" * 60)
    print(f"완료: {ok}/{len(targets)} 성공")
    return 0 if ok == len(targets) else 1


if __name__ == "__main__":
    raise SystemExit(main())
