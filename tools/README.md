# Emport AI — 社内ツール一覧

このディレクトリには、Emport AIの社内業務を自動化・効率化するためのツールが含まれています。
すべてFlaskベースのWebアプリで、ブラウザから利用できます。

---

## 🛠️ ツール一覧

| ツール | ポート | 説明 | 起動コマンド |
|--------|--------|------|-------------|
| [CRM](crm/) | 5001 | 見込み客管理 (ステージ管理・商談追跡) | `python crm/crm.py` |
| [議事録](minutes/) | 5002 | AI議事録自動生成 (文字起こし → 構造化) | `python minutes/minutes.py` |
| [提案書](proposal/) | 5003 | AI提案書生成 (業種別カスタム提案書) | `python proposal/proposal.py` |
| [メルマガ](newsletter/) | 5004 | AIメールマガジン生成 (HTMLメール) | `python newsletter/newsletter.py` |
| [AI分析](ai-analysis/) | — | 問い合わせ分析CLI / RAGデモ | `python ai-analysis/main.py` |
| [コンテンツ生成](content-generator/) | — | セミナースライド・契約書PDF生成 | `python content-generator/generate_slides.py` |
| [SNS連携](social-media/) | — | X投稿・Gmail下書き同期 | `python social-media/post_to_x.py` |
| [フォーム→Discord](form-discord/) | — | フォーム入力 → PDF → Discord通知 | `python form-discord/form_discord_web.py` |

---

## 🚀 セットアップ（初回）

```bash
# 各ツールのディレクトリに入り
cd crm
pip install -r requirements.txt
python crm.py
```

APIキーが必要なツール（議事録・提案書・メルマガ）は、
起動後にブラウザの「設定」タブからAnthropicのAPIキーを入力してください。

---

## 📁 ディレクトリ構成

```
tools/
├── crm/              # 見込み客CRM (port 5001)
│   ├── crm.py
│   ├── crm_data.json (自動生成)
│   └── requirements.txt
├── minutes/          # AI議事録 (port 5002)
│   ├── minutes.py
│   ├── minutes_data.json (自動生成)
│   └── requirements.txt
├── proposal/         # AI提案書 (port 5003)
│   ├── proposal.py
│   ├── proposals_data.json (自動生成)
│   └── requirements.txt
├── newsletter/       # AIメルマガ (port 5004)
│   ├── newsletter.py
│   ├── newsletters.json (自動生成)
│   └── requirements.txt
├── ai-analysis/      # 分析系CLI
├── content-generator/ # コンテンツ生成
├── social-media/     # SNS連携
└── form-discord/     # フォーム→Discord
```

---

## 💡 活用シーン

- **CRM**: 商工会議所セミナー後の名刺管理 → 商談進捗トラッキング
- **議事録**: クライアントとのZoom商談後に文字起こしを貼り付けて議事録化
- **提案書**: 見込み客の情報入力 → 業種別カスタム提案書を5分で作成
- **メルマガ**: 月1回のニュースレターをAIで生成 → HTMLコピー → Mailchimp等に貼り付け

---

*最終更新: 2026-05-13 by Allen (CEO)*
