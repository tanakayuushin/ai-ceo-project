#!/usr/bin/env python3
"""
Emport AI 議事録自動生成ツール
テキストまたは文字起こしを入力 → 構造化議事録をAIで生成
起動: python minutes.py
アクセス: http://localhost:5002
"""

import json
import os
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify
import urllib.request
import urllib.error

app = Flask(__name__)
MINUTES_FILE = os.path.join(os.path.dirname(__file__), "minutes_data.json")

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

SYSTEM_PROMPT = """あなたは経営会議の議事録作成の専門家です。
入力された会議の文字起こしや内容を、以下の構造で整理してください。

出力形式（Markdown）:
## 📋 会議概要
- 目的・議題

## ✅ 決定事項
箇条書きで明確に

## 📌 アクションアイテム
| 担当 | タスク | 期限 |
|------|--------|------|

## 💬 主な議論
要点を箇条書きで

## ⏭️ 次回予定
次回アジェンダや懸案事項

簡潔かつ正確に、ビジネス文書として適切な表現でまとめてください。"""


def call_claude(text: str, api_key: str) -> str:
    url = "https://api.anthropic.com/v1/messages"
    payload = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 2000,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": f"以下の会議内容から議事録を作成してください:\n\n{text}"}]
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("x-api-key", api_key)
    req.add_header("anthropic-version", "2023-06-01")
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        return data["content"][0]["text"]


def load_minutes():
    if not os.path.exists(MINUTES_FILE):
        return []
    with open(MINUTES_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_minutes(data):
    with open(MINUTES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Emport AI — 議事録ツール</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0d1b2a; color: #fff; font-family: -apple-system, sans-serif; }
  .header { background: #0a2342; padding: 16px 24px; border-bottom: 1px solid #2a4a65; display: flex; justify-content: space-between; align-items: center; }
  .header h1 { font-size: 1.3rem; color: #F0A500; }
  .container { max-width: 960px; margin: 0 auto; padding: 24px; }
  .panel { background: #162b40; border: 1px solid #2a4a65; border-radius: 14px; padding: 20px; margin-bottom: 20px; }
  label { display: block; color: #a0b4c8; font-size: 0.82rem; margin-bottom: 6px; }
  input, textarea { width: 100%; background: #0d1b2a; border: 1px solid #2a4a65; color: #fff; padding: 10px 14px; border-radius: 8px; font-size: 0.9rem; }
  textarea { min-height: 180px; resize: vertical; }
  .row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 14px; }
  .form-group { margin-bottom: 14px; }
  .btn { background: #F0A500; color: #0a2342; border: none; padding: 12px 28px; border-radius: 24px; font-weight: 700; cursor: pointer; font-size: 0.95rem; }
  .btn:disabled { opacity: 0.4; cursor: not-allowed; }
  .btn-outline { background: none; border: 1px solid #2a4a65; color: #a0b4c8; padding: 6px 14px; border-radius: 8px; cursor: pointer; font-size: 0.8rem; margin-right: 6px; }
  .result { background: #0d1b2a; border: 1px solid #2a4a65; border-radius: 10px; padding: 16px; min-height: 120px; white-space: pre-wrap; font-size: 0.88rem; line-height: 1.7; color: #d0e4f0; }
  .history-item { background: #0d1b2a; border: 1px solid #2a4a65; border-radius: 10px; padding: 14px; margin-bottom: 10px; }
  .history-meta { color: #5c7a8f; font-size: 0.78rem; margin-bottom: 6px; }
  .history-title { color: #F0A500; font-size: 0.95rem; font-weight: 600; margin-bottom: 4px; }
  .history-preview { color: #a0b4c8; font-size: 0.82rem; line-height: 1.5; }
  .status { padding: 8px 14px; border-radius: 8px; font-size: 0.85rem; margin-bottom: 14px; display: none; }
  .status.loading { background: #1e3a52; color: #a0b4c8; display: block; }
  .status.error { background: #3d1515; color: #e57373; display: block; }
  h2 { color: #F0A500; font-size: 1rem; margin-bottom: 14px; }
  .api-warn { background: #3d2a00; color: #ffb74d; border: 1px solid #5c3d00; border-radius: 8px; padding: 10px 14px; font-size: 0.83rem; margin-bottom: 16px; }
  .copy-btn { float: right; }
  .tab-row { display: flex; gap: 8px; margin-bottom: 20px; }
  .tab { padding: 8px 20px; border-radius: 20px; cursor: pointer; font-size: 0.88rem; border: 1px solid #2a4a65; color: #a0b4c8; background: none; }
  .tab.active { background: #F0A500; color: #0a2342; border-color: #F0A500; font-weight: 700; }
  .section { display: none; }
  .section.active { display: block; }
</style>
</head>
<body>
<div class="header">
  <h1>📝 Emport AI — AI議事録ツール</h1>
</div>
<div class="container">
  <div class="tab-row">
    <button class="tab active" onclick="switchTab('create')">新規作成</button>
    <button class="tab" onclick="switchTab('history')">履歴</button>
    <button class="tab" onclick="switchTab('settings')">設定</button>
  </div>

  <!-- 新規作成 -->
  <div class="section active" id="tab-create">
    {% if not api_key %}
    <div class="api-warn">⚠️ APIキーが設定されていません。「設定」タブからClaude APIキーを入力してください。</div>
    {% endif %}
    <div class="panel">
      <h2>会議情報</h2>
      <div class="row">
        <div class="form-group">
          <label>会議タイトル</label>
          <input type="text" id="title" placeholder="例：5月経営会議">
        </div>
        <div class="form-group">
          <label>参加者</label>
          <input type="text" id="attendees" placeholder="例：山田社長、鈴木部長、田中">
        </div>
      </div>
      <div class="row">
        <div class="form-group">
          <label>開催日</label>
          <input type="date" id="date" value="{{ today }}">
        </div>
        <div class="form-group">
          <label>場所・形式</label>
          <input type="text" id="location" placeholder="例：本社会議室 / Zoom">
        </div>
      </div>
      <div class="form-group">
        <label>会議内容・文字起こし（そのまま貼り付けOK）</label>
        <textarea id="content" placeholder="会議の内容、メモ、文字起こしなどを貼り付けてください...

例：
・Q2売上は前年比115%で目標達成
・新サービスの価格を月額3万円に設定することを決定
・来月から田中がSNS担当を兼務する
・次回会議は6月10日を予定"></textarea>
      </div>
      <div id="status" class="status"></div>
      <button class="btn" id="generateBtn" onclick="generate()" {% if not api_key %}disabled{% endif %}>
        ✨ AI議事録を生成
      </button>
    </div>

    <div class="panel" id="resultPanel" style="display:none">
      <h2>生成された議事録 <button class="btn-outline copy-btn" onclick="copyResult()">📋 コピー</button></h2>
      <div class="result" id="result"></div>
      <div style="margin-top:14px">
        <button class="btn-outline" onclick="saveMinutes()">💾 保存する</button>
      </div>
    </div>
  </div>

  <!-- 履歴 -->
  <div class="section" id="tab-history">
    <div class="panel">
      <h2>保存済み議事録</h2>
      {% if minutes %}
        {% for m in minutes | sort(attribute='created_at', reverse=True) %}
        <div class="history-item">
          <div class="history-meta">{{ m.date }} | {{ m.attendees }} | {{ m.location }}</div>
          <div class="history-title">{{ m.title }}</div>
          <div class="history-preview">{{ m.result[:200] }}...</div>
          <div style="margin-top:8px">
            <button class="btn-outline" onclick="viewMinute('{{ m.id }}')">詳細を見る</button>
            <button class="btn-outline" style="color:#e57373;border-color:#e5737344" onclick="deleteMinute('{{ m.id }}')">削除</button>
          </div>
        </div>
        {% endfor %}
      {% else %}
        <p style="color:#5c7a8f;font-size:0.9rem">まだ保存された議事録がありません。</p>
      {% endif %}
    </div>
  </div>

  <!-- 設定 -->
  <div class="section" id="tab-settings">
    <div class="panel">
      <h2>APIキー設定</h2>
      <div class="form-group">
        <label>Claude APIキー（Anthropic）</label>
        <input type="password" id="apiKeyInput" placeholder="sk-ant-..." value="{{ api_key }}">
      </div>
      <button class="btn" onclick="saveApiKey()">保存</button>
    </div>
  </div>
</div>

<!-- 詳細モーダル -->
<div id="detailModal" style="display:none;position:fixed;inset:0;background:#000a;z-index:100;align-items:center;justify-content:center;display:none">
  <div style="background:#162b40;border:1px solid #2a4a65;border-radius:16px;padding:24px;width:720px;max-width:95vw;max-height:90vh;overflow-y:auto">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h2 id="detailTitle" style="color:#F0A500"></h2>
      <button class="btn-outline" onclick="closeDetail()">✕ 閉じる</button>
    </div>
    <div class="result" id="detailContent"></div>
  </div>
</div>

<script>
const allMinutes = {{ minutes_json | safe }};

function switchTab(tab) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById('tab-' + tab).classList.add('active');
}

async function generate() {
  const title = document.getElementById('title').value || '無題の会議';
  const content = document.getElementById('content').value.trim();
  if (!content) { alert('会議内容を入力してください'); return; }

  const btn = document.getElementById('generateBtn');
  const status = document.getElementById('status');
  btn.disabled = true;
  status.className = 'status loading';
  status.textContent = '⏳ AIが議事録を生成しています... (10〜20秒)';

  try {
    const resp = await fetch('/generate', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        title,
        attendees: document.getElementById('attendees').value,
        date: document.getElementById('date').value,
        location: document.getElementById('location').value,
        content,
      })
    });
    const data = await resp.json();
    if (data.error) throw new Error(data.error);
    document.getElementById('result').textContent = data.result;
    document.getElementById('resultPanel').style.display = 'block';
    status.style.display = 'none';
    window._lastResult = data;
  } catch(e) {
    status.className = 'status error';
    status.textContent = '❌ エラー: ' + e.message;
  } finally {
    btn.disabled = false;
  }
}

function copyResult() {
  navigator.clipboard.writeText(document.getElementById('result').textContent);
  alert('コピーしました！');
}

async function saveMinutes() {
  if (!window._lastResult) return;
  await fetch('/save_minute', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(window._lastResult)
  });
  alert('保存しました！');
  location.reload();
}

function viewMinute(id) {
  const m = allMinutes.find(x => x.id === id);
  if (!m) return;
  document.getElementById('detailTitle').textContent = m.title;
  document.getElementById('detailContent').textContent = m.result;
  document.getElementById('detailModal').style.display = 'flex';
}

function closeDetail() {
  document.getElementById('detailModal').style.display = 'none';
}

async function deleteMinute(id) {
  if (!confirm('削除しますか？')) return;
  await fetch('/delete_minute', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({id})
  });
  location.reload();
}

async function saveApiKey() {
  const key = document.getElementById('apiKeyInput').value.trim();
  await fetch('/save_api_key', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({key})
  });
  alert('APIキーを保存しました。');
  location.reload();
}
</script>
</body>
</html>
"""

API_KEY_FILE = os.path.join(os.path.dirname(__file__), ".api_key")


def get_api_key():
    env_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if env_key:
        return env_key
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE) as f:
            return f.read().strip()
    return ""


@app.route("/")
def index():
    minutes = load_minutes()
    api_key = get_api_key()
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template_string(
        HTML,
        minutes=minutes,
        minutes_json=json.dumps(minutes, ensure_ascii=False),
        api_key=api_key,
        today=today,
    )


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "APIキーが設定されていません"}), 400

    content = data.get("content", "")
    header = f"【タイトル】{data.get('title','')}\n【日時】{data.get('date','')}\n【参加者】{data.get('attendees','')}\n【場所】{data.get('location','')}\n\n【会議内容】\n{content}"

    try:
        result = call_claude(header, api_key)
        return jsonify({
            "id": str(int(datetime.now().timestamp() * 1000)),
            "title": data.get("title", "無題"),
            "date": data.get("date", ""),
            "attendees": data.get("attendees", ""),
            "location": data.get("location", ""),
            "content": content,
            "result": result,
            "created_at": datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/save_minute", methods=["POST"])
def save_minute():
    data = request.get_json()
    minutes = load_minutes()
    minutes.append(data)
    save_minutes(minutes)
    return jsonify({"ok": True})


@app.route("/delete_minute", methods=["POST"])
def delete_minute():
    data = request.get_json()
    minutes = load_minutes()
    minutes = [m for m in minutes if m["id"] != data.get("id")]
    save_minutes(minutes)
    return jsonify({"ok": True})


@app.route("/save_api_key", methods=["POST"])
def save_api_key():
    data = request.get_json()
    key = data.get("key", "").strip()
    with open(API_KEY_FILE, "w") as f:
        f.write(key)
    return jsonify({"ok": True})


if __name__ == "__main__":
    print("Emport AI 議事録ツール起動中... http://localhost:5002")
    app.run(host="0.0.0.0", port=5002, debug=False)
