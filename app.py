import json
import os
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv
from flask import Flask, render_template, request

MODEL_NAME = "claude-haiku-4-5-20251001"

app = Flask(__name__)
load_dotenv()


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


def build_x_post_system_prompt() -> str:
    return (
        "あなたは日本語のX投稿文作成アシスタントです。"
        "ユーザーの入力（今日やったこと・学んだこと）を基に、"
        "AIビジネス・中小企業DXに関連する投稿文を3パターン作成してください。"
        "必ずJSONのみで回答し、以下のスキーマを厳守してください:"
        "{"
        "\"posts\": ["
        "{\"text\": \"投稿文\"},"
        "{\"text\": \"投稿文\"},"
        "{\"text\": \"投稿文\"}"
        "]"
        "}"
        "制約:"
        "1) 各投稿は140文字以内。"
        "2) 絵文字は使わない。"
        "3) 各投稿にハッシュタグを3つ含める。"
        "4) ハッシュタグ以外も自然な日本語にする。"
        "5) JSON以外は出力しない。"
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


def validate_x_posts(result: dict[str, Any]) -> list[str]:
    posts = result.get("posts", [])
    if not isinstance(posts, list):
        return []

    normalized: list[str] = []
    for item in posts:
        if isinstance(item, dict):
            text = str(item.get("text", "")).strip()
        else:
            text = str(item).strip()

        if text:
            normalized.append(text)

    return normalized[:3]


def analyze_inquiry(inquiry_text: str) -> dict[str, Any]:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY が .env に設定されていません。")

    client = Anthropic(api_key=api_key)
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


def generate_x_posts(work_text: str, learning_text: str) -> list[str]:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY が .env に設定されていません。")

    client = Anthropic(api_key=api_key)
    combined = f"今日やったこと:\n{work_text}\n\n学んだこと:\n{learning_text}"

    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=900,
        temperature=0.5,
        system=build_x_post_system_prompt(),
        messages=[{"role": "user", "content": combined}],
    )

    text_blocks = [block.text for block in response.content if hasattr(block, "text")]
    joined_text = "\n".join(text_blocks)
    parsed = parse_response_json(joined_text)
    posts = validate_x_posts(parsed)

    if len(posts) < 3:
        raise ValueError("投稿文の生成に失敗しました。もう一度お試しください。")

    return posts


@app.route("/", methods=["GET", "POST"])
def index():
    inquiry_text = ""
    inquiry_result = None
    inquiry_error = ""
    x_error = ""
    x_posts = None
    work_text = ""
    learning_text = ""
    active_tab = request.args.get("tab", "inquiry")

    if request.method == "POST":
        action = request.form.get("action", "inquiry")
        active_tab = action

        if action == "inquiry":
            inquiry_text = request.form.get("inquiry", "").strip()
            if not inquiry_text:
                inquiry_error = "問い合わせ内容を入力してください。"
            else:
                try:
                    inquiry_result = analyze_inquiry(inquiry_text)
                except Exception as exc:
                    inquiry_error = f"分析中にエラーが発生しました: {exc}"
        elif action == "xpost":
            work_text = request.form.get("work_text", "").strip()
            learning_text = request.form.get("learning_text", "").strip()

            if not work_text or not learning_text:
                x_error = "「今日やったこと」と「学んだこと」を両方入力してください。"
            else:
                try:
                    x_posts = generate_x_posts(work_text, learning_text)
                except Exception as exc:
                    x_error = f"投稿文生成中にエラーが発生しました: {exc}"
        else:
            active_tab = "inquiry"

    return render_template(
        "index.html",
        active_tab=active_tab,
        inquiry_text=inquiry_text,
        inquiry_result=inquiry_result,
        inquiry_error=inquiry_error,
        work_text=work_text,
        learning_text=learning_text,
        x_posts=x_posts,
        x_error=x_error,
    )


if __name__ == "__main__":
    app.run(debug=True)
