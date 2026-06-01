import subprocess
import sys
from pathlib import Path

import pytest

from app.services.content_safety_service import scan_public_content, scan_text
from scripts import scan_public_content as scan_script


def rule_names(text: str) -> set[str]:
    return {finding.rule_name for finding in scan_text(text, source_path="sample.md")}


def test_plain_login_password_is_reported() -> None:
    findings = scan_text(
        "./lnd login -u alice-lab-user -p fakeSecret123",
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
    ['"fakeSecret123"', "'fakeSecret123'"],
)
def test_quoted_login_passwords_are_reported(password: str) -> None:
    assert "login-password" in rule_names(
        f"./lnd login -u alice-lab-user -p {password}"
    )


def test_password_assignment_is_reported() -> None:
    assert "login-password" in rule_names('password = "fakeSecret123"')


def test_login_real_username_is_reported_when_password_is_placeholder() -> None:
    assert "login-password" in rule_names(
        "./lnd login -u alice-lab-user -p <YOUR_PASSWORD>"
    )


@pytest.mark.parametrize(
    "text",
    [
        "./lnd login --username alice-lab-user --password fakeSecret123",
        './lnd login --username="alice-lab-user" --password="fakeSecret123"',
        "./lnd login -u='alice-lab-user' -p='fakeSecret123'",
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
        "./lnd login --username alice-lab-user --password <YOUR_PASSWORD>",
        './lnd login --username="alice-lab-user" --password="${PASSWORD}"',
        "./lnd login -u='alice-lab-user' -p='<YOUR_PASSWORD>'",
    ],
)
def test_login_option_variants_report_real_username_with_placeholder_password(
    text: str,
) -> None:
    assert "login-password" in rule_names(text)


@pytest.mark.parametrize(
    ("text", "expected_rule"),
    [
        ('api_token = "fakeTokenValue123456"', "token"),
        ("token = fakeToken123", "token"),
        ("TOKEN: fakeToken123", "token"),
        ('api_key = "fakeApiKey123456"', "token"),
        ('secret = "fakeSecret123456"', "token"),
        ("Authorization: Bearer fakeToken123", "token"),
        ('{"Authorization": "Bearer fakeToken123"}', "token"),
        ("bearer = fakeToken123", "token"),
        ("Contact alice-lab-user@example.edu before publishing.", "email"),
        ("Contact alice-lab-user@meta.data before publishing.", "email"),
        (
            r'workdir = "C:\Users\alice-lab-user\private-demo-project"',
            "windows-absolute-path",
        ),
        ('workdir = "D:/private-demo/project"', "windows-absolute-path"),
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
        "oss://private-demo-bucket/tutorial/01.RawData",
        "/public/home/alice-lab-user/private-demo-project/results",
        "/home/alice-lab-user/private-demo-project/results",
        "/Users/alice-lab-user/private-demo-project/results",
        "http://10.0.0.42:8080/private-demo/api",
        "192.168.0.42",
        "172.16.0.42",
        "https://compute-demo.cluster.internal/jobs",
        "cache-demo.service.local",
        "/scratch/alice-lab-user/private-demo-project/results",
        "/data/alice-lab-user/private-demo-project/results",
        "/gpfs/users/alice-lab-user/private-demo-project/results",
        "/home/alice-lab-user",
        "/scratch/alice-lab-user",
        "/data/alice-lab-user",
        "/gpfs/users/alice-lab-user",
        "/gpfs/project/alice-lab-user/private-demo-project",
        "http://compute-demo-01:8080/private/api",
        "hdfs://compute-demo-01/user/alice-lab-user/private-demo-project",
        "hdfs://namenode-demo.example.com/user/alice-lab-user/private-demo-project",
        "s3://private-demo-bucket/tutorial/input.fastq.gz",
        "gs://private-demo-bucket/tutorial/input.fastq.gz",
        "cos://private-demo-bucket/tutorial/input.fastq.gz",
        "obs://private-demo-bucket/tutorial/input.fastq.gz",
        "abfs://private-demo-container/tutorial/input.fastq.gz",
        "abfss://private-demo-container@storage-demo.dfs.core.windows.net/tutorial/input.fastq.gz",
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
    ("text", "expected_rule"),
    [
        ("s3://private-demo-bucket/${FOLDER}/input.fastq.gz", "private-locator"),
        (r"C:\Users\alice-lab-user\${PROJECT_DIR}", "windows-absolute-path"),
    ],
)
def test_locator_placeholder_only_ignores_sensitive_component(
    text: str,
    expected_rule: str,
) -> None:
    assert expected_rule in rule_names(text)


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


@pytest.mark.parametrize(
    "text",
    [
        "10.0.0.999",
        "192.168.0.999",
        "172.16.0.999",
    ],
)
def test_private_locator_ignores_invalid_private_ip_prefixes(text: str) -> None:
    assert "private-locator" not in rule_names(text)


def test_scan_public_content_reads_supported_extensions_only(tmp_path: Path) -> None:
    for suffix in [".py", ".json", ".md", ".ts", ".tsx"]:
        (tmp_path / f"unsafe{suffix}").write_text(
            'api_token = "fakeTokenValue123456"',
            encoding="utf-8",
        )
    (tmp_path / "ignored.txt").write_text(
        'api_token = "fakeTokenValue123456"',
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
        b"\xff\n./lnd login -u alice-lab-user -p fakeSecret123\n"
    )

    findings = scan_public_content(tmp_path)

    assert [finding.rule_name for finding in findings] == ["login-password"]


def test_finding_excerpt_redacts_sensitive_value_and_is_length_limited() -> None:
    secret = "fakeSecretPassword123"
    findings = scan_text(
        f'password = "{secret}" ' + ("x" * 300),
        source_path="sample.md",
    )

    assert len(findings) == 1
    assert secret not in findings[0].excerpt
    assert "[REDACTED]" in findings[0].excerpt
    assert len(findings[0].excerpt) <= 160


@pytest.mark.parametrize(
    "line_prefix",
    [
        "token = ",
        "password = ",
        "./lnd login -u alice-lab-user -p ",
    ],
)
def test_finding_excerpt_redacts_entire_overlong_sensitive_value(
    line_prefix: str,
) -> None:
    secret = "s" * 600
    findings = scan_text(
        f"{line_prefix}{secret} visible-context " + ("x" * 300),
        source_path="sample.md",
    )

    assert len(findings) == 1
    assert "s" * 20 not in findings[0].excerpt
    assert "[REDACTED]" in findings[0].excerpt
    assert len(findings[0].excerpt) <= 160


def test_private_locator_excerpt_is_redacted_and_length_limited() -> None:
    locator = "hdfs://compute-demo-01/user/alice-lab-user/private-demo-project"
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
        "Contact alice-lab-user@compute-demo.internal/private-demo/jobs",
        source_path="sample.md",
    )

    assert findings
    assert all("/private-demo/jobs" not in finding.excerpt for finding in findings)


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
    secret = "fakeSecret123456"
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


@pytest.mark.parametrize(
    "error",
    [
        PermissionError("permission denied"),
        OSError("read failed"),
    ],
)
def test_scan_script_reports_os_errors_without_traceback(
    error: OSError,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def raise_error(root: Path) -> list[object]:
        raise error

    monkeypatch.setattr(scan_script, "scan_public_content", raise_error)

    assert scan_script.main([]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == f"Public content safety scan failed: {error}\n"
    assert "Traceback" not in captured.err
