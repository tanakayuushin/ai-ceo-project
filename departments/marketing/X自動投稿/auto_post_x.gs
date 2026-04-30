// X（旧Twitter）自動投稿スクリプト
// Google Apps Script（Rhino / V8 両対応）
//
// セットアップ手順:
//   1. Googleスプレッドシートを新規作成
//   2. 拡張機能 > Apps Script でこのコードを全貼り付け
//   3. setup() にAPIキーを記入して1回実行
//   4. createSheet() を実行してシートひな形を作成
//   5. setHourlyTrigger() を実行して自動化開始

// ===== APIキー設定（setup()の中を書き換えて1回だけ実行） =====
function setup() {
  var props = PropertiesService.getScriptProperties();
  props.setProperties({
    'X_CONSUMER_KEY':        'ここにConsumer Keyを貼り付け',
    'X_CONSUMER_SECRET':     'ここにConsumer Secretを貼り付け',
    'X_ACCESS_TOKEN':        'ここにAccess Tokenを貼り付け',
    'X_ACCESS_TOKEN_SECRET': 'ここにAccess Token Secretを貼り付け'
  });
  Logger.log('APIキーを登録しました');
}

// ===== メイン：予定時刻になったツイートを投稿する =====
function checkAndPost() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('投稿予定');

  if (!sheet) {
    Logger.log('シート「投稿予定」が見つかりません。createSheet()を先に実行してください');
    return;
  }

  var lastRow = sheet.getLastRow();
  if (lastRow < 2) {
    Logger.log('投稿データがありません');
    return;
  }

  var data = sheet.getRange(2, 1, lastRow - 1, 5).getValues();
  var now = new Date();

  for (var i = 0; i < data.length; i++) {
    var row = data[i];
    var scheduledTime = row[0]; // A列: 投稿予定日時
    var content       = row[1]; // B列: 投稿内容
    var status        = row[2]; // C列: ステータス

    // スキップ: 内容なし・投稿済・エラー確認済
    if (!content || status === '投稿済' || status === 'エラー確認済') continue;

    // A列が日時でない場合はスキップ
    if (!(scheduledTime instanceof Date)) continue;

    // 予定時刻の ±10分以内なら投稿
    var diffMin = (now.getTime() - scheduledTime.getTime()) / 1000 / 60;
    if (diffMin < -10 || diffMin > 10) continue;

    var preview = String(content).substring(0, 20);
    Logger.log('投稿実行: 行' + (i + 2) + ' / ' + preview + '...');

    var result = postTweet(String(content));
    var rowNum = i + 2;

    if (result && result.data && result.data.id) {
      sheet.getRange(rowNum, 3).setValue('投稿済');
      sheet.getRange(rowNum, 4).setValue(new Date());
      sheet.getRange(rowNum, 5).setValue(result.data.id);
      Logger.log('投稿成功: ID = ' + result.data.id);
    } else {
      sheet.getRange(rowNum, 3).setValue('エラー');
      sheet.getRange(rowNum, 4).setValue(new Date());
      Logger.log('投稿失敗: ' + JSON.stringify(result));
    }
  }
}

// ===== テスト投稿（動作確認用 ─ 確認後に手動削除すること） =====
function testPost() {
  var result = postTweet('【動作確認】自動投稿テストです。このツイートは削除します。');
  Logger.log(JSON.stringify(result));
}

// ===== X API v2 でツイートを投稿する =====
function postTweet(text) {
  var props = PropertiesService.getScriptProperties();
  var consumerKey       = props.getProperty('X_CONSUMER_KEY');
  var consumerSecret    = props.getProperty('X_CONSUMER_SECRET');
  var accessToken       = props.getProperty('X_ACCESS_TOKEN');
  var accessTokenSecret = props.getProperty('X_ACCESS_TOKEN_SECRET');

  if (!consumerKey || consumerKey.indexOf('ここに') === 0) {
    Logger.log('APIキーが未設定です。setup() を先に実行してください');
    return null;
  }

  var url  = 'https://api.twitter.com/2/tweets';
  var body = JSON.stringify({ text: text });

  var authHeader = buildOAuthHeader(
    'POST', url, consumerKey, consumerSecret, accessToken, accessTokenSecret
  );

  try {
    var res = UrlFetchApp.fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      },
      payload: body,
      muteHttpExceptions: true
    });
    return JSON.parse(res.getContentText());
  } catch (e) {
    Logger.log('通信エラー: ' + e.message);
    return null;
  }
}

// ===== OAuth 1.0a ヘッダーを生成する =====
function buildOAuthHeader(method, url, ck, cs, at, ats) {
  var timestamp = Math.floor(Date.now() / 1000).toString();
  var nonceRaw  = Utilities.computeDigest(
    Utilities.DigestAlgorithm.MD5,
    Math.random().toString() + timestamp
  );
  var nonce = Utilities.base64Encode(nonceRaw)
    .replace(/[^a-zA-Z0-9]/g, '')
    .substring(0, 32);

  var oauthParams = {
    oauth_consumer_key:     ck,
    oauth_nonce:            nonce,
    oauth_signature_method: 'HMAC-SHA1',
    oauth_timestamp:        timestamp,
    oauth_token:            at,
    oauth_version:          '1.0'
  };

  // パラメータをソートしてパーセントエンコードで結合
  var keys = Object.keys(oauthParams).sort();
  var paramParts = [];
  for (var i = 0; i < keys.length; i++) {
    paramParts.push(pct(keys[i]) + '=' + pct(oauthParams[keys[i]]));
  }
  var paramStr = paramParts.join('&');

  // 署名ベース文字列
  var baseStr = method.toUpperCase() + '&' + pct(url) + '&' + pct(paramStr);

  // HMAC-SHA1 署名
  var signingKey = pct(cs) + '&' + pct(ats);
  var sig = Utilities.base64Encode(
    Utilities.computeHmacSha1Signature(baseStr, signingKey)
  );
  oauthParams.oauth_signature = sig;

  // Authorization ヘッダー文字列を組み立て
  var headerKeys = Object.keys(oauthParams);
  var headerParts = [];
  for (var j = 0; j < headerKeys.length; j++) {
    var k = headerKeys[j];
    headerParts.push(pct(k) + '="' + pct(oauthParams[k]) + '"');
  }
  return 'OAuth ' + headerParts.join(', ');
}

// パーセントエンコード（RFC 3986準拠）
function pct(str) {
  return encodeURIComponent(String(str))
    .replace(/!/g,  '%21')
    .replace(/'/g,  '%27')
    .replace(/\(/g, '%28')
    .replace(/\)/g, '%29')
    .replace(/\*/g, '%2A');
}

// ===== スプレッドシートのひな形を自動作成 =====
function createSheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('投稿予定');

  if (sheet) {
    Logger.log('シート「投稿予定」はすでに存在します');
    return;
  }

  sheet = ss.insertSheet('投稿予定');

  // ヘッダー
  var headers = [['投稿予定日時', '投稿内容（140字以内）', 'ステータス', '実際の投稿日時', '投稿ID']];
  sheet.getRange(1, 1, 1, 5).setValues(headers);

  var headerRange = sheet.getRange(1, 1, 1, 5);
  headerRange.setBackground('#1DA1F2');
  headerRange.setFontColor('#FFFFFF');
  headerRange.setFontWeight('bold');

  // 列幅
  sheet.setColumnWidth(1, 180);
  sheet.setColumnWidth(2, 480);
  sheet.setColumnWidth(3, 100);
  sheet.setColumnWidth(4, 160);
  sheet.setColumnWidth(5, 160);

  // サンプル行
  sheet.getRange(2, 1, 1, 5).setValues([
    [new Date(), '投稿したい内容を140字以内で書いてください', '', '', '']
  ]);

  Logger.log('シート「投稿予定」を作成しました');
}

// ===== 毎時トリガーを設定する =====
function setHourlyTrigger() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'checkAndPost') {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }
  ScriptApp.newTrigger('checkAndPost')
    .timeBased()
    .everyHours(1)
    .create();
  Logger.log('毎時トリガーを設定しました（毎時0分にcheckAndPostが動きます）');
}
