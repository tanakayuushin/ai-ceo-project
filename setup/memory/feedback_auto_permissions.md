---
name: 自動承認・安全ガード設定
description: Claude Codeの自動承認設定を実施済み。settings.json + PreToolUseフックで安全な自動実行を実現
type: feedback
originSessionId: 02bc9f6a-bf09-4ca4-bc9e-868df094be04
---
2026-05-13に以下の3層構造の自動承認設定を実施・動作確認済み。

## 実装内容

**Layer 1: `C:\Users\tsube\.claude\settings.json`**
- `defaultMode: "acceptEdits"` — ファイル操作（Read/Write/Edit）を自動承認
- `allow` 87件 — git/python/npm/Bashコマンドを自動承認
- `deny` 14件 — 危険なコマンドをフィルタリング

**Layer 2: `C:\Users\tsube\.claude\hooks\safety_guard.py`**
- PreToolUseフックとして動作
- bypassPermissionsでも動作する最後の安全網
- exit 2でブロック、exit 0で通過

**Layer 3: Auto Mode（VS Code設定で手動有効化）**
- Ctrl+, → Claude Code → Enable Auto Mode をONにする
- AIクラシファイアが各ツール呼び出しを評価して安全なものを自動承認

## ブロック対象（絶対禁止）
- `rm -rf ~/` `rm -rf /` など広範な削除
- `git push --force` `git push -f`
- `git reset --hard`（HEAD~1以外）
- `git clean -fd`
- `sudo rm / sudo mkfs / sudo dd`
- ディスクフォーマット系

**Why:** ユーザーからの明示的な指示。AIが自律的に作業できるようにしつつ、壊滅的な操作だけは物理的にブロックする。

**How to apply:** 今後は追加のPermission許可は不要。危険なコマンドがブロックされた場合はフックが理由を説明する。
