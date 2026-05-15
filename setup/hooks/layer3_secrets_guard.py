#!/usr/bin/env python3
"""
Layer 3: シークレット漏洩防止ガード
PreToolUse(Write|Edit|MultiEdit) フック

ファイルに書き込もうとする内容にAPIキー・パスワード・トークン等が
ハードコードされていないかを検査してブロックする。

実際の被害事例:
- AzureのAPIキーがMarkdownに書かれてGitHubに上がり、
  11日間気づかれず3万ドルの不正利用被害（2025年）

exit 0 = 書き込み許可
exit 2 = ブロック
"""

import sys
import json
import re
import os
import math
from collections import Counter

# =============================================================================
# [S1] 既知シークレットのパターン（サービス別）
# =============================================================================
KNOWN_SECRET_PATTERNS = [
    # Anthropic
    (r"sk-ant-api\d{2}-[a-zA-Z0-9\-_]{95}", "Anthropic API Key"),

    # OpenAI
    (r"sk-[a-zA-Z0-9]{20}T3BlbkFJ[a-zA-Z0-9]{20}", "OpenAI API Key (legacy)"),
    (r"sk-proj-[a-zA-Z0-9_\-]{80,}", "OpenAI Project API Key"),

    # AWS
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"(?:aws_secret_access_key|AWS_SECRET_ACCESS_KEY)\s*[=:]\s*['\"]?[a-zA-Z0-9/+]{40}['\"]?", "AWS Secret Access Key"),

    # Google
    (r"AIza[0-9A-Za-z\-_]{35}", "Google API Key"),
    (r"ya29\.[0-9A-Za-z\-_]+", "Google OAuth Token"),

    # GitHub
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
    (r"gho_[a-zA-Z0-9]{36}", "GitHub OAuth Token"),
    (r"ghs_[a-zA-Z0-9]{36}", "GitHub App Token"),
    (r"github_pat_[a-zA-Z0-9_]{82}", "GitHub Fine-Grained Token"),

    # Slack
    (r"xox[baprs]-[0-9]{12}-[0-9]{12}-[a-zA-Z0-9]{24}", "Slack Token"),
    (r"xoxb-[0-9]+-[0-9]+-[a-zA-Z0-9]+", "Slack Bot Token"),

    # Stripe
    (r"sk_live_[0-9a-zA-Z]{24,}", "Stripe Live Secret Key"),
    (r"rk_live_[0-9a-zA-Z]{24,}", "Stripe Restricted Live Key"),

    # Twilio
    (r"SK[0-9a-fA-F]{32}", "Twilio API Key"),
    (r"AC[a-zA-Z0-9]{32}", "Twilio Account SID"),

    # Square
    (r"sq0atp-[0-9A-Za-z\-_]{22}", "Square Access Token"),
    (r"sq0csp-[0-9A-Za-z\-_]{43}", "Square OAuth Secret"),

    # Mailgun / SendGrid
    (r"key-[0-9a-zA-Z]{32}", "Mailgun API Key"),
    (r"SG\.[a-zA-Z0-9_\-]{22}\.[a-zA-Z0-9_\-]{43}", "SendGrid API Key"),

    # LINE
    (r"['\"]?(?:channel_?secret|channel_?access_?token)['\"]?\s*[:=]\s*['\"][a-zA-Z0-9+/=]{20,}['\"]",
     "LINE Channel Secret/Token"),

    # Supabase
    (r"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+",
     "JWT Token (possibly Supabase/Firebase)"),

    # RSA/SSH Private Keys
    (r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----", "Private Key"),

    # 汎用パスワードパターン（変数代入）
    (r"(?:password|passwd|pwd|secret|api_key|apikey|access_token|auth_token)\s*[=:]\s*['\"][^\s'\"]{8,}['\"]",
     "Hardcoded Password/Secret"),
    (r"(?:DATABASE_URL|DB_PASSWORD|MYSQL_PASSWORD|POSTGRES_PASSWORD)\s*[=:]\s*['\"][^\s'\"]{6,}['\"]",
     "Hardcoded Database Credential"),
]

# =============================================================================
# [S2] 書き込みを禁止するファイルパス
# =============================================================================
PROTECTED_PATHS = [
    r"\.env$",
    r"\.env\.(local|prod|production|staging|development)$",
    r"secrets?\.(json|yaml|yml|toml|ini)$",
    r"credentials?\.(json|yaml|yml)$",
    r"service[-_]?account.*\.json$",
    r"id_rsa$",
    r"id_ed25519$",
    r".*\.pem$",
    r".*\.p12$",
    r".*\.pfx$",
    r"keystore\.jks$",
]

# =============================================================================
# [S3] エントロピー分析（高ランダム文字列の検出）
# =============================================================================
def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    freq = Counter(s)
    length = len(s)
    return -sum((c / length) * math.log2(c / length) for c in freq.values())


def has_high_entropy_secret(content: str) -> tuple[bool, str]:
    """高エントロピーの文字列が変数に代入されていないか検出"""
    pattern = re.compile(
        r"""(?:key|token|secret|password|passwd|api|auth)\s*[=:]\s*['"` ]([a-zA-Z0-9+/\-_=]{20,})['"` ]""",
        re.IGNORECASE
    )
    for match in pattern.finditer(content):
        candidate = match.group(1)
        entropy = shannon_entropy(candidate)
        if entropy > 4.0 and len(candidate) >= 20:
            return True, f"高エントロピー文字列を検出 (entropy={entropy:.2f}, value={candidate[:20]}...)"
    return False, ""


def main():
    try:
        raw = sys.stdin.buffer.read().decode("utf-8-sig")
        if not raw.strip():
            sys.exit(0)
        data = json.loads(raw)
        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})
    except Exception:
        sys.exit(0)

    if tool_name not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)

    # ファイルパスの確認
    file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
    filename = os.path.basename(file_path)

    # [S2] 保護対象ファイルへの書き込み禁止
    for pat in PROTECTED_PATHS:
        if re.search(pat, file_path, re.IGNORECASE):
            msg = (
                f"[Allen Security Layer 3] BLOCKED - Protected file\n"
                f"Reason : Writes to '{filename}' are blocked to prevent credential leaks.\n"
                f"Action : Use environment variables or a secrets manager instead."
            )
            sys.stderr.buffer.write(msg.encode("utf-8"))
            sys.exit(2)

    # 書き込む内容を取得
    content = tool_input.get("content", "") or tool_input.get("new_string", "")
    if not content:
        # MultiEdit の場合
        edits = tool_input.get("edits", [])
        content = " ".join(e.get("new_string", "") for e in edits if isinstance(e, dict))

    if not content:
        sys.exit(0)

    # [S1] 既知シークレットパターン検査
    for pattern, secret_type in KNOWN_SECRET_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            msg = (
                f"[Allen Security Layer 3] BLOCKED - Secret detected\n"
                f"Reason : '{secret_type}' が書き込み内容に検出されました。\n"
                f"File   : {file_path}\n"
                f"Action : 環境変数 (os.environ) またはシークレットマネージャーを使用してください。\n"
                f"         コード内にシークレットを直書きしないでください。"
            )
            sys.stderr.buffer.write(msg.encode("utf-8"))
            sys.exit(2)

    # [S3] 高エントロピー文字列検査
    found, reason = has_high_entropy_secret(content)
    if found:
        msg = (
            f"[Allen Security Layer 3] WARNING - High entropy string\n"
            f"Reason : {reason}\n"
            f"File   : {file_path}\n"
            f"Action : これがAPIキーやパスワードであれば環境変数を使用してください。\n"
            f"         意図的な文字列であれば、変数名を変更して再度お試しください。"
        )
        sys.stderr.buffer.write(msg.encode("utf-8"))
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
