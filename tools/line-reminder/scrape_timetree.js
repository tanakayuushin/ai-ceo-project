// TimeTree スクレイパー（サークルカレンダー専用）
const { chromium } = require('playwright');

const EMAIL       = process.env.TIMETREE_EMAIL;
const PASSWORD    = process.env.TIMETREE_PASSWORD;
const WEBHOOK_URL = process.env.GAS_WEBHOOK_URL;

// 除外ワード（誕生日・個人イベント）
const SKIP_KEYWORDS = [
  'birthday', 'Birthday', 'BIRTHDAY',
  '誕生日', 'バースデー', 'お誕生日',
];

function isBirthdayOrPersonal(title) {
  return SKIP_KEYWORDS.some(kw => title.includes(kw));
}

(async () => {
  if (!EMAIL || !PASSWORD || !WEBHOOK_URL) {
    console.error('環境変数が不足しています: TIMETREE_EMAIL, TIMETREE_PASSWORD, GAS_WEBHOOK_URL');
    process.exit(1);
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    locale: 'ja-JP',
    timezoneId: 'Asia/Tokyo',
    viewport: { width: 1280, height: 900 },
  });
  const page = await context.newPage();

  let clubCalendarId = null; // ログイン後にURLから自動取得
  const capturedEvents = [];

  // ── 全JSONレスポンスを監視 ─────────────────────────
  page.on('response', async (response) => {
    const url = response.url();
    const ct  = response.headers()['content-type'] || '';
    if (!ct.includes('json') || response.status() !== 200) return;

    try {
      const text = await response.text();
      if (!text.includes('start_at') && !text.includes('startAt')) return;

      // URLログ（デバッグ用）
      console.log('[JSON API]', url.slice(0, 120));

      const json = JSON.parse(text);
      const items = json.data
        ? (Array.isArray(json.data) ? json.data : [json.data])
        : (Array.isArray(json) ? json : []);

      for (const item of items) {
        const attrs  = item.attributes || item;
        const start  = attrs.start_at || attrs.startAt || attrs.start;
        const title  = attrs.title || attrs.name || '';
        if (!start || !title) continue;
        if (item.type && item.type !== 'event') continue;

        // サークルカレンダー以外をスキップ（calendar_id で判定）
        const eventCalId = attrs.calendar_id || attrs.calendarId ||
          (item.relationships && item.relationships.calendar &&
           item.relationships.calendar.data && item.relationships.calendar.data.id);
        if (clubCalendarId && eventCalId && eventCalId !== clubCalendarId) {
          console.log('[SKIP other calendar]', title);
          continue;
        }

        // 誕生日・個人イベントをスキップ
        if (isBirthdayOrPersonal(title)) {
          console.log('[SKIP]', title);
          continue;
        }

        console.log('[EVENT]', title, start);
        capturedEvents.push({
          title,
          start_at:    start,
          all_day:     attrs.all_day || attrs.allDay || false,
          description: attrs.description || attrs.note || '',
        });
      }
    } catch (_) {}
  });

  // ── ログイン ────────────────────────────────────────
  console.log('=== ログイン ===');
  await page.goto('https://timetreeapp.com/signin', { waitUntil: 'networkidle', timeout: 30000 });

  const emailInput = page.locator('input[type="email"]').first();
  await emailInput.waitFor({ timeout: 10000 });
  await emailInput.click();
  await emailInput.type(EMAIL, { delay: 50 });

  const pwdInput = page.locator('input[type="password"]').first();
  await pwdInput.click();
  await pwdInput.type(PASSWORD, { delay: 50 });
  await page.waitForTimeout(300);

  const submitBtn = page.locator('button[type="submit"]').first();
  if (await submitBtn.count() > 0) {
    await submitBtn.click();
  } else {
    await pwdInput.press('Enter');
  }

  await page.waitForURL(url => !url.includes('/signin'), { timeout: 20000 });

  // ── カレンダーIDを URL から自動取得 ─────────────────
  const afterLoginUrl = page.url();
  const match = afterLoginUrl.match(/\/calendars\/([A-Za-z0-9_-]+)/);
  clubCalendarId = process.env.TIMETREE_CALENDAR_ID || (match ? match[1] : null);
  console.log('サークルカレンダーID:', clubCalendarId);
  console.log('ログイン成功！URL:', afterLoginUrl);

  // カレンダーデータ読み込み待ち
  await page.waitForTimeout(8000);
  await page.screenshot({ path: 'debug_calendar.png' });

  // ── 来月へ移動 ──────────────────────────────────────
  const nextSelectors = [
    'button[aria-label*="next" i]',
    'button[aria-label*="翌月"]',
    '[data-testid*="next"]',
  ];
  for (const sel of nextSelectors) {
    const btn = page.locator(sel).first();
    if (await btn.count() > 0) {
      await btn.click();
      console.log('来月へ移動');
      await page.waitForTimeout(5000);
      break;
    }
  }

  await browser.close();

  // ── 重複除去して送信 ────────────────────────────────
  const seen = new Set();
  const uniqueEvents = capturedEvents.filter(ev => {
    const key = ev.title + '|' + ev.start_at;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });

  console.log(`\n取得した予定: ${uniqueEvents.length} 件`);
  uniqueEvents.forEach(ev => console.log(' -', ev.title, ev.start_at));

  if (uniqueEvents.length === 0) {
    console.log('予定が取得できませんでした');
    process.exit(0);
  }

  console.log('\nGAS に送信中...');
  const response = await fetch(WEBHOOK_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ events: uniqueEvents }),
    redirect: 'follow',
  });
  const result = await response.text();
  console.log('GAS レスポンス:', result);
  console.log('完了！');
})();
