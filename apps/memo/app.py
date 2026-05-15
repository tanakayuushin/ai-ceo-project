import json
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), 'memos.json')


def load_memos():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, encoding='utf-8') as f:
        return json.load(f)


def save_memos(memos):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(memos, f, ensure_ascii=False, indent=2)


@app.route('/')
def index():
    memos = load_memos()
    return render_template('index.html', memos=memos)


@app.route('/add', methods=['POST'])
def add():
    title = request.form.get('title', '').strip()
    body  = request.form.get('body', '').strip()
    if title:
        memos = load_memos()
        memos.insert(0, {
            'id':      str(len(memos) + 1) + '_' + datetime.now().strftime('%f'),
            'title':   title,
            'body':    body,
            'created': datetime.now().strftime('%Y/%m/%d %H:%M')
        })
        save_memos(memos)
    return redirect(url_for('index'))


@app.route('/delete/<memo_id>', methods=['POST'])
def delete(memo_id):
    memos = load_memos()
    memos = [m for m in memos if m['id'] != memo_id]
    save_memos(memos)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=5001)
