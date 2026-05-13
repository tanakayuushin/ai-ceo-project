import json
import os
import pickle
import re
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

import requests
from fpdf import FPDF
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.pickle")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
FONT_PATH = r"C:\Windows\Fonts\msgothic.ttc"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def extract_spreadsheet_id(url_or_id: str) -> str:
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", url_or_id)
    return match.group(1) if match else url_or_id.strip()


def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"spreadsheet_url": "", "webhook_url": ""}


def save_settings(settings: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


def get_google_creds():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
    return creds


def fetch_responses(spreadsheet_id: str) -> list:
    creds = get_google_creds()
    service = build("sheets", "v4", credentials=creds)
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="A:Z"
    ).execute()
    return result.get("values", [])


def parse_timestamp(ts_str: str) -> datetime:
    for fmt in ("%Y/%m/%d %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M"):
        try:
            return datetime.strptime(ts_str.strip(), fmt)
        except ValueError:
            continue
    return datetime.min


def filter_new_rows(data: list, last_sent_at: str) -> list:
    """前回送信済みのタイムスタンプより新しい行だけ返す"""
    if not data or len(data) < 2:
        return data
    headers = data[0]
    rows = data[1:]
    col = {h.strip(): i for i, h in enumerate(headers)}
    ts_idx = col.get("タイムスタンプ", 0)

    if not last_sent_at:
        return [headers] + rows

    last_dt = parse_timestamp(last_sent_at)
    new_rows = [r for r in rows if parse_timestamp(
        r[ts_idx] if ts_idx < len(r) else "") > last_dt]
    return [headers] + new_rows


def deduplicate_by_name(rows_data: list) -> list:
    """同じ名前の回答は最新の1件だけ残す"""
    col = rows_data[0]["col"]
    name_idx = col.get("名前", 1)
    ts_idx = col.get("タイムスタンプ", 0)

    seen: dict = {}
    for item in rows_data:
        row = item["row"]
        name = row[name_idx].strip() if name_idx < len(row) else "不明"
        ts = parse_timestamp(row[ts_idx] if ts_idx < len(row) else "")
        if name not in seen or ts > seen[name]["ts"]:
            seen[name] = {"item": item, "ts": ts}

    return [v["item"] for v in seen.values()]


def get_latest_timestamp(data: list) -> str:
    """処理したデータの中で最も新しいタイムスタンプを返す"""
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


def group_by_activity(data: list) -> dict:
    if len(data) < 2:
        return {}
    headers = data[0]
    rows = data[1:]
    col = {h.strip(): i for i, h in enumerate(headers)}

    groups = {}
    for row in rows:
        idx = col.get("活動名", 2)
        activity = row[idx].strip() if idx < len(row) else "不明"
        if activity not in groups:
            groups[activity] = []
        groups[activity].append({"row": row, "col": col})

    # 活動ごとに名前で重複除去
    return {name: deduplicate_by_name(items) for name, items in groups.items()}


def get_val(row: list, col: dict, key: str) -> str:
    idx = col.get(key)
    if idx is None or idx >= len(row):
        return ""
    return row[idx].strip()


def generate_pdf(activity_name: str, rows_data: list, location: str, organizer: str) -> str:
    pdf = FPDF()
    pdf.add_font("Gothic", fname=FONT_PATH)
    pdf.add_page()
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    pdf.set_top_margin(20)
    w = pdf.w - 40

    # タイトル
    pdf.set_font("Gothic", size=20)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(w, 14, "SRC 活動記録", ln=True, align="C")
    pdf.ln(6)

    # 情報テーブル
    label_w = 28
    value_w = w - label_w
    first = rows_data[0]
    col = first["col"]
    row = first["row"]

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
        pdf.cell(value_w, 10, value, border=1, ln=True)

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

    safe_name = re.sub(r'[\\/:*?"<>|]', "_", activity_name)
    output_path = os.path.join(BASE_DIR, f"活動記録_{safe_name}.pdf")
    pdf.output(output_path)
    return output_path


def _draw_section(pdf: FPDF, w: float, title: str, items: list):
    pdf.set_font("Gothic", size=10)
    pdf.set_fill_color(220, 220, 220)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(w, 9, title, border=1, align="C", fill=True, ln=True)
    pdf.set_font("Gothic", size=9)
    pdf.set_fill_color(255, 255, 255)

    has_content = False
    for item in items:
        if item.strip():
            has_content = True
            for line in item.split("\n"):
                if line.strip():
                    pdf.multi_cell(w, 7, "・" + line, border="LR")
            pdf.ln(2)

    if not has_content:
        pdf.cell(w, 14, "", border="LR", ln=True)

    pdf.cell(w, 0, "", border="B", ln=True)


def send_to_discord(pdf_path: str, webhook_url: str, activity_name: str) -> bool:
    today = datetime.now().strftime("%Y/%m/%d")
    with open(pdf_path, "rb") as f:
        resp = requests.post(
            webhook_url,
            data={"payload_json": json.dumps({"content": f"【活動記録】{activity_name}（{today}）"})},
            files={"file": (os.path.basename(pdf_path), f, "application/pdf")},
        )
    return resp.status_code in (200, 204)


# ===== メインウィンドウ =====
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SRC 活動記録 → Discord")
        self.geometry("520x340")
        self.resizable(False, False)
        self.configure(bg="#0f1c35")
        self.settings = load_settings()
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="SRC 活動記録 Discord 送信ツール",
                 font=("MS Gothic", 13, "bold"), bg="#0f1c35", fg="#f0b429"
                 ).pack(pady=16)

        frame = tk.Frame(self, bg="#162040")
        frame.pack(fill="x", padx=24)

        tk.Label(frame, text="GoogleスプレッドシートのURL",
                 font=("MS Gothic", 9), bg="#162040", fg="#8a9bbf", anchor="w"
                 ).pack(fill="x", padx=16, pady=(14, 2))
        self.sheet_entry = tk.Entry(frame, font=("MS Gothic", 9),
                                    bg="#0f1c35", fg="#e8eaf0",
                                    insertbackground="#f0b429", relief="flat", bd=6)
        self.sheet_entry.pack(fill="x", padx=16, pady=(0, 10))
        self.sheet_entry.insert(0, self.settings.get("spreadsheet_url", ""))

        tk.Label(frame, text="Discord Webhook URL",
                 font=("MS Gothic", 9), bg="#162040", fg="#8a9bbf", anchor="w"
                 ).pack(fill="x", padx=16, pady=(0, 2))
        self.webhook_entry = tk.Entry(frame, font=("MS Gothic", 9),
                                      bg="#0f1c35", fg="#e8eaf0",
                                      insertbackground="#f0b429", relief="flat", bd=6, show="*")
        self.webhook_entry.pack(fill="x", padx=16, pady=(0, 2))
        self.webhook_entry.insert(0, self.settings.get("webhook_url", ""))

        tk.Button(frame, text="設定を保存",
                  font=("MS Gothic", 9), bg="#2a3f60", fg="#a8c0e0",
                  relief="flat", cursor="hand2", padx=12, pady=5,
                  command=self._save, activebackground="#3a5080"
                  ).pack(anchor="e", padx=16, pady=(6, 14))

        self.status_var = tk.StringVar(value="待機中...")
        tk.Label(self, textvariable=self.status_var,
                 font=("MS Gothic", 10), bg="#0f1c35", fg="#6ee7b7"
                 ).pack(pady=10)

        self.fetch_btn = tk.Button(self, text="活動データを取得する",
                                   font=("MS Gothic", 11, "bold"),
                                   bg="#f0b429", fg="#0f1c35",
                                   padx=20, pady=10, command=self._fetch,
                                   relief="flat", cursor="hand2", activebackground="#fbbf24")
        self.fetch_btn.pack()

    def _save(self):
        self.settings["spreadsheet_url"] = self.sheet_entry.get().strip()
        self.settings["webhook_url"] = self.webhook_entry.get().strip()
        save_settings(self.settings)
        self.status_var.set("設定を保存しました")

    def _fetch(self):
        sheet_url = self.sheet_entry.get().strip()
        webhook_url = self.webhook_entry.get().strip()
        if not sheet_url or not webhook_url:
            messagebox.showerror("エラー", "URLを両方入力してください。")
            return

        self.fetch_btn.config(state="disabled")
        self.status_var.set("データ取得中...")
        self.update()

        try:
            sid = extract_spreadsheet_id(sheet_url)
            raw_data = fetch_responses(sid)

            # 前回送信済みを除外
            last_sent = self.settings.get("last_sent_at", "")
            data = filter_new_rows(raw_data, last_sent)
            groups = group_by_activity(data)

            if not groups:
                msg = "新しい回答がありませんでした。" if last_sent else "回答が見つかりませんでした。"
                messagebox.showinfo("情報", msg)
                return

            total_count = sum(len(v) for v in groups.values())
            self.status_var.set(f"{len(groups)}件の活動・{total_count}件の新着回答を検出")
            ActivityDialog(self, groups, webhook_url, raw_data, self.settings, self)

        except Exception as exc:
            self.status_var.set("エラー発生")
            messagebox.showerror("エラー", str(exc))
        finally:
            self.fetch_btn.config(state="normal")


# ===== 活動ごとに場所・主催を入力するダイアログ =====
class ActivityDialog(tk.Toplevel):
    def __init__(self, parent, groups: dict, webhook_url: str,
                 raw_data: list, settings: dict, app: tk.Tk):
        super().__init__(parent)
        self.title("場所・主催を入力")
        self.configure(bg="#0f1c35")
        self.resizable(False, True)
        self.groups = groups
        self.webhook_url = webhook_url
        self.raw_data = raw_data
        self.settings = settings
        self.app = app
        self.entries = {}
        self._build_ui()
        self.grab_set()

    def _build_ui(self):
        tk.Label(self, text="各活動の場所と主催を入力してください",
                 font=("MS Gothic", 11, "bold"), bg="#0f1c35", fg="#f0b429"
                 ).pack(pady=14)

        # 下部固定エリア（ボタン・ステータス）
        bottom = tk.Frame(self, bg="#0f1c35")
        bottom.pack(side="bottom", fill="x", pady=12)

        self.status_var = tk.StringVar(value="")
        tk.Label(bottom, textvariable=self.status_var,
                 font=("MS Gothic", 9), bg="#0f1c35", fg="#6ee7b7"
                 ).pack(pady=(0, 6))

        tk.Button(bottom, text="PDFを生成してDiscordに送信",
                  font=("MS Gothic", 11, "bold"),
                  bg="#f0b429", fg="#0f1c35",
                  padx=20, pady=10, command=self._send,
                  relief="flat", cursor="hand2", activebackground="#fbbf24"
                  ).pack()

        # スクロール可能な活動リスト
        container = tk.Frame(self, bg="#0f1c35")
        container.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        canvas = tk.Canvas(container, bg="#0f1c35", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#0f1c35")

        scroll_frame.bind("<Configure>",
                          lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for activity_name, rows_data in self.groups.items():
            count = len(rows_data)
            card = tk.Frame(scroll_frame, bg="#162040")
            card.pack(fill="x", padx=4, pady=6)

            tk.Label(card, text=f"■ {activity_name}（{count}名回答）",
                     font=("MS Gothic", 10, "bold"), bg="#162040", fg="#f0b429", anchor="w"
                     ).pack(fill="x", padx=12, pady=(10, 4))

            row_frame = tk.Frame(card, bg="#162040")
            row_frame.pack(fill="x", padx=12, pady=(0, 10))

            tk.Label(row_frame, text="場所",
                     font=("MS Gothic", 9), bg="#162040", fg="#8a9bbf", width=6, anchor="w"
                     ).grid(row=0, column=0, sticky="w")
            loc_entry = tk.Entry(row_frame, font=("MS Gothic", 9),
                                 bg="#0f1c35", fg="#e8eaf0",
                                 insertbackground="#f0b429", relief="flat", bd=5, width=30)
            loc_entry.grid(row=0, column=1, padx=(4, 0), pady=2)

            tk.Label(row_frame, text="主催",
                     font=("MS Gothic", 9), bg="#162040", fg="#8a9bbf", width=6, anchor="w"
                     ).grid(row=1, column=0, sticky="w")
            org_entry = tk.Entry(row_frame, font=("MS Gothic", 9),
                                 bg="#0f1c35", fg="#e8eaf0",
                                 insertbackground="#f0b429", relief="flat", bd=5, width=30)
            org_entry.grid(row=1, column=1, padx=(4, 0), pady=2)

            self.entries[activity_name] = {"location": loc_entry, "organizer": org_entry}

        self.geometry("500x560")

    def _send(self):
        total = len(self.groups)
        sent = 0
        try:
            for i, (activity_name, rows_data) in enumerate(self.groups.items(), 1):
                location = self.entries[activity_name]["location"].get().strip()
                organizer = self.entries[activity_name]["organizer"].get().strip()

                self.status_var.set(f"PDF生成中... ({i}/{total}) {activity_name}")
                self.update()
                pdf_path = generate_pdf(activity_name, rows_data, location, organizer)

                self.status_var.set(f"Discord送信中... ({i}/{total}) {activity_name}")
                self.update()
                if send_to_discord(pdf_path, self.webhook_url, activity_name):
                    sent += 1

            # 送信成功後に最新タイムスタンプを保存
            latest_ts = get_latest_timestamp(self.raw_data)
            if latest_ts:
                self.settings["last_sent_at"] = latest_ts
                save_settings(self.settings)

            self.status_var.set(f"完了！{sent}/{total}件を送信しました")
            messagebox.showinfo("完了", f"{sent}件の活動記録をDiscordに送信しました！")
            self.destroy()

        except Exception as exc:
            self.status_var.set("エラー発生")
            messagebox.showerror("エラー", str(exc))


if __name__ == "__main__":
    app = App()
    app.mainloop()
