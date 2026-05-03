import base64
import json
import os
import pickle
import re
import uuid
from datetime import datetime

import requests
from flask import Flask, render_template, request
from fpdf import FPDF
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp_data")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# フォント（Windows / Linux 両対応）
_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msgothic.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Regular.otf",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJKjp-Regular.otf",
]
FONT_PATH = next((p for p in _FONT_CANDIDATES if os.path.exists(p)), _FONT_CANDIDATES[0])

os.makedirs(TEMP_DIR, exist_ok=True)

print("GOOGLE_CREDENTIALS set:", bool(os.environ.get("GOOGLE_CREDENTIALS")))
print("GOOGLE_TOKEN_B64 set:", bool(os.environ.get("GOOGLE_TOKEN_B64")))

app = Flask(__name__, template_folder="form_templates")
app.secret_key = os.environ.get("SECRET_KEY", "src-form-discord-2026")


def _credentials_file() -> str:
    """環境変数からcredentials.jsonを生成して返す（なければファイルを使う）"""
    creds_json = os.environ.get("GOOGLE_CREDENTIALS")
    if creds_json:
        path = os.path.join(TEMP_DIR, "credentials.json")
        with open(path, "w") as f:
            f.write(creds_json)
        return path
    return os.path.join(BASE_DIR, "credentials.json")


def _token_file() -> str:
    """環境変数からtoken.pickleを生成して返す（なければファイルを使う）"""
    token_b64 = os.environ.get("GOOGLE_TOKEN_B64")
    if token_b64:
        path = os.path.join(TEMP_DIR, "token.pickle")
        with open(path, "wb") as f:
            f.write(base64.b64decode(token_b64))
        return path
    return os.path.join(BASE_DIR, "token.pickle")


# ===== ユーティリティ =====

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"spreadsheet_url": "", "webhook_url": "", "last_sent_at": ""}


def save_settings(settings: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


def save_temp(data: dict) -> str:
    tid = str(uuid.uuid4())
    path = os.path.join(TEMP_DIR, f"{tid}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    return tid


def load_temp(tid: str) -> dict:
    path = os.path.join(TEMP_DIR, f"{tid}.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_spreadsheet_id(url_or_id: str) -> str:
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", url_or_id)
    return match.group(1) if match else url_or_id.strip()


def parse_timestamp(ts_str: str) -> datetime:
    for fmt in ("%Y/%m/%d %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M"):
        try:
            return datetime.strptime(ts_str.strip(), fmt)
        except ValueError:
            continue
    return datetime.min


def get_google_creds():
    token_file = _token_file()
    creds = None
    if os.path.exists(token_file):
        with open(token_file, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
            with open(token_file, "wb") as f:
                pickle.dump(creds, f)
        else:
            raise RuntimeError(
                "Google認証トークンが無効です。GOOGLE_TOKEN_B64 環境変数を再設定してください。"
            )
    return creds


def fetch_from_sheet(spreadsheet_id: str) -> list:
    creds = get_google_creds()
    service = build("sheets", "v4", credentials=creds)
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range="A:Z"
    ).execute()
    return result.get("values", [])


def filter_new_rows(data: list, last_sent_at: str) -> list:
    if not data or len(data) < 2:
        return data
    headers = data[0]
    rows = data[1:]
    col = {h.strip(): i for i, h in enumerate(headers)}
    ts_idx = col.get("タイムスタンプ", 0)
    if not last_sent_at:
        return [headers] + rows
    last_dt = parse_timestamp(last_sent_at)
    new_rows = [r for r in rows
                if parse_timestamp(r[ts_idx] if ts_idx < len(r) else "") > last_dt]
    return [headers] + new_rows


def group_by_activity(data: list) -> dict:
    if len(data) < 2:
        return {}
    headers = data[0]
    rows = data[1:]
    col = {h.strip(): i for i, h in enumerate(headers)}

    groups: dict = {}
    for row in rows:
        idx = col.get("活動名", 2)
        name = row[idx].strip() if idx < len(row) else "不明"
        if name not in groups:
            groups[name] = []
        groups[name].append({"row": row, "col": col})

    # 名前で重複除去（最新1件）
    name_idx = col.get("名前", 1)
    ts_idx = col.get("タイムスタンプ", 0)
    deduped = {}
    for activity, items in groups.items():
        seen: dict = {}
        for item in items:
            r = item["row"]
            person = r[name_idx].strip() if name_idx < len(r) else "不明"
            ts = parse_timestamp(r[ts_idx] if ts_idx < len(r) else "")
            if person not in seen or ts > seen[person]["ts"]:
                seen[person] = {"item": item, "ts": ts}
        deduped[activity] = [v["item"] for v in seen.values()]

    return deduped


def get_val(row: list, col: dict, key: str) -> str:
    idx = col.get(key)
    if idx is None or idx >= len(row):
        return ""
    return row[idx].strip()


def get_latest_timestamp(data: list) -> str:
    if len(data) < 2:
        return ""
    headers = data[0]
    col = {h.strip(): i for i, h in enumerate(headers)}
    ts_idx = col.get("タイムスタンプ", 0)
    latest = datetime.min
    for row in data[1:]:
        ts = parse_timestamp(row[ts_idx] if ts_idx < len(row) else "")
        if ts > latest:
            latest = ts
    return latest.strftime("%Y/%m/%d %H:%M:%S") if latest != datetime.min else ""


def generate_pdf(activity_name: str, rows_data: list, location: str, organizer: str) -> str:
    pdf = FPDF()
    pdf.add_font("Gothic", fname=FONT_PATH)
    pdf.add_page()
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    pdf.set_top_margin(20)
    w = pdf.w - 40

    pdf.set_font("Gothic", size=20)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(w, 14, "SRC 活動記録", ln=True, align="C")
    pdf.ln(6)

    first = rows_data[0]
    col = first["col"]
    row = first["row"]

    label_w = 28
    for label, value in [
        ("活動名", get_val(row, col, "活動名")),
        ("活動日", get_val(row, col, "活動日")),
        ("場所", location),
        ("参加者", f"SRC {len(rows_data)}名"),
        ("主催", organizer),
    ]:
        pdf.set_font("Gothic", size=10)
        pdf.set_fill_color(210, 210, 210)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(label_w, 10, label, border=1, align="C", fill=True)
        pdf.set_fill_color(255, 255, 255)
        pdf.cell(w - label_w, 10, value, border=1, ln=True)

    pdf.ln(8)
    _draw_section(pdf, w, "活動内容",
                  [get_val(r["row"], r["col"], "活動内容") for r in rows_data])
    pdf.ln(6)
    _draw_section(pdf, w, "振り返り（感想・学びなど）",
                  [get_val(r["row"], r["col"], "振り返り") for r in rows_data])
    pdf.set_font("Gothic", size=9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(w, 7, f"（{len(rows_data)}名回答）", ln=True, align="R")
    pdf.ln(6)
    _draw_section(pdf, w, "その他",
                  [get_val(r["row"], r["col"], "その他") for r in rows_data])

    safe = re.sub(r'[\\/:*?"<>|]', "_", activity_name)
    path = os.path.join(TEMP_DIR, f"活動記録_{safe}.pdf")
    pdf.output(path)
    return path


def _draw_section(pdf: FPDF, w: float, title: str, items: list):
    pdf.set_font("Gothic", size=10)
    pdf.set_fill_color(220, 220, 220)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(w, 9, title, border=1, align="C", fill=True, ln=True)
    pdf.set_font("Gothic", size=9)
    has = False
    for item in items:
        if item.strip():
            has = True
            for line in item.split("\n"):
                if line.strip():
                    pdf.multi_cell(w, 7, "・" + line, border="LR")
            pdf.ln(2)
    if not has:
        pdf.cell(w, 14, "", border="LR", ln=True)
    pdf.cell(w, 0, "", border="B", ln=True)


def post_to_discord(pdf_path: str, webhook_url: str, activity_name: str) -> bool:
    today = datetime.now().strftime("%Y/%m/%d")
    with open(pdf_path, "rb") as f:
        resp = requests.post(
            webhook_url,
            data={"payload_json": json.dumps({"content": f"【活動記録】{activity_name}（{today}）"})},
            files={"file": (os.path.basename(pdf_path), f, "application/pdf")},
        )
    return resp.status_code in (200, 204)


# ===== ルート =====

@app.route("/", methods=["GET"])
def index():
    settings = load_settings()
    return render_template("index.html",
                           step="input",
                           spreadsheet_url=settings.get("spreadsheet_url", ""),
                           webhook_url=settings.get("webhook_url", ""),
                           error="")


@app.route("/fetch", methods=["POST"])
def fetch():
    sheet_url = request.form.get("spreadsheet_url", "").strip()
    webhook_url = request.form.get("webhook_url", "").strip()

    if not sheet_url or not webhook_url:
        return render_template("index.html", step="input",
                               spreadsheet_url=sheet_url,
                               webhook_url=webhook_url,
                               error="URLを両方入力してください。")
    try:
        sid = extract_spreadsheet_id(sheet_url)
        settings = load_settings()
        raw_data = fetch_from_sheet(sid)
        filtered = filter_new_rows(raw_data, settings.get("last_sent_at", ""))
        groups = group_by_activity(filtered)

        if not groups:
            msg = "新しい回答がありませんでした。" if settings.get("last_sent_at") else "回答が見つかりませんでした。"
            return render_template("index.html", step="input",
                                   spreadsheet_url=sheet_url,
                                   webhook_url=webhook_url,
                                   error=msg)

        # 一時保存（colはJSONシリアライズのため別処理）
        serializable_groups = {
            name: [{"row": item["row"], "col": item["col"]} for item in items]
            for name, items in groups.items()
        }
        tid = save_temp({
            "groups": serializable_groups,
            "webhook_url": webhook_url,
            "raw_data": raw_data,
            "spreadsheet_url": sheet_url,
        })

        # 設定保存
        settings["spreadsheet_url"] = sheet_url
        settings["webhook_url"] = webhook_url
        save_settings(settings)

        activities = [{"name": name, "count": len(items)}
                      for name, items in groups.items()]
        return render_template("index.html", step="activities",
                               activities=activities, tid=tid, error="")

    except Exception as e:
        return render_template("index.html", step="input",
                               spreadsheet_url=sheet_url,
                               webhook_url=webhook_url,
                               error=f"エラー: {e}")


@app.route("/send", methods=["POST"])
def send():
    tid = request.form.get("tid", "")
    temp = load_temp(tid)
    if not temp:
        return render_template("index.html", step="input",
                               spreadsheet_url="", webhook_url="",
                               error="セッションが切れました。もう一度やり直してください。")

    groups = temp["groups"]
    webhook_url = temp["webhook_url"]
    raw_data = temp["raw_data"]

    results = []
    for activity_name, items in groups.items():
        location = request.form.get(f"location_{activity_name}", "").strip()
        organizer = request.form.get(f"organizer_{activity_name}", "").strip()
        try:
            pdf_path = generate_pdf(activity_name, items, location, organizer)
            success = post_to_discord(pdf_path, webhook_url, activity_name)
            results.append({"name": activity_name, "success": success})
        except Exception as e:
            results.append({"name": activity_name, "success": False, "error": str(e)})

    # タイムスタンプ保存
    latest_ts = get_latest_timestamp(raw_data)
    if latest_ts:
        settings = load_settings()
        settings["last_sent_at"] = latest_ts
        save_settings(settings)

    return render_template("index.html", step="result", results=results, error="")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
