// =====================================================
// LINE リマインダーボット - Google Apps Script
// =====================================================
// 使えるコマンド（LINEグループで入力）:
//   /add 定例会 2026/05/10 19:00        → イベント登録
//   /add 練習 毎週木曜 18:30            → 毎週繰り返し登録
//   /add 総会 毎月15日 20:00            → 毎月繰り返し登録
//   /list                               → 予定一覧
//   /del 1                              → 番号指定で削除
//   /help                               → ヘルプ表示
// =====================================================

// ── 設定（スクリプトプロパティで管理）────────────────
function getToken()   { return PropertiesService.getScriptProperties().getProperty('LINE_TOKEN'); }
function getSheetId() { return PropertiesService.getScriptProperties().getProperty('SHEET_ID'); }
function getGroupId() { return PropertiesService.getScriptProperties().getProperty('LINE_GROUP_ID'); }

// スプレッドシートの列番号
const C_ID       = 1;
const C_NAME     = 2;
const C_DATE     = 3;
const C_TIME     = 4;
const C_REPEAT   = 5; // none / weekly / monthly
const C_REMINDED = 6; // false / evening_done / done


// ── Webhook受信 ──────────────────────────────────────

function doPost(e) {
  try {
    const body = JSON.parse(e.postData.contents);
    body.events.forEach(ev => {
      if (ev.type !== 'message' || ev.message.type !== 'text') return;

      const text    = ev.message.text.trim();
      const token   = ev.replyToken;
      const srcId   = ev.source.groupId || ev.source.roomId || ev.source.userId;

      // グループIDを初回保存
      if (srcId) saveGroupId(srcId);

      if      (text.match(/^\/add|^\/追加/))    handleAdd(text, token);
      else if (text.match(/^\/list|^\/一覧/))   handleList(token);
      else if (text.match(/^\/del|^\/削除/))    handleDelete(text, token);
      else if (text.match(/^\/help|^\/ヘルプ/)) handleHelp(token);
    });
  } catch(err) {
    Logger.log('doPost error: ' + err);
  }
  return ContentService.createTextOutput('OK');
}

function saveGroupId(id) {
  const props = PropertiesService.getScriptProperties();
  if (!props.getProperty('LINE_GROUP_ID')) {
    props.setProperty('LINE_GROUP_ID', id);
  }
}


// ── コマンドハンドラ ──────────────────────────────────

function handleAdd(text, replyToken) {
  const raw   = text.replace(/^\/add\s*|^\/追加\s*/i, '').trim();
  const parts = raw.split(/\s+/);

  if (parts.length < 3) {
    reply(replyToken,
      '⚠️ 形式が違います\n\n' +
      '【使い方】\n' +
      '/add イベント名 日付 時間\n\n' +
      '【例】\n' +
      '/add 定例会 2026/05/10 19:00\n' +
      '/add 練習 毎週木曜 18:30\n' +
      '/add 会費集め 毎月1日 12:00'
    );
    return;
  }

  const name    = parts[0];
  const dateStr = parts[1];
  const timeStr = parts[2];

  let actualDate = dateStr;
  let repeatMode = 'none';

  // 毎週パターン
  if (dateStr.includes('毎週')) {
    repeatMode = 'weekly';
    const dayMap = {'月':1,'火':2,'水':3,'木':4,'金':5,'土':6,'日':0};
    const ch = dateStr.replace('毎週','').replace('曜','');
    if (dayMap[ch] !== undefined) actualDate = getNextWeekday(dayMap[ch]);

  // 毎月パターン
  } else if (dateStr.includes('毎月')) {
    repeatMode = 'monthly';
    const dayNum = parseInt(dateStr.replace(/毎月|日/g,''));
    if (!isNaN(dayNum)) actualDate = getNextMonthDay(dayNum);
  }

  const sheet = getSheet();
  const id    = new Date().getTime().toString();
  sheet.appendRow([id, name, actualDate, timeStr, repeatMode, 'false']);

  const rep = repeatMode === 'weekly' ? '（毎週）' : repeatMode === 'monthly' ? '（毎月）' : '';
  reply(replyToken,
    `✅ 登録しました！\n\n` +
    `📅 ${name} ${rep}\n` +
    `🗓 ${actualDate}  ${timeStr}\n\n` +
    `⏰ 前日20時・当日8時にリマインドします`
  );
}

function handleList(replyToken) {
  const sheet = getSheet();
  const data  = sheet.getDataRange().getValues();

  if (data.length <= 1) {
    reply(replyToken, '📋 予定はまだ登録されていません\n/add で追加できます');
    return;
  }

  const today = new Date(); today.setHours(0,0,0,0);
  const rows  = [];

  for (let i = 1; i < data.length; i++) {
    const d = parseDate(data[i][C_DATE - 1]);
    if (d >= today) rows.push({ rowNum: i, data: data[i] });
  }

  if (rows.length === 0) {
    reply(replyToken, '📋 今後の予定はありません');
    return;
  }

  rows.sort((a, b) => parseDate(a.data[C_DATE-1]) - parseDate(b.data[C_DATE-1]));

  let msg = '📋 今後の予定\n━━━━━━━━━━\n';
  rows.slice(0, 10).forEach((r, idx) => {
    const rep = r.data[C_REPEAT-1];
    const icon = rep === 'weekly' ? '🔄' : rep === 'monthly' ? '🔁' : '📌';
    msg += `${icon} ${r.rowNum}. ${r.data[C_NAME-1]}\n`;
    msg += `   ${r.data[C_DATE-1]}  ${r.data[C_TIME-1]}\n`;
  });
  msg += '\n🗑 削除: /del 番号';

  reply(replyToken, msg);
}

function handleDelete(text, replyToken) {
  const num = parseInt(text.replace(/^\/del\s*|^\/削除\s*/i, '').trim());
  if (isNaN(num) || num < 1) {
    reply(replyToken, '削除する番号を指定してください\n例: /del 1');
    return;
  }

  const sheet = getSheet();
  const data  = sheet.getDataRange().getValues();

  if (num >= data.length) {
    reply(replyToken, '⚠️ その番号のイベントは見つかりません\n/list で確認してください');
    return;
  }

  const name = data[num][C_NAME - 1];
  sheet.deleteRow(num + 1);
  reply(replyToken, `🗑 「${name}」を削除しました`);
}

function handleHelp(replyToken) {
  reply(replyToken,
    '🤖 リマインダーボット\n' +
    '━━━━━━━━━━\n' +
    '📝 登録\n' +
    '/add イベント名 日付 時間\n\n' +
    '【例】\n' +
    '/add 定例会 2026/05/10 19:00\n' +
    '/add 練習 毎週木曜 18:30\n' +
    '/add 総会 毎月15日 20:00\n\n' +
    '📋 一覧\n' +
    '/list\n\n' +
    '🗑 削除\n' +
    '/del 番号\n\n' +
    '⏰ リマインド\n' +
    '前日20時 と 当日8時 に自動送信'
  );
}


// ── 定期実行：リマインド送信（毎時トリガー推奨）────────

function sendReminders() {
  const sheet   = getSheet();
  const data    = sheet.getDataRange().getValues();
  const groupId = getGroupId();
  if (!groupId || data.length <= 1) return;

  const now      = new Date();
  const hour     = now.getHours();
  const today    = formatDate(now);
  const tomorrow = formatDate(new Date(now.getTime() + 86400000));

  for (let i = 1; i < data.length; i++) {
    const row       = data[i];
    const eventDate = row[C_DATE - 1];
    const name      = row[C_NAME - 1];
    const time      = row[C_TIME - 1];
    const repeat    = row[C_REPEAT - 1];
    const reminded  = row[C_REMINDED - 1];

    // 前日夜20時リマインド
    if (eventDate === tomorrow && hour >= 20 && reminded === 'false') {
      push(groupId,
        `🔔 明日の予定があります！\n\n` +
        `📅 ${name}\n` +
        `🕐 ${eventDate}  ${time}\n\n` +
        `準備しておこう！`
      );
      sheet.getRange(i + 1, C_REMINDED).setValue('evening_done');
    }

    // 当日朝8時リマインド
    if (eventDate === today && hour >= 8 && reminded !== 'done') {
      push(groupId,
        `⏰ 今日の予定！\n\n` +
        `📅 ${name}\n` +
        `🕐 ${time}〜\n\n` +
        `遅刻しないように〜！`
      );

      if (repeat === 'weekly') {
        sheet.getRange(i + 1, C_DATE).setValue(getNextWeekFromDate(eventDate));
        sheet.getRange(i + 1, C_REMINDED).setValue('false');
      } else if (repeat === 'monthly') {
        sheet.getRange(i + 1, C_DATE).setValue(getNextMonthFromDate(eventDate));
        sheet.getRange(i + 1, C_REMINDED).setValue('false');
      } else {
        sheet.getRange(i + 1, C_REMINDED).setValue('done');
      }
    }
  }
}


// ── LINE APIヘルパー ──────────────────────────────────

function reply(replyToken, text) {
  UrlFetchApp.fetch('https://api.line.me/v2/bot/message/reply', {
    method: 'post',
    contentType: 'application/json',
    headers: { 'Authorization': 'Bearer ' + getToken() },
    payload: JSON.stringify({
      replyToken: replyToken,
      messages: [{ type: 'text', text: text }]
    }),
    muteHttpExceptions: true
  });
}

function push(to, text) {
  UrlFetchApp.fetch('https://api.line.me/v2/bot/message/push', {
    method: 'post',
    contentType: 'application/json',
    headers: { 'Authorization': 'Bearer ' + getToken() },
    payload: JSON.stringify({
      to: to,
      messages: [{ type: 'text', text: text }]
    }),
    muteHttpExceptions: true
  });
}


// ── スプレッドシートヘルパー ──────────────────────────

function getSheet() {
  const ss    = SpreadsheetApp.openById(getSheetId());
  let   sheet = ss.getSheetByName('events');
  if (!sheet) {
    sheet = ss.insertSheet('events');
    sheet.appendRow(['ID', 'イベント名', '日付', '時間', '繰り返し', 'リマインド済み']);
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function parseDate(str) {
  if (!str) return new Date(0);
  const s = str.toString().replace(/年|月/g, '/').replace('日', '');
  const p = s.split('/');
  if (p.length === 3) return new Date(+p[0], +p[1] - 1, +p[2]);
  return new Date(str);
}

function formatDate(d) {
  return `${d.getFullYear()}/${String(d.getMonth()+1).padStart(2,'0')}/${String(d.getDate()).padStart(2,'0')}`;
}

function getNextWeekday(target) {
  const today = new Date();
  let diff = target - today.getDay();
  if (diff <= 0) diff += 7;
  return formatDate(new Date(today.getTime() + diff * 86400000));
}

function getNextMonthDay(dayNum) {
  const today = new Date();
  let d = new Date(today.getFullYear(), today.getMonth(), dayNum);
  if (d <= today) d = new Date(today.getFullYear(), today.getMonth() + 1, dayNum);
  return formatDate(d);
}

function getNextWeekFromDate(str) {
  return formatDate(new Date(parseDate(str).getTime() + 7 * 86400000));
}

function getNextMonthFromDate(str) {
  const d = parseDate(str);
  return formatDate(new Date(d.getFullYear(), d.getMonth() + 1, d.getDate()));
}
