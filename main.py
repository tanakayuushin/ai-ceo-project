import json
import os
import sys
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv

MODEL_NAME = "claude-haiku-4-5-20251001"


def build_system_prompt() -> str:
    return (
        "あなたは企業の問い合わせ一次対応AIです。"
        "ユーザーの問い合わせ文を読み、必ずJSONのみで回答してください。"
        "出力スキーマは以下を厳守:"
        "{"
        "\"category\": \"見積もり依頼|質問|クレーム|その他\","
        "\"urgency\": \"高|中|低\","
        "\"reply\": \"日本語の丁寧な返信文\","
        "\"summary\": [\"1行目\", \"2行目\", \"3行目\"]"
        "}"
        "summaryは必ず3要素。JSON以外のテキストは出力しないでください。"
    )


def parse_response_json(raw_text: str) -> dict[str, Any]:
    raw_text = raw_text.strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start != -1 and end != -1 and start < end:
            return json.loads(raw_text[start : end + 1])
        raise


def validate_result(result: dict[str, Any]) -> dict[str, Any]:
    category = result.get("category", "その他")
    urgency = result.get("urgency", "中")
    reply = result.get("reply", "返信文の生成に失敗しました。")
    summary = result.get("summary", [])

    if not isinstance(summary, list):
        summary = [str(summary)]

    summary_lines = [str(line).strip() for line in summary if str(line).strip()]

    while len(summary_lines) < 3:
        summary_lines.append("(要約情報なし)")

    return {
        "category": str(category),
        "urgency": str(urgency),
        "reply": str(reply),
        "summary": summary_lines[:3],
    }


def analyze_inquiry(client: Anthropic, inquiry_text: str) -> dict[str, Any]:
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=700,
        temperature=0.2,
        system=build_system_prompt(),
        messages=[
            {
                "role": "user",
                "content": f"問い合わせ本文:\n{inquiry_text}",
            }
        ],
    )

    text_blocks = [block.text for block in response.content if hasattr(block, "text")]
    joined_text = "\n".join(text_blocks)
    parsed = parse_response_json(joined_text)
    return validate_result(parsed)


def main() -> None:
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("エラー: ANTHROPIC_API_KEY が .env に設定されていません。")
        sys.exit(1)

    inquiry_text = input("問い合わせ内容を入力してください: ").strip()

    if not inquiry_text:
        print("エラー: 問い合わせ内容が空です。")
        sys.exit(1)

    client = Anthropic(api_key=api_key)

    try:
        result = analyze_inquiry(client, inquiry_text)
    except Exception as exc:
        print(f"API処理中にエラーが発生しました: {exc}")
        sys.exit(1)

    print("\n===== AI問い合わせ分析結果 =====")
    print(f"種類: {result['category']}")
    print(f"緊急度: {result['urgency']}")
    print("\n--- 自動返信案 ---")
    print(result["reply"])
    print("\n--- 3行要約 ---")
    for idx, line in enumerate(result["summary"], start=1):
        print(f"{idx}. {line}")


if __name__ == "__main__":
    main()
