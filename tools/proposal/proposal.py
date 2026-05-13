#!/usr/bin/env python3
"""
Emport AI 提案書自動生成ツール
見込み客の情報を入力 → AIがカスタム提案書を生成 → PDF出力
起動: python proposal.py
アクセス: http://localhost:5003
"""

import json
import os
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, make_response
import urllib.request
import urllib.error

app = Flask(__name__)
PROPOSALS_FILE = os.path.join(os.path.dirname(__file__), "proposals_data.json")
API_KEY_FILE = os.path.join(os.path.dirname(__file__), ".api_key")

SYSTEM_PROMPT = """あなたはEmport AIの営業担当として、見込み客向けの提案書を作成する専門家です。
以下の情報をもとに、説得力のある営業提案書をMarkdown形式で作成してください。

提案書の構成:
1. **御社の現状認識** — 入力された課題を共感を持って言語化
2. **Emport AIが解決できること** — 具体的な解決策を3つ
3. **導入後のイメージ** — Before/Afterで具体的に
4. **料金プラン** — 推奨プランとその根拠
5. **次のステップ** — 具体的なアクション（無料体験の案内など）
6. **よくある質問** — 業種に合わせた2〜3個のQ&A

トーン: 押し売りにならず、共感ファーストで。具体的な数字を入れる。
"""

INDUSTRIES_SAMPLE = {
    "飲食業": "客数・リピート率改善、Googleマップ口コミ管理、メニュー改善、スタッフ採用",
    "建設・工務店": "見積作業の効率化、採用、請求書管理、補助金活用",
    "美容・サロン": "SNS集客、リピーター獲得、スタッフ教育、予約管理",
    "小売業": "在庫管理、集客、EC展開、仕入れ交渉",
    "製造業": "生産効率化、DX推進、補助金活用、採用難",
    "医療・介護": "スタッフ確保、業務効率化、患者/利用者満足度",
    "士業・コンサル": "営業・集客、単価アップ、業務効率化",
    "その他サービス業": "集客、業務効率化、採用、コスト削減",
}


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
        "max_tokens": 3000,
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


def load_proposals():
    if not os.path.exists(PROPOSALS_FILE):
        return []
    with open(PROPOSALS_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_proposals(data):
    with open(PROPOSALS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Emport AI — 提案書生成ツール</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0d1b2a; color: #fff; font-family: -apple-system, sans-serif; }
  .header { background: #0a2342; padding: 16px 24px; border-bottom: 1px solid #2a4a65; display: flex; justify-content: space-between; align-items: center; }
  .header h1 { font-size: 1.3rem; color: #F0A500; }
  .container { max-width: 1100px; margin: 0 auto; padding: 24px; display: grid; grid-template-columns: 380px 1fr; gap: 20px; }
  @media(max-width:760px){ .container{grid-template-columns:1fr;padding:12px;} }
  .panel { background: #162b40; border: 1px solid #2a4a65; border-radius: 14px; padding: 20px; }
  label { display: block; color: #a0b4c8; font-size: 0.82rem; margin-bottom: 5px; margin-top: 12px; }
  input, select, textarea { width: 100%; background: #0d1b2a; border: 1px solid #2a4a65; color: #fff; padding: 10px 12px; border-radius: 8px; font-size: 0.9rem; }
  textarea { min-height: 100px; resize: vertical; }
  select option { background: #0d1b2a; }
  .btn { background: #F0A500; color: #0a2342; border: none; padding: 12px; border-radius: 10px; font-weight: 700; cursor: pointer; font-size: 0.95rem; width: 100%; margin-top: 16px; }
  .btn:disabled { opacity: 0.4; cursor: not-allowed; }
  .btn-sm { background: none; border: 1px solid #2a4a65; color: #a0b4c8; padding: 6px 14px; border-radius: 8px; cursor: pointer; font-size: 0.8rem; margin-right: 6px; margin-top: 8px; }
  .btn-sm.primary { border-color: #F0A500; color: #F0A500; }
  h2 { color: #F0A500; font-size: 1rem; margin-bottom: 14px; }
  h3 { color: #F0A500; font-size: 0.95rem; margin-bottom: 10px; }
  .result-area { min-height: 400px; background: #0d1b2a; border: 1px solid #2a4a65; border-radius: 10px; padding: 20px; }
  .result-area h2, .result-area h3 { color: #FFD166; }
  .result-area strong { color: #F0A500; }
  .result-area p { margin: 8px 0; line-height: 1.7; color: #d0e4f0; font-size: 0.9rem; }
  .result-area ul, .result-area ol { margin-left: 20px; margin-bottom: 10px; }
  .result-area li { color: #c0d4e8; font-size: 0.9rem; line-height: 1.8; }
  .result-area table { border-collapse: collapse; width: 100%; margin: 10px 0; }
  .result-area th, .result-area td { border: 1px solid #2a4a65; padding: 8px 12px; font-size: 0.85rem; }
  .result-area th { background: #162b40; color: #F0A500; }
  .status { padding: 10px 14px; border-radius: 8px; font-size: 0.85rem; margin-bottom: 14px; display: none; }
  .status.loading { background: #1e3a52; color: #a0b4c8; display: block; }
  .status.error { background: #3d1515; color: #e57373; display: block; }
  .history-list { margin-top: 16px; }
  .history-item { background: #0d1b2a; border: 1px solid #2a4a65; border-radius: 8px; padding: 10px; margin-bottom: 8px; cursor: pointer; }
  .history-item:hover { border-color: #F0A500; }
  .history-name { color: #F0A500; font-size: 0.88rem; font-weight: 600; }
  .history-meta { color: #5c7a8f; font-size: 0.75rem; margin-top: 3px; }
  .empty { color: #5c7a8f; font-size: 0.85rem; text-align: center; padding: 30px 0; }
  .api-warn { background: #3d2a00; color: #ffb74d; border: 1px solid #5c3d00; border-radius: 8px; padding: 8px 12px; font-size: 0.8rem; margin-bottom: 12px; }
  .tips { background: #0a2342; border-radius: 8px; padding: 10px 14px; margin-top: 10px; }
  .tips li { color: #a0b4c8; font-size: 0.8rem; line-height: 1.8; }
  .print-header { display: none; }
  @media print {
    body { background: #fff; color: #000; }
    .header, .container > .panel:first-child, .btn, .btn-sm, .status { display: none !important; }
    .container { grid-template-columns: 1fr; padding: 0; }
    .result-area { border: none; background: #fff; padding: 0; }
    .result-area h2, .result-area h3 { color: #0a2342; }
    .result-area strong { color: #0a2342; }
    .result-area p, .result-area li { color: #333; }
    .result-area th { background: #eee; color: #000; }
    .result-area td { color: #333; }
    .print-header { display: block; }
  }
</style>
</head>
<body>
<div class="header">
  <h1>📄 Emport AI — 提案書生成ツール</h1>
</div>
<div class="container">
  <!-- 左: 入力パネル -->
  <div>
    <div class="panel">
      <h2>見込み客情報</h2>
      {% if not api_key %}
      <div class="api-warn">⚠️ APIキー未設定。下部の設定欄から入力してください。</div>
      {% endif %}

      <label>会社名・屋号 *</label>
      <input type="text" id="company" placeholder="山田建設 株式会社">

      <label>担当者名</label>
      <input type="text" id="contact" placeholder="山田 太郎">

      <label>業種 *</label>
      <select id="industry">
        {% for ind in industries %}
        <option value="{{ ind }}">{{ ind }}</option>
        {% endfor %}
      </select>

      <label>従業員数</label>
      <select id="employees">
        <option>1〜5名</option>
        <option>6〜20名</option>
        <option>21〜50名</option>
        <option>50名以上</option>
      </select>

      <label>主な課題・悩み（自由記述）</label>
      <textarea id="issues" placeholder="例：売上が前年比で落ちている。SNSの集客がうまくいかない。採用が難しい。補助金を使いたいが何から始めればよいか分からない。"></textarea>

      <label>現在使っているツール・サービス</label>
      <input type="text" id="current_tools" placeholder="例：freee、LINE公式アカウント、Excel">

      <label>予算感</label>
      <select id="budget">
        <option>〜月1万円</option>
        <option>〜月3万円</option>
        <option>〜月5万円</option>
        <option>月5万円以上</option>
        <option>未定</option>
      </select>

      <div id="status" class="status"></div>
      <button class="btn" id="genBtn" onclick="generateProposal()" {% if not api_key %}disabled{% endif %}>
        ✨ 提案書を生成する
      </button>

      <div class="tips">
        <ul>
          <li>課題を具体的に書くほど精度が上がります</li>
          <li>生成後はコピーしてWordやNotionに貼り付け可能</li>
          <li>印刷ボタンでそのままPDF保存も可</li>
        </ul>
      </div>
    </div>

    <div class="panel" style="margin-top:16px">
      <h3>過去の提案書</h3>
      <div class="history-list" id="historyList">
        {% if proposals %}
          {% for p in proposals | sort(attribute='created_at', reverse=True) | list %}
          <div class="history-item" onclick="loadProposal('{{ p.id }}')">
            <div class="history-name">{{ p.company }}</div>
            <div class="history-meta">{{ p.industry }} | {{ p.created_at[:10] }}</div>
          </div>
          {% endfor %}
        {% else %}
          <div class="empty">まだ提案書がありません</div>
        {% endif %}
      </div>
    </div>

    <div class="panel" style="margin-top:16px">
      <h3>⚙️ APIキー設定</h3>
      <input type="password" id="apiKey" placeholder="sk-ant-..." value="{{ api_key }}">
      <button class="btn-sm primary" onclick="saveKey()" style="margin-top:10px">保存</button>
    </div>
  </div>

  <!-- 右: 結果パネル -->
  <div>
    <div class="panel" style="min-height:600px">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
        <h2 id="resultTitle">提案書プレビュー</h2>
        <div>
          <button class="btn-sm" onclick="copyResult()">📋 コピー</button>
          <button class="btn-sm" onclick="window.print()">🖨️ 印刷/PDF</button>
          <button class="btn-sm" onclick="saveProposal()">💾 保存</button>
        </div>
      </div>

      <!-- 印刷用ヘッダー -->
      <div class="print-header">
        <h1 style="color:#0a2342;font-size:1.5rem;margin-bottom:8px">Emport AI 導入提案書</h1>
        <p style="color:#666;font-size:0.85rem">作成日: {{ today }} | Emport AI 株式会社</p>
        <hr style="margin:12px 0;border-color:#ddd">
      </div>

      <div class="result-area" id="resultArea">
        <p style="color:#5c7a8f;text-align:center;padding-top:60px">
          左側のフォームに見込み客情報を入力して<br>「提案書を生成する」ボタンを押してください
        </p>
      </div>
    </div>
  </div>
</div>

<script>
const allProposals = {{ proposals_json | safe }};
let currentResult = null;

async function generateProposal() {
  const company = document.getElementById('company').value.trim();
  const industry = document.getElementById('industry').value;
  const issues = document.getElementById('issues').value.trim();

  if (!company) { alert('会社名を入力してください'); return; }
  if (!issues) { alert('課題・悩みを入力してください'); return; }

  const btn = document.getElementById('genBtn');
  const status = document.getElementById('status');
  btn.disabled = true;
  status.className = 'status loading';
  status.textContent = '⏳ AIが提案書を生成しています... (15〜25秒)';

  try {
    const payload = {
      company,
      contact: document.getElementById('contact').value,
      industry,
      employees: document.getElementById('employees').value,
      issues,
      current_tools: document.getElementById('current_tools').value,
      budget: document.getElementById('budget').value,
    };

    const resp = await fetch('/generate_proposal', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await resp.json();
    if (data.error) throw new Error(data.error);

    currentResult = data;
    document.getElementById('resultTitle').textContent = company + ' 様 向け提案書';
    document.getElementById('resultArea').innerHTML = markdownToHtml(data.result);
    status.style.display = 'none';
  } catch(e) {
    status.className = 'status error';
    status.textContent = '❌ エラー: ' + e.message;
  } finally {
    btn.disabled = false;
  }
}

function markdownToHtml(md) {
  return md
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h2>$1</h2>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/^\| (.+)$/gm, (_, row) => {
      if (row.includes('---')) return '';
      const cells = row.split('|').map(c => c.trim());
      return '<tr>' + cells.map((c, i) => i === 0 ? `<th>${c}</th>` : `<td>${c}</td>`).join('') + '</tr>';
    })
    .replace(/(<tr>.*<\/tr>\n)+/g, m => `<table>${m}</table>`)
    .replace(/^[-*] (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n)+/g, m => `<ul>${m}</ul>`)
    .replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/^(?!<[hultpd])/gm, '')
    .replace(/(<\/h[23]>|<\/ul>|<\/table>)(?!\n)/g, '$1\n')
}

function copyResult() {
  const text = document.getElementById('resultArea').innerText;
  navigator.clipboard.writeText(text);
  alert('コピーしました！');
}

async function saveProposal() {
  if (!currentResult) { alert('まず提案書を生成してください'); return; }
  const resp = await fetch('/save_proposal', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(currentResult)
  });
  const data = await resp.json();
  if (data.ok) { alert('保存しました！'); location.reload(); }
}

function loadProposal(id) {
  const p = allProposals.find(x => x.id === id);
  if (!p) return;
  document.getElementById('resultTitle').textContent = p.company + ' 様 向け提案書';
  document.getElementById('resultArea').innerHTML = markdownToHtml(p.result);
  currentResult = p;
}

async function saveKey() {
  const key = document.getElementById('apiKey').value.trim();
  await fetch('/save_key', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({key})
  });
  alert('保存しました。ページを再読み込みします。');
  location.reload();
}
</script>
</body>
</html>
"""


@app.route("/")
def index():
    proposals = load_proposals()
    api_key = get_api_key()
    today = datetime.now().strftime("%Y年%m月%d日")
    return render_template_string(
        HTML,
        proposals=proposals,
        proposals_json=json.dumps(proposals, ensure_ascii=False),
        api_key=api_key,
        today=today,
        industries=list(INDUSTRIES_SAMPLE.keys()),
    )


@app.route("/generate_proposal", methods=["POST"])
def generate_proposal():
    data = request.get_json()
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "APIキーが設定されていません"}), 400

    industry = data.get("industry", "")
    issues = data.get("issues", "")
    company = data.get("company", "")
    employees = data.get("employees", "")
    budget = data.get("budget", "")
    current_tools = data.get("current_tools", "")

    industry_hint = INDUSTRIES_SAMPLE.get(industry, "")
    prompt = f"""以下の見込み客向けの提案書を作成してください:

【会社名】{company}
【業種】{industry}（よくある課題例: {industry_hint}）
【従業員数】{employees}
【主な課題・悩み】{issues}
【現在使用中のツール】{current_tools}
【予算感】{budget}

Emport AIのサービス内容:
- Claude AIを使ったビジネス相談（24時間対応）
- 補助金診断・申請サポート
- 業務効率化コンサル
- 月額9,800円（初月無料）〜

上記の情報をもとに、この会社に響く提案書をMarkdownで作成してください。"""

    try:
        result = call_claude(prompt, api_key)
        return jsonify({
            "id": str(int(datetime.now().timestamp() * 1000)),
            "company": company,
            "industry": industry,
            "issues": issues,
            "result": result,
            "created_at": datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/save_proposal", methods=["POST"])
def save_proposal():
    data = request.get_json()
    proposals = load_proposals()
    if not any(p["id"] == data["id"] for p in proposals):
        proposals.append(data)
        save_proposals(proposals)
    return jsonify({"ok": True})


@app.route("/save_key", methods=["POST"])
def save_key():
    data = request.get_json()
    with open(API_KEY_FILE, "w") as f:
        f.write(data.get("key", ""))
    return jsonify({"ok": True})


if __name__ == "__main__":
    print("Emport AI 提案書生成ツール起動中... http://localhost:5003")
    app.run(host="0.0.0.0", port=5003, debug=False)
