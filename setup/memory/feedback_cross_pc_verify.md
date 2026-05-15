---
name: feedback-cross-pc-verify
description: 他PCでのセットアップ確認・git pull後の検証スキル
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 02bc9f6a-bf09-4ca4-bc9e-868df094be04
---

新しいPCへの移行やgit pull後は、設定が正しく反映されているか必ず verify.ps1 で確認する。

**How to apply:**
- 他のPCでのセットアップ完了後、またはgit pullで大きな変更を取得した後は `setup/verify.ps1` の実行を案内する
- ユーザーが「別PCで動かない」「反映されない」と言ったら、まず verify.ps1 を実行してもらう
- 新しいアプリや機能を追加した際も、verify.ps1 に確認項目を追記する（スクリプトを育てる）

**verify.ps1 の確認項目（現在）:**
1. `~/.claude/settings.json` — BOMなし・JSON有効・defaultMode=bypassPermissions
2. セキュリティフック4本（layer2〜5）の存在確認
3. Python の動作確認（フックのテスト実行）
4. アレンのメモリファイル（19件）の存在確認
5. プロジェクト `.claude/settings.json` — BOMなし・JSON有効
6. git 状態（origin/mainとの同期、未コミット変更）
7. Claude Code CLI のインストール確認

**Why:**
BOM付きUTF-8でsettings.jsonが保存されるとClaude CodeがJSONを読めず自動承認が無効になる問題が発生した。
手動確認は見落としが多く、スクリプトで一括チェックする方が確実。

**実行コマンド:**
```powershell
cd setup
powershell -ExecutionPolicy Bypass -File .\verify.ps1
```

[[feedback-auto-push]] [[feedback-auto-permissions]]
