import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.content_safety_service import scan_public_content


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    seed_data_dir = Path(__file__).resolve().parents[1] / "app" / "seed_data"
    parser = argparse.ArgumentParser(description="Scan public content for sensitive values.")
    parser.add_argument("root", nargs="?", type=Path, default=seed_data_dir)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        findings = scan_public_content(args.root)
    except (FileNotFoundError, NotADirectoryError) as error:
        print(f"Public content safety scan failed: {error}", file=sys.stderr)
        return 2

    if findings:
        for finding in findings:
            print(
                f"{finding.path}:{finding.line_number}: "
                f"[{finding.rule_name}] {finding.excerpt}"
            )
        return 1

    print("Public content safety scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
