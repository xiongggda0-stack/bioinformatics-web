import re
from dataclasses import dataclass
from pathlib import Path


SUPPORTED_SUFFIXES = {".py", ".json", ".md", ".ts", ".tsx"}

_PLACEHOLDER = r"(?:<YOUR_[A-Z0-9_]+>|\$\{[A-Z_][A-Z0-9_]*\})"
_RULE_PATTERNS = {
    "login-password": re.compile(
        rf"\blogin\b[^\n]*?\s-p\s+(?!{_PLACEHOLDER})[^\s\"'`]+",
        re.IGNORECASE,
    ),
    "token": re.compile(
        rf"\b(?:token|api[_-]?token|access[_-]?token|auth[_-]?token|bearer[_-]?token|secret[_-]?token)"
        rf"\b\s*(?:=|:)\s*[\"']?(?!{_PLACEHOLDER})[A-Za-z0-9][A-Za-z0-9._~+/=-]{{7,}}",
        re.IGNORECASE,
    ),
    "email": re.compile(
        r"(?<![A-Za-z0-9._%+-])"
        r"[A-Za-z0-9.!#$%&'*+/=?^`{|}~-]+"
        r"@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
        r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+",
    ),
    "windows-absolute-path": re.compile(
        r"\b[A-Z]:[\\/](?:[^\\/\s\"'`]+[\\/]?)+",
        re.IGNORECASE,
    ),
    "private-locator": re.compile(
        rf"(?:"
        rf"(?:oss|s3|gs|cos|obs)://(?!{_PLACEHOLDER})[^\s\"'`\\]+"
        rf"|(?:/public/home|/home|/Users)/(?!{_PLACEHOLDER})[A-Za-z0-9._-]+(?:/[^\s\"'`\\]*)?"
        rf")",
        re.IGNORECASE,
    ),
}
_IGNORED_EMAIL_DOMAINS = {"example.com", "example.org", "example.net", "meta.data"}


@dataclass(frozen=True)
class ContentSafetyFinding:
    path: Path
    line_number: int
    rule_name: str
    excerpt: str


def scan_text(text: str, source_path: str | Path) -> list[ContentSafetyFinding]:
    path = Path(source_path)
    findings: list[ContentSafetyFinding] = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        for rule_name, pattern in _RULE_PATTERNS.items():
            for match in pattern.finditer(line):
                if rule_name == "email":
                    domain = match.group(0).rsplit("@", maxsplit=1)[1].lower()
                    if domain in _IGNORED_EMAIL_DOMAINS:
                        continue

                findings.append(
                    ContentSafetyFinding(
                        path=path,
                        line_number=line_number,
                        rule_name=rule_name,
                        excerpt=line.strip(),
                    )
                )

    return findings


def scan_public_content(root: str | Path) -> list[ContentSafetyFinding]:
    root_path = Path(root)
    findings: list[ContentSafetyFinding] = []

    for path in sorted(root_path.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            text = path.read_text(encoding="utf-8", errors="replace")
            findings.extend(scan_text(text, source_path=path))

    return findings
