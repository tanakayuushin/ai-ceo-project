---
name: feedback-post-push-advice
description: git push後に他PCへの反映手順や確認事項を必ず伝える
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 02bc9f6a-bf09-4ca4-bc9e-868df094be04
---

git push を実行した後は、変更内容に応じた次のアクションを必ずオーナーに伝える。

**Why:** pushしただけでは他のPCに反映されない。何をすべきか伝えないと作業が止まる。

**How to apply:** push完了後、以下のパターンに応じてアドバイスを出す。

---

## パターン別アドバイス

### setup/ や .claude/ を変更した場合（設定・フック・メモリ）

```
他のPCで以下を実行してください：

git pull
cd setup
powershell -ExecutionPolicy Bypass -File .\verify.ps1

verify.ps1 が全項目 [OK] になれば Claude Code を再起動で完了です。
```

### アプリコード（apps/ や tools/）を変更した場合

```
他のPCで以下を実行してください：

git pull
cd apps/emport-ai-app   # 該当するアプリのディレクトリ
npm install
```

### ドキュメント・レポートのみの変更の場合

```
他のPCで git pull するだけで反映されます。
```

### 通常のコード変更の場合

```
他のPCで git pull するだけで最新版になります。
```

---

**注意:** 毎回同じ文言を出す必要はない。変更内容を見て本当に必要なアドバイスだけを簡潔に伝える。

[[feedback-cross-pc-verify]] [[feedback-auto-push]]
