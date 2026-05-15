// =====================================================
// LINE リマインダーボット - Google Apps Script
// =====================================================
// メニュー「リマインダー」→「イベントを追加」でフォーム入力
// GASトリガーで sendReminders を1時間ごとに実行
// =====================================================


// ── カスタムメニュー ──────────────────────────────────

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('リマインダー')
    .addItem('イベントを追加', 'showAddForm')
    .addItem('イベント一覧を確認', 'showList')
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


// ── スマホ向けWebアプリ ───────────────────────────────
// ウェブアプリとしてデプロイすると、このURLをスマホで開いて
// イベントの追加・一覧・削除ができる（ホーム画面に追加でアプリ風）。

function doGet(e) {
  return HtmlService.createHtmlOutputFromFile('MobileApp')
    .setTitle('LINEリマインダー')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

// 一覧取得（今後の予定のみ、日付昇順）
function getEventList() {
  const sheet = getSheet();
  const data  = sheet.getDataRange().getValues();
  if (data.length <= 1) return [];

  const today = new Date(); today.setHours(0,0,0,0);
  const events = [];
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const d   = parseDate(row[C_DATE - 1]);
    if (d < today || row[C_REMINDED - 1] === 'done') continue;
    events.push({
      row:       i + 1,
      name:      row[C_NAME - 1],
      date:      formatDate(d),
      dateLabel: formatDateJapanese(d),
      time:      row[C_TIME - 1],
      timeLabel: formatTimeJapanese(row[C_TIME - 1]),
      repeat:    row[C_REPEAT - 1] || 'none',
      memo:      row[C_MEMO - 1] || ''
    });
  }
  events.sort((a, b) => a.date.localeCompare(b.date));
  return events;
}

function deleteEvent(rowIndex) {
  const sheet = getSheet();
  if (rowIndex < 2 || rowIndex > sheet.getLastRow()) {
    throw new Error('無効な行番号です');
  }
  sheet.deleteRow(rowIndex);
  return 'ok';
}


// ── プロパティ取得 ────────────────────────────────────

function getToken()   { return PropertiesService.getScriptProperties().getProperty('LINE_TOKEN'); }
function getSheetId() { return PropertiesService.getScriptProperties().getProperty('SHEET_ID'); }
function getGroupId() { return PropertiesService.getScriptProperties().getProperty('LINE_GROUP_ID'); }

const C_NAME      = 1;
const C_DATE      = 2;
const C_TIME      = 3;
const C_REPEAT    = 4;
const C_MEMO      = 5;
const C_REMINDERS = 6; // "1:20;0:8" → 1日前20時と当日8時
const C_REMINDED  = 7; // "false" / "1:20|0:8" (送信済みキー) / "done"


// ── 月次カレンダー送信 ────────────────────────────────

function sendMonthlyCalendar() {
  const groupId = getGroupId();
  if (!groupId) return;

  const now        = new Date();
  const year       = now.getFullYear();
  const month      = now.getMonth();
  const firstDay   = new Date(year, month, 1);
  const lastDay    = new Date(year, month + 1, 0);
  const totalDays  = lastDay.getDate();

  // 当月の予定を収集
  const sheet  = getSheet();
  const data   = sheet.getDataRange().getValues();
  const events = {};
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    if (row[C_REMINDED - 1] === 'done') continue;
    const d = parseDate(row[C_DATE - 1]);
    if (d.getFullYear() === year && d.getMonth() === month) {
      const day = d.getDate();
      if (!events[day]) events[day] = [];
      events[day].push({ name: row[C_NAME - 1], time: row[C_TIME - 1] });
    }
  }

  // カレンダーグリッド生成（月曜始まり）
  const DOW_LABELS = ['月', '火', '水', '木', '金', '土', '日'];
  const startDow   = (firstDay.getDay() + 6) % 7;
  let grid = DOW_LABELS.join('  ') + '\n';
  let row  = Array(startDow).fill('   ');
  for (let d = 1; d <= totalDays; d++) {
    const mark = events[d] ? '●' : ' ';
    row.push(mark + String(d).padStart(2, ' '));
    if (row.length === 7 || d === totalDays) {
      grid += row.join(' ') + '\n';
      row  = [];
    }
  }

  // 予定リスト
  const weekdays  = ['日', '月', '火', '水', '木', '金', '土'];
  const eventKeys = Object.keys(events).map(Number).sort((a, b) => a - b);
  let eventList   = '';
  if (eventKeys.length > 0) {
    eventList = '\n📌 今月の予定\n';
    for (const day of eventKeys) {
      const dow = weekdays[new Date(year, month, day).getDay()];
      for (const ev of events[day]) {
        const t = ev.time ? ' ' + formatTimeJapanese(ev.time) : '';
        eventList += '●' + day + '日(' + dow + ') ' + ev.name + t + '\n';
      }
    }
  } else {
    eventList = '\n今月の登録予定はありません';
  }

  push(groupId, '📅 ' + (month + 1) + '月のカレンダー\n\n' + grid + eventList);
}


// ── 定期実行：リマインド送信 ─────────────────────────

function sendReminders() {
  const sheet   = getSheet();
  const data    = sheet.getDataRange().getValues();
  const groupId = getGroupId();
  if (!groupId || data.length <= 1) return;

  const now   = new Date();
  const hour  = now.getHours();
  const today = formatDate(now);

  // 毎月1日の8時にカレンダーを送信
  if (now.getDate() === 1 && hour === 8) {
    sendMonthlyCalendar();
  }

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

        push(groupId,
          msgDate + '\n\n' +
          '━━━━━━━━━━\n' +
          '【' + name + '】\n' +
          formatDateJapanese(eventDateObj) + '\n' +
          formatTimeJapanese(time) + '\n' +
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
    .requireValueInList(times, true).setAllowInvalid(false).build();
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
