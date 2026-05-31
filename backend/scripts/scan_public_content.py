import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.content_safety_service import scan_public_content


def main() -> int:
    seed_data_dir = Path(__file__).resolve().parents[1] / "app" / "seed_data"
    findings = scan_public_content(seed_data_dir)

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
