// Gmail Draft Sync - AI CEO Project
// GitHub の営業メール下書きを Gmail 下書きに自動登録する
// 実行タイミング: 毎週木曜 10:00 JST（トリガーで設定）

// ===== 設定 =====
var GITHUB_OWNER = "tanakayuushin";
var GITHUB_REPO  = "ai-ceo-project";
var DRAFTS_PATH  = "departments/sales/outreach-drafts";
var FROM_EMAIL   = "tsubeyou081@gmail.com";
// =================

// メインエントリーポイント（トリガーから呼び出す）
function syncDraftsToGmail() {
  var today = getTodayJST();
  Logger.log("実行日: " + today);

  var files = fetchDraftFiles(today);
  if (files.length === 0) {
    Logger.log("本日の下書きファイルが見つかりませんでした: " + today);
    return;
  }

  var created = 0;
  for (var i = 0; i < files.length; i++) {
    var file = files[i];
    try {
      var content = fetchFileContent(file.url);
      var parsed  = parseDraftMarkdown(content);
      if (!parsed) {
        Logger.log("スキップ（パース失敗）: " + file.name);
        continue;
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
  }

  Logger.log("完了: " + created + " 件の下書きを作成しました");
}

// 今日の日付を JST で YYYY-MM-DD 形式で返す
function getTodayJST() {
  var now = new Date();
  var jst = new Date(now.getTime() + 9 * 60 * 60 * 1000);
  var y = jst.getUTCFullYear();
  var m = jst.getUTCMonth() + 1;
  var d = jst.getUTCDate();
  var mm = m < 10 ? "0" + m : "" + m;
  var dd = d < 10 ? "0" + d : "" + d;
  return y + "-" + mm + "-" + dd;
}

// GitHub API で今日の下書きファイル一覧を取得する
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
  var result = [];
  for (var i = 0; i < items.length; i++) {
    var item = items[i];
    if (item.type === "file" &&
        item.name.indexOf(dateStr) === 0 &&
        item.name.indexOf("summary") === -1 &&
        item.name.slice(-3) === ".md") {
      result.push(item);
    }
  }
  return result;
}

// GitHub のダウンロード URL からファイル内容を取得する
function fetchFileContent(downloadUrl) {
  var res = UrlFetchApp.fetch(downloadUrl, { muteHttpExceptions: true });
  return res.getContentText("UTF-8");
}

// Markdown の下書きから件名と本文を抽出する
// 期待フォーマット:
//   件名: [件名テキスト]
//   ---
//   [本文...]
function parseDraftMarkdown(content) {
  var lines = content.split("\n");
  var subject = "";
  var bodyLines = [];
  var inBody = false;
  var subjectIdx = -1;

  for (var i = 0; i < lines.length; i++) {
    var line = lines[i];

    if (!subject && /件名\s*[:：]/.test(line)) {
      subject = line.replace(/.*件名\s*[:：]\s*/, "").trim();
      subjectIdx = i;
      inBody = false;
      continue;
    }

    if (subject && /^-{3,}$/.test(line.trim())) {
      inBody = true;
      continue;
    }

    if (inBody) {
      bodyLines.push(line);
    }
  }

  if (subject && bodyLines.length === 0 && subjectIdx !== -1) {
    bodyLines = lines.slice(subjectIdx + 2);
  }

  if (!subject) return null;

  var body = bodyLines.join("\n")
    .replace(/^#{1,3}\s+/gm, "")
    .replace(/\*\*(.+?)\*\*/g, "$1")
    .replace(/\*(.+?)\*/g, "$1")
    .trim();

  return { subject: subject, body: body };
}

// 手動テスト用: 今日のファイル名だけ表示する
function listTodayFiles() {
  var today = getTodayJST();
  var files = fetchDraftFiles(today);
  Logger.log("今日(" + today + ")のファイル: " + files.length + " 件");
  for (var i = 0; i < files.length; i++) {
    Logger.log(" - " + files[i].name);
  }
}
