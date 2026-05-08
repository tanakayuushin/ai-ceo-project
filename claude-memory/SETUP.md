# 別PCでのメモリセットアップ手順

このフォルダのファイルを新しいPCの Claude Code メモリディレクトリにコピーする。

## コピー先（Windows）

```
C:\Users\<ユーザー名>\.claude\projects\c--Users-<ユーザー名>-OneDrive--------ai-ceo-project\memory\
```

## コピー先（Mac/Linux）

```
~/.claude/projects/<プロジェクトパスをハイフン区切りに変換>/memory/
```

## 手順

1. リポジトリを `git clone` する
2. 上記のパスにフォルダが存在しなければ作成する
3. `claude-memory/` 内の全 `.md` ファイルをコピーする
4. Claude Code（Cursor拡張）を再起動する

## 注意

- このフォルダへの変更は定期的に `git push` して同期すること
- `.env` / `credentials.json` / `token.pickle` は **絶対にGitHubに追加しない**
