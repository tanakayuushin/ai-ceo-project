/**
 * Emport AI - Gmail下書き自動同期スクリプト
 *
 * 動作:
 *   GitHub の departments/sales/outreach-drafts/ から
 *   当日の営業メール下書きを取得し、Gmailの下書きに自動登録する
 *
 * 実行タイミング:
 *   毎週木曜 10:00 JST（トリガーで設定）
 */

// ===== 設定 =====
var GITHUB_OWNER = "tanakayuushin";
var GITHUB_REPO  = "ai-ceo-project";
var DRAFTS_PATH  = "departments/sales/outreach-drafts";
var FROM_EMAIL   = "tsubeyou081@gmail.com";
// =================

/**
 * メインエントリーポイント（トリガーから呼び出す）
 */
function syncDraftsToGmail() {
  var today = getTodayJST();
  Logger.log("実行日: " + today);

  var files = fetchDraftFiles(today);
  if (files.length === 0) {
    Logger.log("本日の下書きファイルが見つかりませんでした: " + today);
    return;
  }

  var created = 0;
  files.forEach(function(file) {
    try {
      var content = fetchFileContent(file.url);
      var parsed  = parseDraftMarkdown(content);
      if (!parsed) {
        Logger.log("スキップ（パース失敗）: " + file.name);
        return;
      }
      GmailApp.createDraft(
        FROM_EMAIL,
        parsed.subject,
        parsed.body
      );
      Logger.log("下書き作成: " + parsed.subject);
      created++;
    } catch (e) {
      Logger.log("エラー: " + file.name + " - " + e.message);
    }
  });

  Logger.log("完了: " + created + " 件の下書きを作成しました");
}

/**
 * 今日の日付を JST で YYYY-MM-DD 形式で返す
 */
function getTodayJST() {
  var now = new Date();
  var jst = new Date(now.getTime() + 9 * 60 * 60 * 1000);
  var y = jst.getUTCFullYear();
  var m = String(jst.getUTCMonth() + 1).padStart(2, "0");
  var d = String(jst.getUTCDate()).padStart(2, "0");
  return y + "-" + m + "-" + d;
}

/**
 * GitHub API で今日の下書きファイル一覧を取得する
 * summary ファイルは除外する
 */
function fetchDraftFiles(dateStr) {
  var url = "https://api.github.com/repos/" +
    GITHUB_OWNER + "/" + GITHUB_REPO +
    "/contents/" + DRAFTS_PATH;

  var res = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
  if (res.getResponseCode() !== 200) {
    Logger.log("GitHub API エラー: " + res.getContentText());
    return [];
  }

  var items = JSON.parse(res.getContentText());
  return items.filter(function(item) {
    return item.type === "file" &&
           item.name.startsWith(dateStr) &&
           !item.name.includes("summary") &&
           item.name.endsWith(".md");
  });
}

/**
 * GitHub のダウンロード URL からファイル内容を取得する
 */
function fetchFileContent(downloadUrl) {
  var res = UrlFetchApp.fetch(downloadUrl, { muteHttpExceptions: true });
  return res.getContentText("UTF-8");
}

/**
 * Markdown の下書きファイルから件名と本文を抽出する
 *
 * 期待するフォーマット:
 *   **件名**: [件名テキスト]
 *   （空行）
 *   [本文...]
 */
function parseDraftMarkdown(content) {
  var lines = content.split("\n");

  var subject = "";
  var bodyLines = [];
  var inBody = false;

  for (var i = 0; i < lines.length; i++) {
    var line = lines[i];

    // 件名行を検出
    if (!subject && /\*{0,2}件名\*{0,2}\s*[:：]/.test(line)) {
      subject = line.replace(/\*{0,2}件名\*{0,2}\s*[:：]\s*/, "").trim();
      inBody = false;
      continue;
    }

    // 件名の次の --- 以降を本文として取得
    if (subject && /^---+$/.test(line.trim())) {
      inBody = true;
      continue;
    }

    if (inBody) {
      bodyLines.push(line);
    }
  }

  // --- がない場合: 件名の2行後から本文とみなす
  if (subject && bodyLines.length === 0) {
    var subjectIdx = lines.findIndex(function(l) {
      return /\*{0,2}件名\*{0,2}\s*[:：]/.test(l);
    });
    if (subjectIdx !== -1) {
      bodyLines = lines.slice(subjectIdx + 2);
    }
  }

  if (!subject) return null;

  // Markdown の **bold** や # 見出しを平文に変換
  var body = bodyLines.join("\n")
    .replace(/^\#{1,3}\s+/gm, "")
    .replace(/\*\*(.+?)\*\*/g, "$1")
    .replace(/\*(.+?)\*/g, "$1")
    .trim();

  return { subject: subject, body: body };
}

/**
 * 手動テスト用: 今日の下書きファイル名だけ表示する
 */
function listTodayFiles() {
  var today = getTodayJST();
  var files = fetchDraftFiles(today);
  Logger.log("今日(" + today + ")のファイル: " + files.length + " 件");
  files.forEach(function(f) { Logger.log(" - " + f.name); });
}
