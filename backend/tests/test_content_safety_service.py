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
    "password",
    ['"secret123"', "'secret123'"],
)
def test_quoted_login_passwords_are_reported(password: str) -> None:
    assert "login-password" in rule_names(f"./lnd login -u private-user -p {password}")


def test_password_assignment_is_reported() -> None:
    assert "login-password" in rule_names('password = "secret123"')


def test_login_real_username_is_reported_when_password_is_placeholder() -> None:
    assert "login-password" in rule_names(
        "./lnd login -u private-user -p <YOUR_PASSWORD>"
    )


@pytest.mark.parametrize(
    "text",
    [
        "./lnd login --username private-user --password secret123",
        './lnd login --username="private-user" --password="secret123"',
        "./lnd login -u='private-user' -p='secret123'",
    ],
)
def test_login_option_variants_with_real_values_are_reported(text: str) -> None:
    assert "login-password" in rule_names(text)


@pytest.mark.parametrize(
    "text",
    [
        "./lnd login --username <YOUR_USERNAME> --password <YOUR_PASSWORD>",
        './lnd login --username="${USERNAME}" --password="${PASSWORD}"',
        "./lnd login -u='<YOUR_USERNAME>' -p='${PASSWORD}'",
    ],
)
def test_login_option_variants_with_placeholders_are_not_reported(text: str) -> None:
    assert "login-password" not in rule_names(text)


@pytest.mark.parametrize(
    "text",
    [
        "./lnd login --username private-user --password <YOUR_PASSWORD>",
        './lnd login --username="private-user" --password="${PASSWORD}"',
        "./lnd login -u='private-user' -p='<YOUR_PASSWORD>'",
    ],
)
def test_login_option_variants_report_real_username_with_placeholder_password(
    text: str,
) -> None:
    assert "login-password" in rule_names(text)


@pytest.mark.parametrize(
    ("text", "expected_rule"),
    [
        ('api_token = "live-token-value-123456"', "token"),
        ("token = realtoken123", "token"),
        ("TOKEN: realtoken123", "token"),
        ('api_key = "real-api-key-123456"', "token"),
        ('secret = "real-secret-123456"', "token"),
        ("Authorization: Bearer realtoken123", "token"),
        ('{"Authorization": "Bearer realtoken123"}', "token"),
        ("bearer = realtoken123", "token"),
        ("Contact maintainer@example.edu before publishing.", "email"),
        ("Contact maintainer@meta.data before publishing.", "email"),
        (r'workdir = "C:\Users\alice\private-project"', "windows-absolute-path"),
        ('workdir = "D:/private/project"', "windows-absolute-path"),
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
        "token = <YOUR_TOKEN>",
        "TOKEN: ${API_TOKEN}",
        "api_key = <YOUR_TOKEN>",
        "secret = ${TOKEN}",
        "Authorization: Bearer <YOUR_TOKEN>",
        '{"Authorization": "Bearer ${API_TOKEN}"}',
        "bearer = <YOUR_TOKEN>",
        "The tutorial explains how a token is used for authentication.",
    ],
)
def test_token_rule_ignores_placeholders_and_tutorial_prose(text: str) -> None:
    assert "token" not in rule_names(text)


@pytest.mark.parametrize(
    "text",
    [
        "oss://CP2023071800097/private/01.RawData",
        "/public/home/yhpeng/cut_tag/results",
        "/home/alice/private-project/results",
        "/Users/alice/private-project/results",
        "http://10.23.45.67:8080/private/api",
        "192.168.10.42",
        "172.16.1.5",
        "https://compute.cluster.internal/jobs",
        "cache.service.local",
        "/scratch/alice/private-project/results",
        "/data/alice/private-project/results",
        "/gpfs/users/alice/private-project/results",
        "/home/alice",
        "/scratch/alice",
        "/data/alice",
        "/gpfs/users/alice",
        "/gpfs/project/alice/private-project",
        "http://compute01:8080/private/api",
        "hdfs://compute01/user/alice/private-project",
        "hdfs://namenode.example.com/user/alice/private-project",
        "s3://real-bucket/tutorial/input.fastq.gz",
        "gs://real-bucket/tutorial/input.fastq.gz",
        "cos://real-bucket/tutorial/input.fastq.gz",
        "obs://real-bucket/tutorial/input.fastq.gz",
        "abfs://real-container/tutorial/input.fastq.gz",
        "abfss://real-container@storage-account.dfs.core.windows.net/tutorial/input.fastq.gz",
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
        "/scratch/${USER}/private-project",
        "/data/<YOUR_USERNAME>/private-project",
        "/gpfs/users/${USER}/private-project",
        "http://localhost:8000/api/health",
        "https://example.com/tutorial/input.fastq.gz",
        "oss://archive-${BUCKET}/tutorial/input.fastq.gz",
        "s3://${BUCKET}/tutorial/input.fastq.gz",
        "s3://<YOUR_BUCKET>/tutorial/input.fastq.gz",
        "gs://archive-<YOUR_BUCKET>/tutorial/input.fastq.gz",
        "cos://archive-${BUCKET}/tutorial/input.fastq.gz",
        "obs://archive-<YOUR_BUCKET>/tutorial/input.fastq.gz",
        "abfs://${CONTAINER}/tutorial/input.fastq.gz",
        "abfss://<YOUR_CONTAINER>@${STORAGE_ACCOUNT}.dfs.core.windows.net/tutorial/input.fastq.gz",
        "hdfs://${NAMENODE}/user/<YOUR_USERNAME>/private-project",
        r"C:\Users\<YOUR_USERNAME>\tutorial\input.fastq.gz",
        r"D:\${PROJECT_DIR}\tutorial\input.fastq.gz",
    ],
)
def test_private_locator_placeholders_are_not_reported(text: str) -> None:
    assert "private-locator" not in rule_names(text)


@pytest.mark.parametrize(
    "text",
    [
        r"C:\Users\<YOUR_USERNAME>\tutorial\input.fastq.gz",
        r"D:\${PROJECT_DIR}\tutorial\input.fastq.gz",
    ],
)
def test_windows_absolute_path_placeholders_are_not_reported(text: str) -> None:
    assert "windows-absolute-path" not in rule_names(text)


@pytest.mark.parametrize(
    "text",
    [
        "/data/fastq",
        "/data/image",
        "--fastqs=/data/fastq --sample=sample01",
        "--image=/data/image --sample=sample01",
        "/data/fastq/sampleA",
        "/data/image/tissue_hires_image.tif",
        "/data/tutorial/input.fastq.gz",
        "/scratch/tutorial/input.fastq.gz",
        "/gpfs/users/tutorial/input.fastq.gz",
        "/home/example/private-project",
        "/gpfs/project/example/private-project",
    ],
)
def test_private_locator_ignores_common_data_directories(text: str) -> None:
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


def test_finding_excerpt_redacts_sensitive_value_and_is_length_limited() -> None:
    secret = "super-secret-password"
    findings = scan_text(
        f'password = "{secret}" ' + ("x" * 300),
        source_path="sample.md",
    )

    assert len(findings) == 1
    assert secret not in findings[0].excerpt
    assert "[REDACTED]" in findings[0].excerpt
    assert len(findings[0].excerpt) <= 160


def test_private_locator_excerpt_is_redacted_and_length_limited() -> None:
    locator = "hdfs://compute01/user/alice/private-project"
    findings = scan_text(
        f"private source: {locator} " + ("x" * 300),
        source_path="sample.md",
    )

    assert findings
    assert all(locator not in finding.excerpt for finding in findings)
    assert all("[REDACTED]" in finding.excerpt for finding in findings)
    assert all(len(finding.excerpt) <= 160 for finding in findings)


def test_finding_excerpt_redacts_overlapping_sensitive_values() -> None:
    findings = scan_text(
        "Contact owner@compute.internal/private/jobs",
        source_path="sample.md",
    )

    assert findings
    assert all("/private/jobs" not in finding.excerpt for finding in findings)


def test_scan_public_content_rejects_missing_root(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="does not exist"):
        scan_public_content(tmp_path / "missing")


def test_scan_public_content_rejects_file_root(tmp_path: Path) -> None:
    file_path = tmp_path / "content.md"
    file_path.write_text("safe", encoding="utf-8")

    with pytest.raises(NotADirectoryError, match="not a directory"):
        scan_public_content(file_path)


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


def test_scan_script_reports_redacted_findings_and_returns_one(tmp_path: Path) -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    secret = "real-secret-123456"
    (tmp_path / "unsafe.md").write_text(
        f'secret = "{secret}"',
        encoding="utf-8",
    )

    completed = subprocess.run(
        [sys.executable, "scripts/scan_public_content.py", str(tmp_path)],
        cwd=backend_dir,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 1
    assert "[token]" in completed.stdout
    assert "[REDACTED]" in completed.stdout
    assert secret not in completed.stdout


def test_scan_script_reports_missing_root_and_returns_nonzero(tmp_path: Path) -> None:
    backend_dir = Path(__file__).resolve().parents[1]

    completed = subprocess.run(
        [sys.executable, "scripts/scan_public_content.py", str(tmp_path / "missing")],
        cwd=backend_dir,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "does not exist" in completed.stderr
