#!/usr/bin/env python3
"""
Layer 2: Bash コマンド動的安全ガード
PreToolUse(Bash) フック — 危険なコマンドを30+パターンで検査してブロック

exit 0 = 実行許可
exit 2 = ブロック（stderrの内容がClaudeへフィードバックされる）
"""

import sys
import json
import re

BLOCKED = [
    # [C1] ファイルシステム破壊
    (r"rm\s+(-[a-z]*r[a-z]*f|--recursive.*--force|--force.*--recursive)\s+[\"']?~[/\\]",
     "[C1] ホームディレクトリへの再帰削除は禁止"),
    (r"rm\s+(-[a-z]*r[a-z]*f|--recursive.*--force|--force.*--recursive)\s+[\"']?\/\s*$",
     "[C1] ルートディレクトリへの再帰削除は禁止"),
    (r"rm\s+(-[a-z]*r[a-z]*f|--recursive.*--force|--force.*--recursive)\s+[\"']?[Cc]:[/\\\\]\s*$",
     "[C1] Cドライブルートへの再帰削除は禁止"),
    (r"rm\s+(-[a-z]*r[a-z]*f|--recursive.*--force|--force.*--recursive)\s+[\"']?\/(?:usr|bin|lib|etc|boot|sys|proc|dev)\b",
     "[C1] システムディレクトリへの再帰削除は禁止"),
    (r"del\s+/[sS]\s+/[qQ]\s+[\"']?[Cc]:[/\\\\]",
     "[C1] Cドライブへのdel /s /q は禁止"),
    (r"Remove-Item\s+.*-Recurse\s+.*-Force\s+[\"']?[Cc]:[/\\\\]",
     "[C1] CドライブへのRemove-Item -Recurse -Force は禁止"),

    # [C2] Git 歴史破壊
    (r"git\s+push\s+.*--force(?!-with-lease)",
     "[C2] git push --force は禁止（git push --force-with-lease を使用）"),
    (r"git\s+push\s+.*-f(?:\s|$)",
     "[C2] git push -f は禁止"),
    (r"git\s+reset\s+--hard\s+(?!HEAD\^{0,2}$|HEAD~[12]$)",
     "[C2] git reset --hard（直近コミット以外）は禁止"),
    (r"git\s+clean\s+-[a-z]*[fd][a-z]*",
     "[C2] git clean -fd は禁止"),
    (r"git\s+filter-branch\b",
     "[C2] git filter-branch は禁止"),
    (r"git\s+push\s+.*--mirror\b",
     "[C2] git push --mirror は禁止"),

    # [C3] 権限昇格
    (r"\bsudo\s+(rm|dd|mkfs|format|shred|shutdown|reboot|halt|poweroff|passwd|adduser|deluser|chmod\s+777\s+/)",
     "[C3] sudo による危険な操作は禁止"),
    (r"\bsu\s+-\s*root\b",
     "[C3] root へのスイッチは禁止"),
    (r"runas\s+/user:Administrator",
     "[C3] Administratorとしての実行は禁止"),

    # [C4] ディスク破壊
    (r"\bdd\s+if=.+\s+of=/dev/(sd|hd|vd|xvd|nvme|disk)",
     "[C4] dd によるディスク書き込みは禁止"),
    (r"\bmkfs\b",
     "[C4] mkfs は禁止"),
    (r"\bformat\s+[a-zA-Z]:\s*$",
     "[C4] ドライブフォーマットは禁止"),
    (r"\bshred\s+.*-[a-z]*z",
     "[C4] shred によるデータ消去は禁止"),
    (r"\bwipefs\b",
     "[C4] wipefs は禁止"),

    # [C5] シークレット送信
    (r"curl.+\$(?:API_KEY|SECRET(?:_KEY)?|TOKEN|PASSWORD|PASSWD|ANTHROPIC_API_KEY|OPENAI_API_KEY)\b",
     "[C5] APIキーのcurl送信は禁止"),
    (r"wget.+\$(?:API_KEY|SECRET(?:_KEY)?|TOKEN|PASSWORD|PASSWD)\b",
     "[C5] APIキーのwget送信は禁止"),
    (r"curl.+Authorization:\s*Bearer\s+['\"]?\$[A-Z_]+",
     "[C5] 環境変数をBearer tokenとして外部送信は禁止"),

    # [C6] システム停止
    (r"shutdown\s+/[srh]",
     "[C6] Windows シャットダウン・再起動は禁止"),
    (r"\b(shutdown|reboot|halt|poweroff)\s+-[nhHrpf]",
     "[C6] システムシャットダウンは禁止"),
    (r"Stop-Computer\b",
     "[C6] Stop-Computer は禁止"),
    (r"Restart-Computer\b",
     "[C6] Restart-Computer は禁止"),

    # [C7] 環境変数流出
    (r"printenv\s*\|\s*curl",
     "[C7] 環境変数一覧の外部送信は禁止"),
    (r"env\s*\|\s*(curl|wget|nc|netcat)",
     "[C7] 環境変数の外部送信は禁止"),
    (r"cat\s+[~$].*\.env\s*\|\s*(curl|wget|nc)",
     "[C7] .envファイルの外部送信は禁止"),

    # [C8] 危険なchmod
    (r"chmod\s+-R\s+777\s+[/~]",
     "[C8] chmod -R 777 / または ~ は禁止"),
    (r"chmod\s+777\s+/etc",
     "[C8] /etcへの777は禁止"),

    # [C9] リバースシェル・外部スクリプト実行
    (r"(?:curl|wget)\s+[^\n]*\|\s*(?:bash|sh|python\d?|node|ruby|perl|powershell|pwsh)",
     "[C9] curl/wget | shell による外部スクリプト実行は禁止"),
    (r"Invoke-Expression\s*[\(]?.*(?:WebClient|Invoke-WebRequest|curl|wget)",
     "[C9] IEX(Invoke-WebRequest)によるリモートスクリプト実行は禁止"),
    (r"nc\s+-[elnp]+\s+\d+\s+-e\s+/bin",
     "[C9] netcatによるリバースシェルは禁止"),
    (r"bash\s+-i\s+>&\s*/dev/tcp/",
     "[C9] /dev/tcpを使ったリバースシェルは禁止"),

    # [C10] その他
    (r"git\s+config\s+--global\s+user\.(email|name)\s+.*@",
     "[C10] gitグローバル設定の書き換えは禁止"),
    (r"npm\s+publish\s+--access\s+public",
     "[C10] npmパッケージの公開パブリッシュは禁止"),
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

    if tool_name != "Bash":
        sys.exit(0)

    command = tool_input.get("command", "")
    if not command:
        sys.exit(0)

    for pattern, reason in BLOCKED:
        if re.search(pattern, command, re.IGNORECASE | re.DOTALL):
            msg = (
                f"[Allen Security Layer 2] BLOCKED\n"
                f"Reason : {reason}\n"
                f"Command: {command[:300]}\n"
                f"Action : Revise the command to a safer alternative."
            )
            sys.stderr.buffer.write(msg.encode("utf-8"))
            sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
