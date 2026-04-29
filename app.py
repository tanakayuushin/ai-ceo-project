import json
import os
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect, url_for

MODEL_NAME = "claude-haiku-4-5-20251001"

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY", "emport-ai-secret-change-in-prod")
ACCESS_CODE = os.getenv("ACCESS_CODE", "emportai2026")


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


def build_manufacturing_prompt() -> str:
    return (
        "あなたはEmport AIのAI活用コンサルタントです。"
        "製造業の中小企業からの相談情報を分析し、最適なAI活用プランを日本語で提案してください。"
        "必ずJSONのみで回答し、以下のスキーマを厳守してください:"
        "{"
        "\"priority_issues\": [\"最優先課題1\", \"最優先課題2\", \"最優先課題3\"],"
        "\"solutions\": ["
        "{\"name\": \"ソリューション名\", \"description\": \"60字以内の説明\","
        " \"effect\": \"期待できる具体的な効果\", \"cost\": \"概算費用\", \"subsidy_cost\": \"補助金活用後の実質負担\"},"
        "{\"name\": \"...\", \"description\": \"...\", \"effect\": \"...\", \"cost\": \"...\", \"subsidy_cost\": \"...\"}"
        "],"
        "\"subsidy_info\": \"活用可能な補助金の説明（IT導入補助金・ものづくり補助金など）\","
        "\"next_step\": \"今すぐできる具体的な次のアクション（1〜2文）\""
        "}"
        "solutionsは2〜3件。priority_issuesは必ず3件。JSON以外のテキストは出力しないでください。"
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


def validate_manufacturing_result(result: dict[str, Any]) -> dict[str, Any]:
    priority_issues = result.get("priority_issues", [])
    if not isinstance(priority_issues, list):
        priority_issues = []
    priority_issues = [str(i).strip() for i in priority_issues if str(i).strip()][:3]
    while len(priority_issues) < 3:
        priority_issues.append("課題を分析中")

    solutions = result.get("solutions", [])
    if not isinstance(solutions, list):
        solutions = []
    validated_solutions = []
    for s in solutions[:3]:
        if isinstance(s, dict):
            validated_solutions.append({
                "name": str(s.get("name", "")),
                "description": str(s.get("description", "")),
                "effect": str(s.get("effect", "")),
                "cost": str(s.get("cost", "")),
                "subsidy_cost": str(s.get("subsidy_cost", "")),
            })

    return {
        "priority_issues": priority_issues,
        "solutions": validated_solutions,
        "subsidy_info": str(result.get("subsidy_info", "")),
        "next_step": str(result.get("next_step", "")),
    }


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
        messages=[{"role": "user", "content": f"問い合わせ本文:\n{inquiry_text}"}],
    )

    text_blocks = [block.text for block in response.content if hasattr(block, "text")]
    parsed = parse_response_json("\n".join(text_blocks))
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
    parsed = parse_response_json("\n".join(text_blocks))
    posts = validate_x_posts(parsed)

    if len(posts) < 3:
        raise ValueError("投稿文の生成に失敗しました。もう一度お試しください。")

    return posts


def build_sales_prompt() -> str:
    return (
        "あなたはAI営業支援アシスタントです。"
        "製造業・中小企業への30分AI提案商談をサポートします。"
        "ヒアリング内容をもとに商談資料を生成してください。"
        "必ずJSONのみで回答し、以下のスキーマを厳守:"
        "{"
        '"summary": "ヒアリング内容の2〜3行まとめ（この会社の状況と課題の核心）",'
        '"followup_questions": ["デモ前に確認すべき深掘り質問（1文）", "深掘り質問2"],'
        '"demo_points": ["デモで特に強調すべきポイント1", "ポイント2", "ポイント3"],'
        '"proposals": ['
        '{"title": "提案タイトル", "problem": "この会社の課題", "solution": "AIによる解決策", "effect": "具体的な効果", "cost": "概算費用", "subsidy": "補助金活用後の実質負担"},'
        '{"title": "...", "problem": "...", "solution": "...", "effect": "...", "cost": "...", "subsidy": "..."}'
        '],'
        '"closing_script": "クロージングのトークスクリプト（自然な日本語で2〜3文。次の面談や診断の申し込みにつなげる流れで）",'
        '"next_actions": ["次のアクション1（具体的に）", "次のアクション2", "次のアクション3"]'
        "}"
        "proposalsは2件。JSON以外は出力しないでください。"
    )


def validate_sales_result(result: dict[str, Any]) -> dict[str, Any]:
    proposals = result.get("proposals", [])
    validated_proposals = []
    for p in proposals[:2]:
        if isinstance(p, dict):
            validated_proposals.append({
                "title": str(p.get("title", "")),
                "problem": str(p.get("problem", "")),
                "solution": str(p.get("solution", "")),
                "effect": str(p.get("effect", "")),
                "cost": str(p.get("cost", "")),
                "subsidy": str(p.get("subsidy", "")),
            })

    followup = result.get("followup_questions", [])
    demo_points = result.get("demo_points", [])
    next_actions = result.get("next_actions", [])

    return {
        "summary": str(result.get("summary", "")),
        "followup_questions": [str(q) for q in followup[:3]],
        "demo_points": [str(p) for p in demo_points[:3]],
        "proposals": validated_proposals,
        "closing_script": str(result.get("closing_script", "")),
        "next_actions": [str(a) for a in next_actions[:3]],
    }


def generate_sales_guide(form_data: dict[str, Any]) -> dict[str, Any]:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY が .env に設定されていません。")

    content = (
        f"【商談相手】\n"
        f"会社名: {form_data.get('company_name', '不明')}\n"
        f"業種: {form_data.get('industry', '不明')}\n\n"
        f"【ヒアリング結果】\n"
        f"Q1. 一番困っている業務・作業は？\n→ {form_data.get('q1', '未回答')}\n\n"
        f"Q2. その業務にかかる時間・関わる人数は？\n→ {form_data.get('q2', '未回答')}\n\n"
        f"Q3. 今はどうやって対応しているか？\n→ {form_data.get('q3', '未回答')}\n\n"
        f"Q4. AI導入を考えたきっかけは？\n→ {form_data.get('q4', '未回答')}\n\n"
        f"Q5. 導入時期・予算のイメージは？\n→ {form_data.get('q5', '未回答')}"
    )

    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=1400,
        temperature=0.3,
        system=build_sales_prompt(),
        messages=[{"role": "user", "content": content}],
    )

    text_blocks = [block.text for block in response.content if hasattr(block, "text")]
    parsed = parse_response_json("\n".join(text_blocks))
    return validate_sales_result(parsed)


def analyze_manufacturing(form_data: dict[str, Any]) -> dict[str, Any]:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY が .env に設定されていません。")

    issues = form_data.get("issues", [])
    issues_text = "・" + "\n・".join(issues) if issues else "（未選択）"

    content = (
        f"【会社情報】\n"
        f"会社名: {form_data.get('company_name', '不明')}\n"
        f"業種: {form_data.get('industry', '不明')}\n"
        f"従業員数: {form_data.get('employees', '不明')}\n"
        f"IT活用レベル: {form_data.get('it_level', '不明')}\n\n"
        f"【困っている課題】\n{issues_text}\n\n"
        f"【その他・補足】\n{form_data.get('note', '（なし）')}"
    )

    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=1200,
        temperature=0.2,
        system=build_manufacturing_prompt(),
        messages=[{"role": "user", "content": content}],
    )

    text_blocks = [block.text for block in response.content if hasattr(block, "text")]
    parsed = parse_response_json("\n".join(text_blocks))
    return validate_manufacturing_result(parsed)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        code = request.form.get("code", "").strip()
        if code == ACCESS_CODE:
            session["authenticated"] = True
            return redirect(url_for("index"))
        error = "アクセスコードが違います。"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop("authenticated", None)
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    inquiry_text = ""
    inquiry_result = None
    inquiry_error = ""
    x_error = ""
    x_posts = None
    work_text = ""
    learning_text = ""
    mfg_result = None
    mfg_error = ""
    mfg_form = {}
    sales_result = None
    sales_error = ""
    sales_form = {}
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

        elif action == "manufacturing":
            mfg_form = {
                "company_name": request.form.get("company_name", "").strip(),
                "industry": request.form.get("industry", "").strip(),
                "employees": request.form.get("employees", "").strip(),
                "it_level": request.form.get("it_level", "").strip(),
                "issues": request.form.getlist("issues"),
                "note": request.form.get("note", "").strip(),
            }
            if not mfg_form["industry"] or not mfg_form["issues"]:
                mfg_error = "業種と課題を少なくとも1つ選択してください。"
            else:
                try:
                    mfg_result = analyze_manufacturing(mfg_form)
                except Exception as exc:
                    mfg_error = f"分析中にエラーが発生しました: {exc}"
        elif action == "sales":
            sales_form = {
                "company_name": request.form.get("company_name", "").strip(),
                "industry": request.form.get("industry", "").strip(),
                "q1": request.form.get("q1", "").strip(),
                "q2": request.form.get("q2", "").strip(),
                "q3": request.form.get("q3", "").strip(),
                "q4": request.form.get("q4", "").strip(),
                "q5": request.form.get("q5", "").strip(),
            }
            if not sales_form["q1"]:
                sales_error = "Q1（一番困っている業務）は必ず入力してください。"
            else:
                try:
                    sales_result = generate_sales_guide(sales_form)
                except Exception as exc:
                    sales_error = f"生成中にエラーが発生しました: {exc}"
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
        mfg_result=mfg_result,
        sales_result=sales_result,
        sales_error=sales_error,
        sales_form=sales_form,
        mfg_error=mfg_error,
        mfg_form=mfg_form,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
