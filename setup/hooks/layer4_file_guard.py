#!/usr/bin/env python3
"""
Layer 4: 重要ファイル保護ガード
PreToolUse(Write|Edit|MultiEdit|Bash) フック

セキュリティ上重要なファイルや設定ファイルへの
意図しない書き換えを防止する。

保護対象:
- Claude Codeの設定・フックファイル自体（自己改ざん防止）
- gitフック（悪意あるコードの注入防止）
- システム設定ファイル
- Windows Hostsファイル（DNS詐称防止）
"""

import sys
import json
import re
import os

# =============================================================================
# [F1] 書き換えを禁止するファイルパス（絶対パスまたは末尾パターン）
# =============================================================================
PROTECTED_FILE_PATTERNS = [
    # Claude Code 自身の設定・フック（自己改ざん防止）
    (r"\.claude[/\\]settings\.json$",
     "Claude Code設定ファイルへの書き込みは禁止（Claude自身が変更することを防止）"),
    (r"\.claude[/\\]hooks[/\\].*\.py$",
     "セキュリティフック自体への書き込みは禁止（セキュリティ無効化防止）"),

    # Git フック（悪意あるスクリプト注入防止）
    (r"\.git[/\\]hooks[/\\](pre-commit|post-commit|pre-push|post-merge|commit-msg)$",
     "gitフックへの書き込みは禁止（悪意あるコードの注入防止）"),

    # Windows システムファイル
    (r"[Cc]:[/\\][Ww]indows[/\\]System32[/\\]drivers[/\\]etc[/\\]hosts$",
     "Hostsファイルへの書き込みは禁止（DNS詐称防止）"),
    (r"[Cc]:[/\\][Ww]indows[/\\]System32[/\\].*\.dll$",
     "システムDLLへの書き込みは禁止"),
    (r"[Cc]:[/\\][Ww]indows[/\\]System32[/\\].*\.exe$",
     "システムexeへの書き込みは禁止"),

    # SSH設定
    (r"[/\\]\.ssh[/\\](authorized_keys|config|known_hosts)$",
     "SSH設定ファイルへの書き込みは禁止"),

    # シェル設定（意図しないコード注入防止）
    (r"[/\\]\.(bash_profile|bashrc|zshrc|profile|zprofile)$",
     "シェル設定ファイルへの書き込みは禁止（意図しないコード実行防止）"),
    (r"[/\\]\.powershell[/\\]profile\.ps1$",
     "PowerShellプロファイルへの書き込みは禁止"),
]

# =============================================================================
# [F2] Bashコマンドによる保護ファイルへのアクセスもブロック
# =============================================================================
PROTECTED_BASH_PATTERNS = [
    (r"(?:echo|printf|cat|tee|>>|>)\s+.*(?:\.claude[/\\]settings\.json|\.claude[/\\]hooks)",
     "Claude Code設定・フックへのBash書き込みは禁止"),
    (r"(?:echo|printf|tee|>>|>)\s+.*(?:\.git[/\\]hooks[/\\])",
     "gitフックへのBash書き込みは禁止"),
    (r"(?:echo|printf|tee|>>|>)\s+.*(?:drivers[/\\]etc[/\\]hosts|/etc/hosts)",
     "Hostsファイルへの書き込みは禁止"),
    (r"(?:echo|printf|tee|>>|>)\s+.*(?:\.ssh[/\\]authorized_keys)",
     "authorized_keysへの書き込みは禁止"),
    (r"curl\s+.*-o\s+.*(?:\.git[/\\]hooks[/\\])",
     "gitフックへのcurlダウンロードは禁止"),
    (r"curl\s+.*\|\s*(?:sh|bash|python|powershell)",
     "curl | shによる外部スクリプト直接実行は禁止"),
    (r"wget\s+.*\|\s*(?:sh|bash|python|powershell)",
     "wget | shによる外部スクリプト直接実行は禁止"),
    (r"Invoke-Expression\s*\(.*(?:WebClient|Invoke-WebRequest|curl|wget)",
     "IEX(Invoke-WebRequest)によるリモートスクリプト実行は禁止"),
]


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

    # --- Write/Edit/MultiEdit: ファイルパス検査 ---
    if tool_name in ("Write", "Edit", "MultiEdit"):
        file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
        for pattern, reason in PROTECTED_FILE_PATTERNS:
            if re.search(pattern, file_path, re.IGNORECASE):
                msg = (
                    f"[Allen Security Layer 4] BLOCKED - Protected file\n"
                    f"Reason : {reason}\n"
                    f"File   : {file_path}\n"
                    f"Action : このファイルへの変更が必要な場合はオーナーに確認してください。"
                )
                sys.stderr.buffer.write(msg.encode("utf-8"))
                sys.exit(2)

    # --- Bash: 保護ファイルへの書き込みコマンド検査 ---
    elif tool_name == "Bash":
        command = tool_input.get("command", "")
        for pattern, reason in PROTECTED_BASH_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE | re.DOTALL):
                msg = (
                    f"[Allen Security Layer 4] BLOCKED - Protected path via Bash\n"
                    f"Reason : {reason}\n"
                    f"Command: {command[:300]}\n"
                    f"Action : このファイルへの変更が必要な場合はオーナーに確認してください。"
                )
                sys.stderr.buffer.write(msg.encode("utf-8"))
                sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
