import subprocess
import sys
from pathlib import Path

import pytest

from app.services.content_safety_service import scan_public_content, scan_text


def rule_names(text: str) -> set[str]:
    return {finding.rule_name for finding in scan_text(text, source_path="sample.md")}


def test_plain_login_password_is_reported() -> None:
    findings = scan_text(
        "./lnd login -u X101SC250910114-Z01-J003 -p ggeah41n",
        source_path="pipelines.py",
    )

    assert [finding.rule_name for finding in findings] == ["login-password"]


def test_login_placeholders_are_not_reported() -> None:
    findings = scan_text(
        "./lnd login -u <YOUR_USERNAME> -p <YOUR_PASSWORD>",
        source_path="pipelines.py",
    )

    assert findings == []


@pytest.mark.parametrize(
    ("text", "expected_rule"),
    [
        ('api_token = "live-token-value-123456"', "token"),
        ("Contact maintainer@example.edu before publishing.", "email"),
        (r'workdir = "C:\Users\alice\private-project"', "windows-absolute-path"),
    ],
)
def test_supported_sensitive_value_rules_are_reported(
    text: str,
    expected_rule: str,
) -> None:
    assert expected_rule in rule_names(text)


@pytest.mark.parametrize(
    "text",
    [
        "meta <- seurat_obj@meta.data",
        "Contact tutorial@example.com for this example.",
        "Contact tutorial@example.org for this example.",
        "Contact tutorial@example.net for this example.",
    ],
)
def test_email_rule_ignores_r_slot_syntax_and_example_domains(text: str) -> None:
    assert "email" not in rule_names(text)


@pytest.mark.parametrize(
    "text",
    [
        "oss://CP2023071800097/private/01.RawData",
        "/public/home/yhpeng/cut_tag/results",
        "/home/alice/private-project/results",
        "/Users/alice/private-project/results",
    ],
)
def test_private_locators_are_reported(text: str) -> None:
    assert "private-locator" in rule_names(text)


@pytest.mark.parametrize(
    "text",
    [
        "<YOUR_OSS_RAW_DATA_URI>",
        "<YOUR_PROJECT_DIR>",
        "${OSS_RAW_DATA_URI}",
        "${PROJECT_DIR}",
    ],
)
def test_private_locator_placeholders_are_not_reported(text: str) -> None:
    assert "private-locator" not in rule_names(text)


def test_scan_public_content_reads_supported_extensions_only(tmp_path: Path) -> None:
    for suffix in [".py", ".json", ".md", ".ts", ".tsx"]:
        (tmp_path / f"unsafe{suffix}").write_text(
            'api_token = "live-token-value-123456"',
            encoding="utf-8",
        )
    (tmp_path / "ignored.txt").write_text(
        'api_token = "live-token-value-123456"',
        encoding="utf-8",
    )

    findings = scan_public_content(tmp_path)

    assert {finding.path.suffix for finding in findings} == {
        ".py",
        ".json",
        ".md",
        ".ts",
        ".tsx",
    }


def test_scan_public_content_tolerates_non_utf8_bytes(tmp_path: Path) -> None:
    source_path = tmp_path / "unsafe.md"
    source_path.write_bytes(
        b"\xff\n./lnd login -u private-user -p private-password\n"
    )

    findings = scan_public_content(tmp_path)

    assert [finding.rule_name for finding in findings] == ["login-password"]


def test_scan_script_runs_from_backend_root() -> None:
    backend_dir = Path(__file__).resolve().parents[1]

    completed = subprocess.run(
        [sys.executable, "scripts/scan_public_content.py"],
        cwd=backend_dir,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "Public content safety scan passed."
