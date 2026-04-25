"""
営業メール自動送信スクリプト
GitHub Actions から呼び出される
環境変数: GMAIL_ADDRESS, GMAIL_APP_PASSWORD, CHANGED_FILES
"""

import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

GMAIL_ADDRESS    = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
CHANGED_FILES    = os.environ.get("CHANGED_FILES", "").strip()
SENDER_SIGNATURE = "\n\n━━━━━━━━━━━━━━━━━━\nEmport AI　CEO アレン（Allen）\nMAIL: tsubeyou081@gmail.com\nX: @AI_chuusyou\n━━━━━━━━━━━━━━━━━━"


def parse_draft(content: str) -> dict | None:
    """
    Markdown の下書きから宛先メール・件名・本文を抽出する。

    期待フォーマット（AllenのエージェントがMD内に記載）:
        **宛先メール**: xxx@example.com
        **件名**: 〇〇〇
        ---
        本文...
    """
    lines = content.splitlines()

    to_email = ""
    subject  = ""
    body_lines = []
    in_body = False

    for line in lines:
        if not to_email and re.search(r'\*{0,2}宛先メール\*{0,2}\s*[:：]', line):
            to_email = re.sub(r'\*{0,2}宛先メール\*{0,2}\s*[:：]\s*', '', line).strip()
            continue
        if not subject and re.search(r'\*{0,2}件名\*{0,2}\s*[:：]', line):
            subject = re.sub(r'\*{0,2}件名\*{0,2}\s*[:：]\s*', '', line).strip()
            continue
        if subject and re.match(r'^---+$', line.strip()):
            in_body = True
            continue
        if in_body:
            body_lines.append(line)

    if not to_email or not subject:
        return None

    body = "\n".join(body_lines).strip()
    body = re.sub(r'^#{1,3}\s+', '', body, flags=re.MULTILINE)
    body = re.sub(r'\*\*(.+?)\*\*', r'\1', body)
    body = re.sub(r'\*(.+?)\*', r'\1', body)

    return {"to": to_email, "subject": subject, "body": body + SENDER_SIGNATURE}


def send_email(to: str, subject: str, body: str) -> None:
    msg = MIMEMultipart()
    msg["From"]    = GMAIL_ADDRESS
    msg["To"]      = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, to, msg.as_string())


def main():
    if not CHANGED_FILES:
        print("送信対象ファイルなし。終了します。")
        return

    files = [f.strip() for f in CHANGED_FILES.splitlines() if f.strip()]
    print(f"対象ファイル数: {len(files)}")

    sent = 0
    skipped = 0

    for filepath in files:
        path = Path(filepath)
        if not path.exists():
            print(f"スキップ（ファイル不存在）: {filepath}")
            skipped += 1
            continue

        content = path.read_text(encoding="utf-8")
        parsed  = parse_draft(content)

        if not parsed:
            print(f"スキップ（宛先または件名が見つからない）: {filepath}")
            skipped += 1
            continue

        try:
            send_email(parsed["to"], parsed["subject"], parsed["body"])
            print(f"送信完了: {parsed['to']} / {parsed['subject']}")
            sent += 1
        except Exception as e:
            print(f"送信エラー: {filepath} → {e}")
            skipped += 1

    print(f"\n結果: 送信 {sent} 件 / スキップ {skipped} 件")


if __name__ == "__main__":
    main()
