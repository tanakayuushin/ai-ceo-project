import json
import logging
import os
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect, url_for

load_dotenv()

MODEL_NAME = "claude-haiku-4-5-20251001"
MAX_INPUT_LENGTH = 2000  # ユーザー入力の最大文字数

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "emport-ai-secret-change-in-prod")
ACCESS_CODE = os.getenv("ACCESS_CODE", "emportai2026")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_api_key = os.getenv("ANTHROPIC_API_KEY")
if not _api_key:
    raise RuntimeError("ANTHROPIC_API_KEY が .env に設定されていません。")
client = Anthropic(api_key=_api_key)


SYSTEM_PROMPT_INQUIRY = """
<role>
あなたは企業の問い合わせ一次対応AIです。
受信した問い合わせを分析し、カテゴリ・緊急度・返信文・要約を返します。
</role>

<output_format>
出力はシステムが自動処理するため、JSONのみを返してください。前置きや説明文は不要です。
{
  "category": "見積もり依頼|質問|クレーム|その他",
  "urgency": "高|中|低",
  "reply": "日本語の丁寧な返信文",
  "summary": ["1行目", "2行目", "3行目"]
}
summaryは必ず3要素。
</output_format>

<example>
入力: 先日注文した商品がまだ届きません。注文番号は12345です。急いでいるので早めに対応してください。
出力:
{
  "category": "クレーム",
  "urgency": "高",
  "reply": "このたびはご不便をおかけし、大変申し訳ございません。ご注文番号12345の配送状況を至急確認し、本日中にご連絡いたします。",
  "summary": ["未着商品に関するクレーム", "注文番号12345・早急対応を要求", "本日中の状況確認と折り返し連絡が必要"]
}
</example>

<example>
入力: 商品が届いていないんですけどどうしたらいいですか
出力:
{
  "category": "質問",
  "urgency": "中",
  "reply": "お問い合わせいただきありがとうございます。商品がお手元に届いていないとのこと、大変ご不便をおかけしております。配送状況を確認のうえ、折り返しご連絡いたします。今しばらくお待ちくださいませ。",
  "summary": ["商品未着に関する問い合わせ", "怒りはなく対処法を聞いている質問トーン", "配送状況確認と折り返し連絡が必要"]
}
</example>
"""

SYSTEM_PROMPT_XPOST = """
<role>
あなたは日本語のX投稿文作成アシスタントです。
エンゲージメントが高い投稿を得意とし、
「AIを使いたいけど何から始めるべきかわからない」「業務を自動化・効率化したい」中小企業・個人事業主に刺さる投稿を作ります。
ユーザーの「今日やったこと・学んだこと」を基に、AIビジネス・中小企業DXに関連する投稿文を3パターン作成します。
</role>

<output_format>
出力はシステムが自動処理するため、JSONのみを返してください。
{"posts": [{"text": "投稿文1"}, {"text": "投稿文2"}, {"text": "投稿文3"}]}
</output_format>

<constraints>
1. 各投稿は140文字以内
2. 絵文字は使わない
3. 各投稿にハッシュタグを3つ含める
4. ハッシュタグ以外も自然な日本語にする
5. トーン・切り口を3パターンで変える（例：学び系・実績系・問いかけ系）
</constraints>
"""

SYSTEM_PROMPT_MANUFACTURING = """
<role>
あなたはEmport AIのAI活用コンサルタントです。
製造業の中小企業からの相談情報を分析し、実現可能で費用対効果の高いAI活用プランを日本語で提案してください。
補助金（IT導入補助金・ものづくり補助金・デジタル化・AI導入補助金2026など）を積極的に活用した提案を心がけてください。
</role>

<thinking_steps>
回答を作る前に、以下の順序で考えてください：
1. 会社の規模・IT習熟度・業種を把握する
2. 挙げられた課題の中で、AIで解決できるものとそうでないものを仕分ける
3. 費用対効果が最も高い課題から優先順位をつける
4. 各ソリューションに使える補助金を特定する
5. 上記を踏まえてJSONを出力する
</thinking_steps>

<output_format>
出力はシステムが自動処理するため、JSONのみを返してください。
{
  "priority_issues": ["最優先課題1", "最優先課題2", "最優先課題3"],
  "solutions": [
    {
      "name": "ソリューション名",
      "description": "60字以内の説明",
      "effect": "期待できる具体的な効果（数値があれば入れる）",
      "cost": "概算費用",
      "subsidy_cost": "補助金活用後の実質負担"
    }
  ],
  "subsidy_info": "活用可能な補助金の説明",
  "next_step": "今すぐできる具体的な次のアクション（1〜2文）"
}
solutionsは2〜3件。priority_issuesは必ず3件。
</output_format>

<constraints>
入力された相談内容に記載がない情報や、判断できない項目については推測で埋めず「確認が必要です」と記載してください。
</constraints>
"""

SYSTEM_PROMPT_MINUTES = """
<role>
あなたは会議における書記のスペシャリストです。
提供された議事録テキストを分析し、決定事項・TODO・次回議題を正確に抽出します。
</role>

<output_format>
出力はシステムが自動処理するため、JSONのみを返してください。
{
  "decisions": ["決定事項1", "決定事項2"],
  "todos": [
    {"task": "タスク内容", "owner": "担当者名（不明の場合は「不明」）", "due": "期限（記載なしの場合は「未定」）"}
  ],
  "next_agenda": ["次回議題1", "次回議題2"]
}
</output_format>

<constraints>
1. 議事録に記載されている情報だけを使うこと。
2. 記載がない・読み取れない項目は「不明」または「無し」とし、推測で補わないこと。
3. 各配列が空になる場合は空配列 [] を返すこと。
</constraints>
"""


def parse_response_json(raw_text: str) -> dict[str, Any]:
    raw_text = raw_text.strip()
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        logger.warning("JSONパース失敗。フォールバック処理を試みます: %s", raw_text[:100])
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
    if len(inquiry_text) > MAX_INPUT_LENGTH:
        raise ValueError(f"入力が長すぎます（{MAX_INPUT_LENGTH}文字以内にしてください）。")
    logger.info("analyze_inquiry: %d文字", len(inquiry_text))
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=500,
        temperature=0.2,
        system=SYSTEM_PROMPT_INQUIRY,
        messages=[
            {"role": "user", "content": f"<inquiry>\n{inquiry_text}\n</inquiry>"},
            {"role": "assistant", "content": "{"},
        ],
    )

    text_blocks = [block.text for block in response.content if hasattr(block, "text")]
    parsed = parse_response_json("{" + "\n".join(text_blocks))
    return validate_result(parsed)


def generate_x_posts(work_text: str, learning_text: str) -> list[str]:
    if len(work_text) + len(learning_text) > MAX_INPUT_LENGTH:
        raise ValueError(f"入力が長すぎます（合計{MAX_INPUT_LENGTH}文字以内にしてください）。")
    combined = f"今日やったこと:\n{work_text}\n\n学んだこと:\n{learning_text}"
    logger.info("generate_x_posts: %d文字", len(combined))

    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=500,
        temperature=0.5,
        system=SYSTEM_PROMPT_XPOST,
        messages=[{"role": "user", "content": combined}],
    )

    text_blocks = [block.text for block in response.content if hasattr(block, "text")]
    parsed = parse_response_json("\n".join(text_blocks))
    posts = validate_x_posts(parsed)

    if len(posts) < 3:
        raise ValueError("投稿文の生成に失敗しました。もう一度お試しください。")

    return posts


SYSTEM_PROMPT_SALES = """
<role>
あなたはAI営業支援アシスタントです。
製造業・中小企業への30分AI提案商談をサポートするため、ヒアリング内容をもとに商談資料を生成します。
顧客の課題に寄り添い、補助金を活用した費用対効果の高い提案を心がけてください。
</role>

<output_format>
出力はシステムが自動処理するため、JSONのみを返してください。
{
  "summary": "ヒアリング内容の2〜3行まとめ（この会社の状況と課題の核心）",
  "followup_questions": ["デモ前に確認すべき深掘り質問1", "深掘り質問2"],
  "demo_points": ["デモで特に強調すべきポイント1", "ポイント2", "ポイント3"],
  "proposals": [
    {
      "title": "提案タイトル",
      "problem": "この会社の課題",
      "solution": "AIによる解決策",
      "effect": "具体的な効果（数値化できれば入れる）",
      "cost": "概算費用",
      "subsidy": "補助金活用後の実質負担"
    }
  ],
  "closing_script": "クロージングのトークスクリプト（自然な日本語で2〜3文。次の面談や診断の申し込みにつなげる流れで）",
  "next_actions": ["次のアクション1（具体的に）", "次のアクション2", "次のアクション3"]
}
proposalsは2件。
</output_format>
"""


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
    content = (
        f"<client>\n"
        f"会社名: {form_data.get('company_name', '不明')}\n"
        f"業種: {form_data.get('industry', '不明')}\n"
        f"</client>\n\n"
        f"<hearing>\n"
        f"Q1. 一番困っている業務・作業は？\n→ {form_data.get('q1', '未回答')}\n\n"
        f"Q2. その業務にかかる時間・関わる人数は？\n→ {form_data.get('q2', '未回答')}\n\n"
        f"Q3. 今はどうやって対応しているか？\n→ {form_data.get('q3', '未回答')}\n\n"
        f"Q4. AI導入を考えたきっかけは？\n→ {form_data.get('q4', '未回答')}\n\n"
        f"Q5. 導入時期・予算のイメージは？\n→ {form_data.get('q5', '未回答')}\n"
        f"</hearing>"
    )

    logger.info("generate_sales_guide: %s", form_data.get("company_name", "不明"))
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=1400,
        temperature=0.3,
        system=SYSTEM_PROMPT_SALES,
        messages=[{"role": "user", "content": content}],
    )

    text_blocks = [block.text for block in response.content if hasattr(block, "text")]
    parsed = parse_response_json("\n".join(text_blocks))
    return validate_sales_result(parsed)


def validate_minutes_result(result: dict[str, Any]) -> dict[str, Any]:
    decisions = result.get("decisions", [])
    if not isinstance(decisions, list):
        decisions = []

    todos = result.get("todos", [])
    if not isinstance(todos, list):
        todos = []
    validated_todos = []
    for t in todos:
        if isinstance(t, dict):
            validated_todos.append({
                "task": str(t.get("task", "")),
                "owner": str(t.get("owner", "不明")),
                "due": str(t.get("due", "未定")),
            })

    next_agenda = result.get("next_agenda", [])
    if not isinstance(next_agenda, list):
        next_agenda = []

    return {
        "decisions": [str(d).strip() for d in decisions if str(d).strip()],
        "todos": validated_todos,
        "next_agenda": [str(a).strip() for a in next_agenda if str(a).strip()],
    }


def analyze_minutes(minutes_text: str) -> dict[str, Any]:
    if len(minutes_text) > MAX_INPUT_LENGTH:
        raise ValueError(f"入力が長すぎます（{MAX_INPUT_LENGTH}文字以内にしてください）。")
    logger.info("analyze_minutes: %d文字", len(minutes_text))
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=600,
        temperature=0.1,
        system=SYSTEM_PROMPT_MINUTES,
        messages=[
            {"role": "user", "content": f"<minutes>\n{minutes_text}\n</minutes>"},
            {"role": "assistant", "content": "{"},
        ],
    )

    text_blocks = [block.text for block in response.content if hasattr(block, "text")]
    parsed = parse_response_json("{" + "\n".join(text_blocks))
    return validate_minutes_result(parsed)


def analyze_manufacturing(form_data: dict[str, Any]) -> dict[str, Any]:
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

    logger.info("analyze_manufacturing: %s", form_data.get("company_name", "不明"))
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=1000,
        temperature=0.2,
        system=SYSTEM_PROMPT_MANUFACTURING,
        messages=[
            {"role": "user", "content": content},
            {"role": "assistant", "content": "{"},
        ],
    )

    text_blocks = [block.text for block in response.content if hasattr(block, "text")]
    parsed = parse_response_json("{" + "\n".join(text_blocks))
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
    minutes_text = ""
    minutes_result = None
    minutes_error = ""
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
        elif action == "minutes":
            minutes_text = request.form.get("minutes", "").strip()
            if not minutes_text:
                minutes_error = "議事録テキストを入力してください。"
            else:
                try:
                    minutes_result = analyze_minutes(minutes_text)
                except Exception as exc:
                    minutes_error = f"分析中にエラーが発生しました: {exc}"
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
        minutes_text=minutes_text,
        minutes_result=minutes_result,
        minutes_error=minutes_error,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
