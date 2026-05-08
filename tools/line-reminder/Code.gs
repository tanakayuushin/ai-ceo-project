// =====================================================
// LINE リマインダーボット - Google Apps Script
// =====================================================
// メニュー「リマインダー」→「イベントを追加」でフォーム入力
// GASトリガーで sendReminders を1時間ごとに実行
// =====================================================


// ── Web アプリエントリーポイント ──────────────────────

// スマホ・PC からフォームを開く
function doGet() {
  return HtmlService.createHtmlOutputFromFile('Form')
    .setTitle('LINEリマインダー')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

// Playwright スクレイパーから予定データを受け取る
function doPost(e) {
  try {
    const data   = JSON.parse(e.postData.contents);
    const events = data.events || [];
    const sheet  = getSheet();
    const rows   = sheet.getLastRow() > 1
      ? sheet.getRange(2, 1, sheet.getLastRow() - 1, 7).getValues()
      : [];

    const existingKeys = new Set(
      rows.map(r => r[C_NAME - 1] + '|' + formatDate(parseDate(r[C_DATE - 1])))
    );

    const todayStr = formatDate(new Date());
    let added = 0;
    for (const ev of events) {
      if (!ev.start_at) continue;
      // ミリ秒タイムスタンプ（数値）と ISO 文字列の両方に対応
      const start = (typeof ev.start_at === 'number' || /^\d{10,}$/.test(String(ev.start_at)))
        ? new Date(Number(ev.start_at))
        : new Date(ev.start_at);
      const dateStr = formatDate(start);

      // 今日より前の予定はスキップ
      if (dateStr < todayStr) continue;

      const timeStr = ev.all_day
        ? ''
        : String(start.getHours()).padStart(2, '0') + ':' + String(start.getMinutes()).padStart(2, '0');
      const title   = ev.title || '（タイトルなし）';
      const key     = title + '|' + dateStr;

      if (existingKeys.has(key)) continue;

      sheet.appendRow([title, dateStr, timeStr, 'none', ev.description || '', '1:20;0:8', 'false']);
      existingKeys.add(key);
      added++;
    }

    // 日付順に並び替え（B列 = 日付列、YYYY/MM/DD形式なので文字列ソートで正確）
    const lastRow = sheet.getLastRow();
    if (lastRow > 1) {
      sheet.getRange(2, 1, lastRow - 1, 7).sort({ column: 2, ascending: true });
    }

    return ContentService
      .createTextOutput(JSON.stringify({ status: 'ok', added: added }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'error', message: err.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}


// ── カスタムメニュー ──────────────────────────────────

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('リマインダー')
    .addItem('イベントを追加', 'showAddForm')
    .addItem('イベント一覧を確認', 'showList')
    .addSeparator()
    .addItem('TimeTree から同期', 'syncFromTimeTree')
    .addItem('TimeTree カレンダーID を確認', 'listTimeTreeCalendars')
    .addItem('TimeTree 自動同期トリガーを設定', 'setupTimeTreeTrigger')
    .addSeparator()
    .addItem('シートのレイアウトを修正', 'fixSheetLayout')
    .addToUi();
}

function showAddForm() {
  const html = HtmlService.createHtmlOutputFromFile('Form')
    .setTitle('イベント追加')
    .setWidth(360);
  SpreadsheetApp.getUi().showSidebar(html);
}

function showList() {
  const sheet = getSheet();
  const data  = sheet.getDataRange().getValues();
  if (data.length <= 1) {
    SpreadsheetApp.getUi().alert('予定はまだ登録されていません');
    return;
  }
  const today = new Date(); today.setHours(0,0,0,0);
  const upcoming = data.slice(1).filter(row => {
    const d = parseDate(row[C_DATE - 1]);
    return d >= today && row[C_REMINDED - 1] !== 'done';
  });
  if (upcoming.length === 0) {
    SpreadsheetApp.getUi().alert('今後の予定はありません');
    return;
  }
  const msg = upcoming.map(row =>
    '【' + row[C_NAME-1] + '】' +
    formatDateJapanese(parseDate(row[C_DATE-1])) + ' ' +
    formatTimeJapanese(row[C_TIME-1])
  ).join('\n');
  SpreadsheetApp.getUi().alert('今後の予定\n\n' + msg);
}

// フォームからイベント登録
// reminders: "days:hour;days:hour" 形式 (例: "1:20;0:8")
function addEventFromForm(data) {
  const sheet = getSheet();
  sheet.appendRow([
    data.name,
    data.date,
    data.time,
    data.repeat,
    data.memo,
    data.reminders,
    'false'
  ]);
  return '登録しました：' + data.name + ' ' + data.date + ' ' + data.time;
}

function fixSheetLayout() {
  const ss    = SpreadsheetApp.openById(getSheetId());
  let   sheet = ss.getSheetByName('events');
  if (!sheet) { getSheet(); return; }

  const headers = ['イベント名', '日付', '時間', '繰り返し', 'メモ（任意）', 'リマインド設定', 'リマインド済み'];
  headers.forEach((h, i) => sheet.getRange(1, i + 1).setValue(h));

  const widths = [160, 120, 80, 110, 200, 180, 120];
  widths.forEach((w, i) => sheet.setColumnWidth(i + 1, w));

  sheet.setFrozenRows(1);
  setupValidation(sheet);
  SpreadsheetApp.getUi().alert('レイアウトを修正しました');
}


// ── プロパティ取得 ────────────────────────────────────

function getToken()          { return PropertiesService.getScriptProperties().getProperty('LINE_TOKEN'); }
function getSheetId()        { return PropertiesService.getScriptProperties().getProperty('SHEET_ID'); }
function getGroupId()        { return PropertiesService.getScriptProperties().getProperty('LINE_GROUP_ID'); }
function getTimetreeToken()  { return PropertiesService.getScriptProperties().getProperty('TIMETREE_TOKEN'); }
function getTimetreeCalId()  { return PropertiesService.getScriptProperties().getProperty('TIMETREE_CALENDAR_ID'); }

const C_NAME      = 1;
const C_DATE      = 2;
const C_TIME      = 3;
const C_REPEAT    = 4;
const C_MEMO      = 5;
const C_REMINDERS = 6; // "1:20;0:8" → 1日前20時と当日8時
const C_REMINDED  = 7; // "false" / "1:20|0:8" (送信済みキー) / "done"


// ── 定期実行：リマインド送信 ─────────────────────────

function sendReminders() {
  const sheet   = getSheet();
  const data    = sheet.getDataRange().getValues();
  const groupId = getGroupId();
  if (!groupId || data.length <= 1) return;

  const now   = new Date();
  const hour  = now.getHours();
  const today = formatDate(now);

  for (let i = 1; i < data.length; i++) {
    const row          = data[i];
    const eventDateObj = parseDate(row[C_DATE - 1]);
    const eventDate    = formatDate(eventDateObj);
    const name         = row[C_NAME - 1];
    const time         = row[C_TIME - 1];
    const repeat       = row[C_REPEAT - 1];
    const memo         = row[C_MEMO - 1] || '';
    const remindersStr = String(row[C_REMINDERS - 1] || '1:20;0:8');
    const remindedStr  = String(row[C_REMINDED - 1] || 'false');

    if (remindedStr === 'done') continue;

    // 送信済みキーのセット
    const sentKeys = remindedStr === 'false' ? [] : remindedStr.split('|');

    // リマインド設定をパース: [{days, hour}]
    const reminders = remindersStr.split(';').map(r => {
      const p = r.trim().split(':');
      return { days: parseInt(p[0]), hour: parseInt(p[1]) };
    }).filter(r => !isNaN(r.days) && !isNaN(r.hour));

    const memoLine = memo ? '\n\n' + memo : '';
    let newSentKeys = [...sentKeys];
    let updated = false;

    for (const rem of reminders) {
      const remDateObj = new Date(eventDateObj.getTime() - rem.days * 86400000);
      const remDate    = formatDate(remDateObj);
      const key        = rem.days + ':' + rem.hour;

      if (remDate === today && hour >= rem.hour && !sentKeys.includes(key)) {
        const msgDate = rem.days === 0  ? '今日の予定です！'
          : rem.days === 1             ? '明日の予定です！'
          : rem.days === 2             ? '明後日の予定です！'
          : rem.days === 3             ? '3日後に予定があります！'
          : rem.days === 4             ? '4日後に予定があります！'
          : rem.days === 5             ? '5日後に予定があります！'
          : rem.days === 6             ? '6日後に予定があります！'
          : rem.days === 7             ? '1週間後に予定があります！'
          : rem.days === 14            ? '2週間後に予定があります！'
          : rem.days + '日後に予定があります！';

        const timeDisplay = formatTimeJapanese(time);
        push(groupId,
          msgDate + '\n\n' +
          '━━━━━━━━━━\n' +
          '【' + name + '】\n' +
          formatDateJapanese(eventDateObj) +
          (timeDisplay ? '\n' + timeDisplay : '') + '\n' +
          '━━━━━━━━━━' +
          memoLine
        );
        newSentKeys.push(key);
        updated = true;
      }
    }

    if (!updated) continue;

    // 当日のリマインドがすべて送信済みかチェック
    const dayOfReminders = reminders.filter(r => r.days === 0);
    const allDayOfSent   = dayOfReminders.length > 0 &&
      dayOfReminders.every(r => newSentKeys.includes(r.days + ':' + r.hour));

    if (allDayOfSent && eventDate <= today) {
      if (repeat === 'weekly') {
        sheet.getRange(i + 1, C_DATE).setValue(getNextWeekFromDate(eventDate));
        sheet.getRange(i + 1, C_REMINDED).setValue('false');
      } else if (repeat === 'monthly') {
        sheet.getRange(i + 1, C_DATE).setValue(getNextMonthFromDate(eventDate));
        sheet.getRange(i + 1, C_REMINDED).setValue('false');
      } else {
        sheet.getRange(i + 1, C_REMINDED).setValue('done');
      }
    } else {
      sheet.getRange(i + 1, C_REMINDED).setValue(newSentKeys.join('|'));
    }
  }
}


// ── LINE APIヘルパー ──────────────────────────────────

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
  } else {
    if (sheet.getLastRow() > 0 && sheet.getRange(1, 1).getValue() === 'イベント名') {
      setupValidation(sheet);
      return sheet;
    }
  }

  sheet.clearContents();
  sheet.appendRow(['イベント名', '日付', '時間', '繰り返し', 'メモ（任意）', 'リマインド設定', 'リマインド済み']);
  sheet.setFrozenRows(1);

  const widths = [160, 120, 80, 110, 200, 180, 120];
  widths.forEach((w, i) => sheet.setColumnWidth(i + 1, w));

  setupValidation(sheet);
  return sheet;
}

function setupValidation(sheet) {
  const dateRule = SpreadsheetApp.newDataValidation()
    .requireDate().setAllowInvalid(false).build();
  sheet.getRange('B2:B1000').setDataValidation(dateRule);

  const times = [];
  for (let h = 0; h < 24; h++) {
    times.push(String(h).padStart(2,'0') + ':00');
    times.push(String(h).padStart(2,'0') + ':30');
  }
  const timeRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(times, true).setAllowInvalid(true).build();
  sheet.getRange('C2:C1000').setDataValidation(timeRule);

  const repeatRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(['none', 'weekly', 'monthly'], true).setAllowInvalid(false).build();
  sheet.getRange('D2:D1000').setDataValidation(repeatRule);

  const remindedRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(['false', 'done'], true).setAllowInvalid(true).build();
  sheet.getRange('G2:G1000').setDataValidation(remindedRule);
}


// ── 日付・時間ヘルパー ────────────────────────────────

function parseDate(str) {
  if (!str) return new Date(0);
  if (str instanceof Date) return str;
  const s = str.toString().replace(/年|月/g, '/').replace('日', '');
  const p = s.split('/');
  if (p.length === 3) return new Date(+p[0], +p[1] - 1, +p[2]);
  return new Date(str);
}

function formatDate(d) {
  return d.getFullYear() + '/' +
    String(d.getMonth() + 1).padStart(2, '0') + '/' +
    String(d.getDate()).padStart(2, '0');
}

function formatDateJapanese(d) {
  const days = ['日', '月', '火', '水', '木', '金', '土'];
  return (d.getMonth() + 1) + '月' + d.getDate() + '日（' + days[d.getDay()] + '）';
}

function formatTimeJapanese(t) {
  if (!t && t !== 0) return '';
  let h, m;
  if (t instanceof Date) {
    h = t.getHours();
    m = t.getMinutes();
  } else if (typeof t === 'number') {
    const totalMinutes = Math.round(t * 24 * 60);
    h = Math.floor(totalMinutes / 60);
    m = totalMinutes % 60;
  } else {
    const parts = t.toString().split(':');
    if (parts.length >= 2) {
      h = parseInt(parts[0]);
      m = parseInt(parts[1]);
    } else {
      return t + 'から';
    }
  }
  return m === 0 ? h + '時から' : h + '時' + m + '分から';
}

function getNextWeekFromDate(str) {
  return formatDate(new Date(parseDate(str).getTime() + 7 * 86400000));
}

function getNextMonthFromDate(str) {
  const d = parseDate(str);
  return formatDate(new Date(d.getFullYear(), d.getMonth() + 1, d.getDate()));
}


// ── TimeTree 連携 ─────────────────────────────────────

const TIMETREE_BASE = 'https://timetreeapis.com';

// TimeTree のカレンダー一覧を表示（TIMETREE_CALENDAR_ID 確認用）
function listTimeTreeCalendars() {
  const token = getTimetreeToken();
  if (!token) { SpreadsheetApp.getUi().alert('TIMETREE_TOKEN が未設定です'); return; }

  const res = UrlFetchApp.fetch(TIMETREE_BASE + '/calendars', {
    headers: { 'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.timetree.v1+json' },
    muteHttpExceptions: true
  });
  if (res.getResponseCode() !== 200) {
    SpreadsheetApp.getUi().alert('API エラー: ' + res.getResponseCode() + '\n' + res.getContentText());
    return;
  }
  const calendars = JSON.parse(res.getContentText()).data || [];
  const msg = calendars.length === 0
    ? 'カレンダーが見つかりませんでした'
    : calendars.map(c => 'ID: ' + c.id + '\n名前: ' + c.attributes.name).join('\n\n');
  SpreadsheetApp.getUi().alert('TimeTree カレンダー一覧\n\n' + msg);
}

// TimeTree の今後の予定をスプレッドシートに同期する
function syncFromTimeTree() {
  const token = getTimetreeToken();
  const calId = getTimetreeCalId();
  if (!token || !calId) {
    SpreadsheetApp.getUi().alert('TIMETREE_TOKEN または TIMETREE_CALENDAR_ID が未設定です\n\n' +
      'スクリプトプロパティに登録してください');
    return;
  }

  const res = UrlFetchApp.fetch(
    TIMETREE_BASE + '/calendars/' + calId + '/upcoming_events?timezone=Asia%2FTokyo&days=7',
    {
      headers: { 'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.timetree.v1+json' },
      muteHttpExceptions: true
    }
  );
  if (res.getResponseCode() !== 200) {
    Logger.log('TimeTree sync error: ' + res.getContentText());
    return;
  }

  const events = JSON.parse(res.getContentText()).data || [];
  const sheet  = getSheet();
  const rows   = sheet.getLastRow() > 1 ? sheet.getRange(2, 1, sheet.getLastRow() - 1, 7).getValues() : [];

  // 重複チェック用キー（イベント名 + 日付）
  const existingKeys = new Set(
    rows.map(r => r[C_NAME - 1] + '|' + formatDate(parseDate(r[C_DATE - 1])))
  );

  let added = 0;
  for (const ev of events) {
    const attrs = ev.attributes;
    if (!attrs || !attrs.start_at) continue;

    // 終日イベントはデフォルト時刻 09:00 で登録
    const start   = new Date(attrs.start_at);
    const dateStr = formatDate(start);
    const timeStr = attrs.all_day
      ? '09:00'
      : String(start.getHours()).padStart(2, '0') + ':' + String(start.getMinutes()).padStart(2, '0');
    const title   = attrs.title || '（タイトルなし）';
    const key     = title + '|' + dateStr;

    if (existingKeys.has(key)) continue;

    sheet.appendRow([title, dateStr, timeStr, 'none', attrs.description || '', '1:20;0:8', 'false']);
    existingKeys.add(key);
    added++;
  }

  const msg = added > 0 ? added + ' 件の予定を追加しました' : '新しい予定はありませんでした';
  Logger.log('TimeTree sync: ' + msg);
  // メニューから手動実行した場合のみダイアログ表示
  try { SpreadsheetApp.getUi().alert(msg); } catch (e) { /* トリガー実行時はスキップ */ }
}

// 1時間おきの自動同期トリガーを登録（1回だけ実行すればOK）
function setupTimeTreeTrigger() {
  // 既存トリガーの重複登録を防ぐ
  ScriptApp.getProjectTriggers().forEach(t => {
    if (t.getHandlerFunction() === 'syncFromTimeTree') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('syncFromTimeTree').timeBased().everyHours(1).create();
  SpreadsheetApp.getUi().alert('自動同期トリガーを設定しました（1時間おき）');
}
