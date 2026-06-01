import re
from dataclasses import dataclass
from pathlib import Path


SUPPORTED_SUFFIXES = {".py", ".json", ".md", ".ts", ".tsx"}
EXCERPT_MAX_LENGTH = 160
REDACTED = "[REDACTED]"

_PLACEHOLDER_TEXT = r"(?:<YOUR_[A-Z0-9_]+>|\$\{[A-Z_][A-Z0-9_]*\})"
_VALUE_TEXT = r"(?:\"[^\"\r\n]{1,512}\"|'[^'\r\n]{1,512}'|[^\s\"'`]{1,512})"
_PLACEHOLDER_PATTERN = re.compile(rf"^{_PLACEHOLDER_TEXT}$", re.IGNORECASE)
_LOGIN_COMMAND_PATTERN = re.compile(r"\blogin\b[^\r\n]{0,512}", re.IGNORECASE)
_LOGIN_OPTION_PATTERN = re.compile(
    rf"(?:^|\s)-(?P<option>[up])\s+(?P<value>{_VALUE_TEXT})",
    re.IGNORECASE,
)
_PASSWORD_PATTERN = re.compile(
    rf"\bpassword\b\s*(?:=|:)\s*(?P<value>{_VALUE_TEXT})",
    re.IGNORECASE,
)
_TOKEN_ASSIGNMENT_PATTERN = re.compile(
    rf"\b(?:token|api[_-]?token|access[_-]?token|auth[_-]?token|bearer[_-]?token|"
    rf"secret[_-]?token|api[_-]?key|secret)\b\s*(?:=|:)\s*(?P<value>{_VALUE_TEXT})",
    re.IGNORECASE,
)
_BEARER_TOKEN_PATTERN = re.compile(
    rf"\bauthorization\b\s*:\s*bearer\s+(?P<value>{_VALUE_TEXT})",
    re.IGNORECASE,
)
_EMAIL_PATTERN = re.compile(
    r"(?<![A-Za-z0-9._%+-])"
    r"[A-Za-z0-9.!#$%&'*+/=?^`{|}~-]+"
    r"@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+",
)
_WINDOWS_ABSOLUTE_PATH_PATTERN = re.compile(
    r"\b[A-Z]:[\\/][^\s\"'`]{1,512}",
    re.IGNORECASE,
)
_CLOUD_URI_PATTERN = re.compile(
    rf"\b(?:oss|s3|gs|cos|obs)://(?P<value>[^\s\"'`\\]{{1,512}})",
    re.IGNORECASE,
)
_PERSONAL_PATH_PATTERN = re.compile(
    rf"(?:/public/home|/home|/Users|/scratch)/"
    rf"(?P<user>{_PLACEHOLDER_TEXT}|[A-Za-z0-9._-]{{1,128}})/"
    rf"[^\s\"'`\\]{{1,384}}",
)
_DATA_PERSONAL_PATH_PATTERN = re.compile(
    rf"/data/(?!fastq/|image/|input/|output/|raw/|ref/|reference/|results?/|tmp/)"
    rf"(?P<user>{_PLACEHOLDER_TEXT}|[A-Za-z0-9._-]{{1,128}})/"
    rf"[^\s\"'`\\]{{1,384}}",
    re.IGNORECASE,
)
_IP_OCTET = r"(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})"
_PRIVATE_IP_PATTERN = re.compile(
    rf"(?<![\d.])(?:"
    rf"10(?:\.{_IP_OCTET}){{3}}"
    rf"|192\.168(?:\.{_IP_OCTET}){{2}}"
    rf"|172\.(?:1[6-9]|2[0-9]|3[01])(?:\.{_IP_OCTET}){{2}}"
    rf")(?::[0-9]{{1,5}})?(?:/[^\s\"'`\\]{{0,384}})?"
)
_PRIVATE_DOMAIN_PATTERN = re.compile(
    r"(?<![A-Za-z0-9.-])(?:https?://)?"
    r"(?:[A-Za-z0-9-]+\.)+(?:internal|local)"
    r"(?::[0-9]{1,5})?(?:/[^\s\"'`\\]{0,384})?",
    re.IGNORECASE,
)
_IGNORED_EMAIL_DOMAINS = {"example.com", "example.org", "example.net"}


@dataclass(frozen=True)
class ContentSafetyFinding:
    path: Path
    line_number: int
    rule_name: str
    excerpt: str


@dataclass(frozen=True)
class _LineMatch:
    rule_name: str
    start: int
    end: int


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _is_placeholder(value: str) -> bool:
    return _PLACEHOLDER_PATTERN.fullmatch(_unquote(value)) is not None


def _is_r_slot_expression(line: str, match: re.Match[str]) -> bool:
    if match.group(0).rsplit("@", maxsplit=1)[1].lower() != "meta.data":
        return False

    before = line[: match.start()]
    after = line[match.end() :]
    return re.search(r"(?:<-|=)\s*$", before) is not None or after.lstrip().startswith("|>")


def _redact_excerpt(line: str, matches: list[_LineMatch]) -> str:
    parts: list[str] = []
    cursor = 0
    intervals: list[tuple[int, int]] = []

    for match in sorted(matches, key=lambda item: (item.start, item.end)):
        if intervals and match.start <= intervals[-1][1]:
            start, end = intervals[-1]
            intervals[-1] = (start, max(end, match.end))
            continue
        intervals.append((match.start, match.end))

    for start, end in intervals:
        parts.append(line[cursor:start])
        parts.append(REDACTED)
        cursor = end

    parts.append(line[cursor:])
    excerpt = "".join(parts).strip()
    if len(excerpt) > EXCERPT_MAX_LENGTH:
        return f"{excerpt[: EXCERPT_MAX_LENGTH - 3]}..."
    return excerpt


def _find_line_matches(line: str) -> list[_LineMatch]:
    matches: list[_LineMatch] = []

    for command in _LOGIN_COMMAND_PATTERN.finditer(line):
        credentials = _LOGIN_OPTION_PATTERN.finditer(command.group(0))
        if any(not _is_placeholder(item.group("value")) for item in credentials):
            matches.append(_LineMatch("login-password", command.start(), command.end()))

    for match in _PASSWORD_PATTERN.finditer(line):
        if not _is_placeholder(match.group("value")):
            matches.append(_LineMatch("login-password", match.start(), match.end()))

    for pattern in (_TOKEN_ASSIGNMENT_PATTERN, _BEARER_TOKEN_PATTERN):
        for match in pattern.finditer(line):
            if not _is_placeholder(match.group("value")):
                matches.append(_LineMatch("token", match.start(), match.end()))

    for match in _EMAIL_PATTERN.finditer(line):
        domain = match.group(0).rsplit("@", maxsplit=1)[1].lower()
        if domain in _IGNORED_EMAIL_DOMAINS or _is_r_slot_expression(line, match):
            continue
        matches.append(_LineMatch("email", match.start(), match.end()))

    for match in _WINDOWS_ABSOLUTE_PATH_PATTERN.finditer(line):
        matches.append(_LineMatch("windows-absolute-path", match.start(), match.end()))

    for match in _CLOUD_URI_PATTERN.finditer(line):
        if not _is_placeholder(match.group("value")):
            matches.append(_LineMatch("private-locator", match.start(), match.end()))

    for pattern in (_PERSONAL_PATH_PATTERN, _DATA_PERSONAL_PATH_PATTERN):
        for match in pattern.finditer(line):
            if not _is_placeholder(match.group("user")):
                matches.append(_LineMatch("private-locator", match.start(), match.end()))

    for pattern in (_PRIVATE_IP_PATTERN, _PRIVATE_DOMAIN_PATTERN):
        for match in pattern.finditer(line):
            matches.append(_LineMatch("private-locator", match.start(), match.end()))

    return matches


def scan_text(text: str, source_path: str | Path) -> list[ContentSafetyFinding]:
    path = Path(source_path)
    findings: list[ContentSafetyFinding] = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        matches = _find_line_matches(line)
        excerpt = _redact_excerpt(line, matches)
        findings.extend(
            ContentSafetyFinding(
                path=path,
                line_number=line_number,
                rule_name=match.rule_name,
                excerpt=excerpt,
            )
            for match in matches
        )

    return findings


def scan_public_content(root: str | Path) -> list[ContentSafetyFinding]:
    root_path = Path(root)
    if not root_path.exists():
        raise FileNotFoundError(f"Public content root does not exist: {root_path}")
    if not root_path.is_dir():
        raise NotADirectoryError(f"Public content root is not a directory: {root_path}")

    findings: list[ContentSafetyFinding] = []
    for path in sorted(root_path.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            text = path.read_text(encoding="utf-8", errors="replace")
            findings.extend(scan_text(text, source_path=path))

    return findings
