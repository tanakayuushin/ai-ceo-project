#!/usr/bin/env python3
"""
Emport AI 簡易CRM — 見込み客管理ツール
JSONファイルベースの軽量CRM。ブラウザで動作。

起動: python crm.py
アクセス: http://localhost:5001
"""

import json
import os
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, jsonify

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(__file__), "crm_data.json")

STAGES = ["新規", "初回接触", "提案中", "検討中", "成約", "失注"]
STAGE_COLORS = {
    "新規": "#607D8B",
    "初回接触": "#2196F3",
    "提案中": "#F0A500",
    "検討中": "#9C27B0",
    "成約": "#4CAF50",
    "失注": "#e57373",
}


def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Emport AI CRM</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0d1b2a; color: #fff; font-family: -apple-system, sans-serif; }
  .header { background: #0a2342; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #2a4a65; }
  .header h1 { font-size: 1.3rem; color: #F0A500; }
  .add-btn { background: #F0A500; color: #0a2342; border: none; padding: 8px 18px; border-radius: 20px; font-weight: 700; cursor: pointer; font-size: 0.9rem; }
  .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 24px; }
  .stat-card { background: #162b40; border: 1px solid #2a4a65; border-radius: 12px; padding: 14px; text-align: center; }
  .stat-num { font-size: 1.8rem; font-weight: 700; }
  .stat-label { color: #a0b4c8; font-size: 0.8rem; margin-top: 4px; }
  .search-bar { display: flex; gap: 10px; margin-bottom: 20px; }
  .search-bar input, .search-bar select { background: #162b40; border: 1px solid #2a4a65; color: #fff; padding: 10px 14px; border-radius: 8px; font-size: 0.9rem; flex: 1; }
  .table { width: 100%; border-collapse: collapse; }
  .table th { background: #0a2342; color: #a0b4c8; font-size: 0.8rem; padding: 10px 14px; text-align: left; font-weight: 600; }
  .table td { padding: 12px 14px; border-bottom: 1px solid #1e3a52; font-size: 0.9rem; }
  .table tr:hover td { background: #1e3a52; }
  .stage-badge { padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; }
  .action-btn { background: none; border: 1px solid #2a4a65; color: #a0b4c8; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.8rem; margin-right: 4px; }
  .action-btn:hover { background: #2a4a65; }
  .del-btn { color: #e57373; border-color: #e5737344; }
  .modal { display: none; position: fixed; inset: 0; background: #000a; z-index: 100; align-items: center; justify-content: center; }
  .modal.open { display: flex; }
  .modal-box { background: #162b40; border: 1px solid #2a4a65; border-radius: 16px; padding: 24px; width: 500px; max-width: 95vw; max-height: 90vh; overflow-y: auto; }
  .modal-box h2 { margin-bottom: 18px; color: #F0A500; }
  .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .form-group { margin-bottom: 14px; }
  label { display: block; color: #a0b4c8; font-size: 0.82rem; margin-bottom: 5px; }
  input, select, textarea { width: 100%; background: #0d1b2a; border: 1px solid #2a4a65; color: #fff; padding: 10px 12px; border-radius: 8px; font-size: 0.9rem; }
  textarea { min-height: 80px; resize: vertical; }
  .save-btn { background: #F0A500; color: #0a2342; border: none; padding: 10px 24px; border-radius: 8px; font-weight: 700; cursor: pointer; width: 100%; margin-top: 8px; font-size: 0.95rem; }
  .cancel-btn { background: none; border: 1px solid #2a4a65; color: #a0b4c8; padding: 10px 24px; border-radius: 8px; cursor: pointer; width: 100%; margin-top: 8px; }
  .note-text { color: #a0b4c8; font-size: 0.82rem; white-space: pre-wrap; }
</style>
</head>
<body>
<div class="header">
  <h1>Emport AI CRM — 見込み客管理</h1>
  <button class="add-btn" onclick="openAdd()">＋ 新規追加</button>
</div>
<div class="container">
  <!-- 統計 -->
  <div class="stats">
    {% for stage in stages %}
    <div class="stat-card">
      <div class="stat-num" style="color:{{ stage_colors[stage] }}">
        {{ leads | selectattr('stage','eq',stage) | list | length }}
      </div>
      <div class="stat-label">{{ stage }}</div>
    </div>
    {% endfor %}
  </div>

  <!-- 検索・フィルター -->
  <div class="search-bar">
    <input type="text" id="searchInput" placeholder="会社名・担当者で検索..." oninput="filterTable()">
    <select id="stageFilter" onchange="filterTable()">
      <option value="">全ステージ</option>
      {% for s in stages %}<option>{{ s }}</option>{% endfor %}
    </select>
  </div>

  <!-- テーブル -->
  <table class="table" id="leadsTable">
    <thead>
      <tr>
        <th>会社名</th><th>担当者</th><th>業種</th><th>ステージ</th>
        <th>次のアクション</th><th>期限</th><th>更新日</th><th>操作</th>
      </tr>
    </thead>
    <tbody>
      {% for lead in leads | sort(attribute='updated_at', reverse=True) %}
      <tr data-stage="{{ lead.stage }}" data-name="{{ lead.company }} {{ lead.contact }}">
        <td><strong>{{ lead.company }}</strong></td>
        <td>{{ lead.contact }}</td>
        <td style="color:#a0b4c8">{{ lead.industry }}</td>
        <td>
          <span class="stage-badge" style="background:{{ stage_colors.get(lead.stage,'#607D8B') }}22;color:{{ stage_colors.get(lead.stage,'#607D8B') }}">
            {{ lead.stage }}
          </span>
        </td>
        <td style="font-size:0.85rem">{{ lead.next_action or '—' }}</td>
        <td style="color:{{ '#e57373' if lead.due_date and lead.due_date < today else '#a0b4c8' }};font-size:0.85rem">
          {{ lead.due_date or '—' }}
        </td>
        <td style="color:#a0b4c8;font-size:0.82rem">{{ lead.updated_at[:10] }}</td>
        <td>
          <button class="action-btn" onclick="openEdit('{{ lead.id }}')">編集</button>
          <button class="action-btn del-btn" onclick="deleteLead('{{ lead.id }}')">削除</button>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>

<!-- モーダル -->
<div class="modal" id="modal">
  <div class="modal-box">
    <h2 id="modalTitle">新規追加</h2>
    <form id="leadForm" onsubmit="submitForm(event)">
      <input type="hidden" id="leadId" name="id" value="">
      <div class="form-row">
        <div class="form-group">
          <label>会社名 *</label>
          <input type="text" name="company" id="f_company" required placeholder="山田建設 株式会社">
        </div>
        <div class="form-group">
          <label>担当者名</label>
          <input type="text" name="contact" id="f_contact" placeholder="山田 太郎">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>業種</label>
          <input type="text" name="industry" id="f_industry" placeholder="建設業">
        </div>
        <div class="form-group">
          <label>電話番号</label>
          <input type="text" name="phone" id="f_phone" placeholder="083-000-0000">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>ステージ</label>
          <select name="stage" id="f_stage">
            {% for s in stages %}<option>{{ s }}</option>{% endfor %}
          </select>
        </div>
        <div class="form-group">
          <label>期限</label>
          <input type="date" name="due_date" id="f_due_date">
        </div>
      </div>
      <div class="form-group">
        <label>次のアクション</label>
        <input type="text" name="next_action" id="f_next_action" placeholder="例：資料送付後、来週電話フォロー">
      </div>
      <div class="form-group">
        <label>メモ</label>
        <textarea name="note" id="f_note" placeholder="商談内容・課題・特記事項など"></textarea>
      </div>
      <button type="submit" class="save-btn">保存する</button>
      <button type="button" class="cancel-btn" onclick="closeModal()">キャンセル</button>
    </form>
  </div>
</div>

<script>
const leads = {{ leads_json | safe }};

function openAdd() {
  document.getElementById('modalTitle').textContent = '新規追加';
  document.getElementById('leadId').value = '';
  document.getElementById('leadForm').reset();
  document.getElementById('modal').classList.add('open');
}

function openEdit(id) {
  const lead = leads.find(l => l.id === id);
  if (!lead) return;
  document.getElementById('modalTitle').textContent = '編集';
  document.getElementById('leadId').value = lead.id;
  document.getElementById('f_company').value = lead.company || '';
  document.getElementById('f_contact').value = lead.contact || '';
  document.getElementById('f_industry').value = lead.industry || '';
  document.getElementById('f_phone').value = lead.phone || '';
  document.getElementById('f_stage').value = lead.stage || '新規';
  document.getElementById('f_due_date').value = lead.due_date || '';
  document.getElementById('f_next_action').value = lead.next_action || '';
  document.getElementById('f_note').value = lead.note || '';
  document.getElementById('modal').classList.add('open');
}

function closeModal() {
  document.getElementById('modal').classList.remove('open');
}

function submitForm(e) {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target));
  fetch('/save', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) })
    .then(() => location.reload());
}

function deleteLead(id) {
  if (!confirm('削除しますか？')) return;
  fetch('/delete', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({id}) })
    .then(() => location.reload());
}

function filterTable() {
  const q = document.getElementById('searchInput').value.toLowerCase();
  const stage = document.getElementById('stageFilter').value;
  document.querySelectorAll('#leadsTable tbody tr').forEach(row => {
    const name = row.dataset.name.toLowerCase();
    const s = row.dataset.stage;
    row.style.display = (name.includes(q) && (!stage || s === stage)) ? '' : 'none';
  });
}
</script>
</body>
</html>
"""


@app.route("/")
def index():
    leads = load_data()
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template_string(
        HTML,
        leads=leads,
        leads_json=json.dumps(leads, ensure_ascii=False),
        stages=STAGES,
        stage_colors=STAGE_COLORS,
        today=today,
    )


@app.route("/save", methods=["POST"])
def save():
    data = request.get_json()
    leads = load_data()
    now = datetime.now().isoformat()
    lead_id = data.get("id", "").strip()
    if lead_id:
        for lead in leads:
            if lead["id"] == lead_id:
                lead.update({
                    "company": data.get("company", ""),
                    "contact": data.get("contact", ""),
                    "industry": data.get("industry", ""),
                    "phone": data.get("phone", ""),
                    "stage": data.get("stage", "新規"),
                    "due_date": data.get("due_date", ""),
                    "next_action": data.get("next_action", ""),
                    "note": data.get("note", ""),
                    "updated_at": now,
                })
                break
    else:
        leads.append({
            "id": str(int(datetime.now().timestamp() * 1000)),
            "company": data.get("company", ""),
            "contact": data.get("contact", ""),
            "industry": data.get("industry", ""),
            "phone": data.get("phone", ""),
            "stage": data.get("stage", "新規"),
            "due_date": data.get("due_date", ""),
            "next_action": data.get("next_action", ""),
            "note": data.get("note", ""),
            "created_at": now,
            "updated_at": now,
        })
    save_data(leads)
    return jsonify({"ok": True})


@app.route("/delete", methods=["POST"])
def delete():
    data = request.get_json()
    leads = load_data()
    leads = [l for l in leads if l["id"] != data.get("id")]
    save_data(leads)
    return jsonify({"ok": True})


if __name__ == "__main__":
    print("Emport AI CRM 起動中... http://localhost:5001")
    app.run(host="0.0.0.0", port=5001, debug=False)
