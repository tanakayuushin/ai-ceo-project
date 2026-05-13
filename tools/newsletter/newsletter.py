#!/usr/bin/env python3
"""
Emport AI メールマガジン生成ツール
AIがニュースレターを生成 → HTMLでコピー → メール配信ツールに貼り付け
起動: python newsletter.py
アクセス: http://localhost:5004
"""

import json
import os
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify
import urllib.request

app = Flask(__name__)
NL_FILE = os.path.join(os.path.dirname(__file__), "newsletters.json")
API_KEY_FILE = os.path.join(os.path.dirname(__file__), ".api_key")

SYSTEM_PROMPT = """あなたはEmport AIのメールマガジン編集者です。
中小企業オーナー向けのメールニュースレターを作成してください。

ニュースレターの構成:
1. **今月のひとこと**（オーナーへの共感メッセージ、2〜3文）
2. **今月のAI活用ヒント**（具体的なビジネス活用例、1つ）
3. **補助金・助成金 最新情報**（旬の補助金情報、1〜2件）
4. **経営Q&A**（よくある質問に答える形式）
5. **今月のアクションチェックリスト**（3項目）

トーン: 友人のような親しみやすさ。押し売り不要。具体的で実践的。
HTMLメール向けに読みやすく整形してください。"""


def get_api_key():
    env_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if env_key:
        return env_key
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE) as f:
            return f.read().strip()
    return ""


def call_claude(prompt: str, api_key: str) -> str:
    url = "https://api.anthropic.com/v1/messages"
    payload = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 2000,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("x-api-key", api_key)
    req.add_header("anthropic-version", "2023-06-01")
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        return data["content"][0]["text"]


def load_nl():
    if not os.path.exists(NL_FILE):
        return []
    with open(NL_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_nl(data):
    with open(NL_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Emport AI — メールマガジンツール</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0d1b2a; color: #fff; font-family: -apple-system, sans-serif; }
  .header { background: #0a2342; padding: 16px 24px; border-bottom: 1px solid #2a4a65; }
  .header h1 { font-size: 1.3rem; color: #F0A500; }
  .container { max-width: 1100px; margin: 0 auto; padding: 24px; display: grid; grid-template-columns: 340px 1fr; gap: 20px; }
  @media(max-width:760px){ .container{grid-template-columns:1fr;} }
  .panel { background: #162b40; border: 1px solid #2a4a65; border-radius: 14px; padding: 20px; margin-bottom: 16px; }
  label { display: block; color: #a0b4c8; font-size: 0.82rem; margin-bottom: 5px; margin-top: 12px; }
  input, select, textarea { width: 100%; background: #0d1b2a; border: 1px solid #2a4a65; color: #fff; padding: 10px 12px; border-radius: 8px; font-size: 0.9rem; }
  textarea { min-height: 80px; resize: vertical; }
  .btn { background: #F0A500; color: #0a2342; border: none; padding: 12px; border-radius: 10px; font-weight: 700; cursor: pointer; font-size: 0.95rem; width: 100%; margin-top: 14px; }
  .btn:disabled { opacity: 0.4; cursor: not-allowed; }
  .btn-sm { background: none; border: 1px solid #2a4a65; color: #a0b4c8; padding: 6px 14px; border-radius: 8px; cursor: pointer; font-size: 0.8rem; margin-right: 6px; }
  h2 { color: #F0A500; font-size: 1rem; margin-bottom: 12px; }
  .status { padding: 10px 14px; border-radius: 8px; font-size: 0.85rem; margin-bottom: 12px; display: none; }
  .status.loading { background: #1e3a52; color: #a0b4c8; display: block; }
  .status.error { background: #3d1515; color: #e57373; display: block; }
  .preview-frame { background: #fff; border-radius: 10px; padding: 0; overflow: hidden; }
  iframe { width: 100%; height: 700px; border: none; }
  .history-item { background: #0d1b2a; border: 1px solid #2a4a65; border-radius: 8px; padding: 10px; margin-bottom: 8px; cursor: pointer; }
  .history-item:hover { border-color: #F0A500; }
  .history-name { color: #F0A500; font-size: 0.88rem; font-weight: 600; }
  .history-meta { color: #5c7a8f; font-size: 0.75rem; margin-top: 3px; }
  .empty { color: #5c7a8f; font-size: 0.85rem; text-align: center; padding: 20px 0; }
  .copy-area { background: #0d1b2a; border: 1px solid #2a4a65; border-radius: 8px; padding: 12px; font-size: 0.78rem; color: #a0b4c8; max-height: 200px; overflow-y: auto; white-space: pre-wrap; word-break: break-all; margin-top: 12px; }
</style>
</head>
<body>
<div class="header">
  <h1>📧 Emport AI — メールマガジンツール</h1>
</div>
<div class="container">
  <div>
    <div class="panel">
      <h2>ニュースレター設定</h2>
      {% if not api_key %}
      <div style="background:#3d2a00;color:#ffb74d;border-radius:8px;padding:8px 12px;font-size:0.8rem;margin-bottom:12px">
        ⚠️ APIキー未設定
      </div>
      {% endif %}

      <label>号数・タイトル</label>
      <input type="text" id="title" placeholder="例：Emport AI通信 Vol.3 — 補助金特集号">

      <label>ターゲット読者</label>
      <select id="target">
        <option>全業種の中小企業オーナー</option>
        <option>飲食業オーナー</option>
        <option>建設・工務店オーナー</option>
        <option>美容サロンオーナー</option>
        <option>小売業オーナー</option>
        <option>製造業オーナー</option>
      </select>

      <label>今月の重点テーマ</label>
      <select id="theme">
        <option>補助金・助成金活用</option>
        <option>AI・DX推進</option>
        <option>SNS集客</option>
        <option>採用・人材</option>
        <option>資金繰り・財務</option>
        <option>売上アップ戦略</option>
        <option>生産性向上</option>
      </select>

      <label>特記事項・追加したいトピック（任意）</label>
      <textarea id="extra" placeholder="例：今月から補助金の申請受付が始まったこと、うちのサービスの新機能など"></textarea>

      <div id="status" class="status"></div>
      <button class="btn" id="genBtn" onclick="generate()" {% if not api_key %}disabled{% endif %}>
        ✨ メールマガジンを生成
      </button>
    </div>

    <div class="panel">
      <h2>過去のニュースレター</h2>
      {% if newsletters %}
        {% for n in newsletters | sort(attribute='created_at', reverse=True) | list %}
        <div class="history-item" onclick="loadNl('{{ n.id }}')">
          <div class="history-name">{{ n.title }}</div>
          <div class="history-meta">{{ n.target }} | {{ n.created_at[:10] }}</div>
        </div>
        {% endfor %}
      {% else %}
        <div class="empty">まだ生成したニュースレターがありません</div>
      {% endif %}
    </div>

    <div class="panel">
      <h2>⚙️ APIキー</h2>
      <input type="password" id="apiKey" value="{{ api_key }}" placeholder="sk-ant-...">
      <button class="btn-sm" onclick="saveKey()" style="margin-top:10px">保存</button>
    </div>
  </div>

  <div>
    <div class="panel" style="min-height:500px">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
        <h2 id="previewTitle">プレビュー</h2>
        <div>
          <button class="btn-sm" onclick="copyHtml()">📋 HTMLコピー</button>
          <button class="btn-sm" onclick="copyText()">📝 テキストコピー</button>
          <button class="btn-sm" onclick="saveNl()">💾 保存</button>
        </div>
      </div>
      <div class="preview-frame">
        <iframe id="previewFrame" srcdoc="<p style='color:#999;padding:40px;text-align:center'>ニュースレターを生成するとここにプレビューが表示されます</p>"></iframe>
      </div>
      <div id="htmlArea" class="copy-area" style="display:none"></div>
    </div>
  </div>
</div>

<script>
const allNl = {{ nl_json | safe }};
let currentNl = null;

async function generate() {
  const title = document.getElementById('title').value || 'Emport AI通信';
  const btn = document.getElementById('genBtn');
  const status = document.getElementById('status');
  btn.disabled = true;
  status.className = 'status loading';
  status.textContent = '⏳ AIがニュースレターを生成しています... (15〜20秒)';

  try {
    const resp = await fetch('/generate_nl', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        title,
        target: document.getElementById('target').value,
        theme: document.getElementById('theme').value,
        extra: document.getElementById('extra').value,
      })
    });
    const data = await resp.json();
    if (data.error) throw new Error(data.error);

    currentNl = data;
    document.getElementById('previewTitle').textContent = title;
    document.getElementById('previewFrame').srcdoc = data.html;
    document.getElementById('htmlArea').textContent = data.html;
    status.style.display = 'none';
  } catch(e) {
    status.className = 'status error';
    status.textContent = '❌ ' + e.message;
  } finally {
    btn.disabled = false;
  }
}

function copyHtml() {
  if (!currentNl) { alert('先に生成してください'); return; }
  navigator.clipboard.writeText(currentNl.html);
  alert('HTMLをコピーしました！ メール配信ツールのHTML入力欄に貼り付けてください。');
}

function copyText() {
  if (!currentNl) return;
  const tmp = document.createElement('div');
  tmp.innerHTML = currentNl.html;
  navigator.clipboard.writeText(tmp.innerText);
  alert('テキストをコピーしました！');
}

async function saveNl() {
  if (!currentNl) { alert('先に生成してください'); return; }
  await fetch('/save_nl', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(currentNl)
  });
  alert('保存しました！');
  location.reload();
}

function loadNl(id) {
  const n = allNl.find(x => x.id === id);
  if (!n) return;
  currentNl = n;
  document.getElementById('previewTitle').textContent = n.title;
  document.getElementById('previewFrame').srcdoc = n.html;
}

async function saveKey() {
  const key = document.getElementById('apiKey').value.trim();
  await fetch('/save_key', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({key})
  });
  alert('保存しました。');
  location.reload();
}
</script>
</body>
</html>
"""


def markdown_to_email_html(text: str, title: str) -> str:
    """MarkdownをHTMLメール形式に変換"""
    lines = text.split('\n')
    html_parts = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('## '):
            html_parts.append(f'<h2 style="color:#0A2342;font-size:1.1rem;font-weight:700;padding:12px 0 6px;border-bottom:2px solid #F0A500;margin-top:20px">{line[3:]}</h2>')
        elif line.startswith('# '):
            html_parts.append(f'<h1 style="color:#0A2342;font-size:1.3rem;font-weight:900">{line[2:]}</h1>')
        elif line.startswith('**') and line.endswith('**'):
            html_parts.append(f'<p style="font-weight:700;color:#0A2342;margin:8px 0">{line[2:-2]}</p>')
        elif line.startswith('- ') or line.startswith('・'):
            content = line[2:] if line.startswith('- ') else line[1:]
            html_parts.append(f'<li style="margin:6px 0;color:#333;line-height:1.7">{content}</li>')
        elif line.startswith('☑') or line.startswith('□'):
            html_parts.append(f'<li style="margin:8px 0;color:#333;line-height:1.7;list-style:none;padding-left:0">{line}</li>')
        else:
            line = line.replace('**', '').replace('*', '')
            html_parts.append(f'<p style="margin:8px 0;color:#333;line-height:1.8;font-size:0.95rem">{line}</p>')

    now = datetime.now().strftime('%Y年%m月号')
    body = '\n'.join(html_parts)
    return f"""<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="background:#f5f7fa;margin:0;padding:20px;font-family:'Hiragino Kaku Gothic ProN','Meiryo',sans-serif">
<div style="max-width:600px;margin:0 auto">
  <!-- ヘッダー -->
  <div style="background:#0A2342;padding:24px;border-radius:12px 12px 0 0;text-align:center">
    <div style="color:#F0A500;font-size:0.8rem;letter-spacing:2px;margin-bottom:6px">EMPORT AI</div>
    <h1 style="color:#fff;font-size:1.4rem;margin:0">{title}</h1>
    <div style="color:#A0B4C8;font-size:0.8rem;margin-top:6px">{now}</div>
  </div>
  <!-- 本文 -->
  <div style="background:#fff;padding:28px;border-radius:0 0 12px 12px;border:1px solid #e0e8f0;border-top:none">
    {body}
    <!-- フッター -->
    <div style="margin-top:32px;padding-top:20px;border-top:1px solid #e0e8f0;text-align:center">
      <a href="https://emport-ai.vercel.app/" style="display:inline-block;background:#F0A500;color:#0A2342;padding:12px 28px;border-radius:24px;font-weight:700;text-decoration:none;font-size:0.9rem">
        Emport AIを使ってみる
      </a>
      <p style="color:#999;font-size:0.75rem;margin-top:16px">
        Emport AI 株式会社<br>
        <a href="mailto:support@emport-ai.com" style="color:#999">support@emport-ai.com</a><br>
        <a href="#" style="color:#999">配信停止はこちら</a>
      </p>
    </div>
  </div>
</div>
</body></html>"""


@app.route("/")
def index():
    newsletters = load_nl()
    api_key = get_api_key()
    return render_template_string(
        HTML,
        newsletters=newsletters,
        nl_json=json.dumps(newsletters, ensure_ascii=False),
        api_key=api_key,
    )


@app.route("/generate_nl", methods=["POST"])
def generate_nl():
    data = request.get_json()
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "APIキーが設定されていません"}), 400

    now_str = datetime.now().strftime('%Y年%m月')
    prompt = f"""以下の条件で{now_str}号のメールニュースレターを作成してください:

タイトル: {data.get('title', 'Emport AI通信')}
ターゲット: {data.get('target', '中小企業オーナー')}
重点テーマ: {data.get('theme', 'AI活用')}
追加トピック: {data.get('extra', 'なし')}

Markdown形式で、読みやすく実践的な内容にしてください。"""

    try:
        result = call_claude(prompt, api_key)
        title = data.get('title', 'Emport AI通信')
        html = markdown_to_email_html(result, title)
        return jsonify({
            "id": str(int(datetime.now().timestamp() * 1000)),
            "title": title,
            "target": data.get("target", ""),
            "theme": data.get("theme", ""),
            "markdown": result,
            "html": html,
            "created_at": datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/save_nl", methods=["POST"])
def save_nl_route():
    data = request.get_json()
    nls = load_nl()
    if not any(n["id"] == data["id"] for n in nls):
        nls.append(data)
        save_nl(nls)
    return jsonify({"ok": True})


@app.route("/save_key", methods=["POST"])
def save_key():
    data = request.get_json()
    with open(API_KEY_FILE, "w") as f:
        f.write(data.get("key", ""))
    return jsonify({"ok": True})


if __name__ == "__main__":
    print("Emport AI メールマガジンツール起動中... http://localhost:5004")
    app.run(host="0.0.0.0", port=5004, debug=False)
