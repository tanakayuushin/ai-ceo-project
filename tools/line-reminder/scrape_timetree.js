// TimeTree スクレイパー
const { chromium } = require('playwright');

const EMAIL       = process.env.TIMETREE_EMAIL;
const PASSWORD    = process.env.TIMETREE_PASSWORD;
const WEBHOOK_URL = process.env.GAS_WEBHOOK_URL;

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

  const capturedEvents = [];

  // ── 全レスポンスを監視してイベントデータを探す ──────
  page.on('response', async (response) => {
    const url = response.url();
    const ct  = response.headers()['content-type'] || '';
    if (!ct.includes('json')) return;
    if (response.status() !== 200) return;

    try {
      const text = await response.text();
      if (!text.includes('start_at') && !text.includes('startAt')) return;

      console.log('[JSON API]', url);
      const json = JSON.parse(text);

      // JSON:API 形式 { data: [...] }
      const items = json.data
        ? (Array.isArray(json.data) ? json.data : [json.data])
        : [];

      for (const item of items) {
        const attrs = item.attributes || item;
        const start = attrs.start_at || attrs.startAt || attrs.start;
        if (!start) continue;
        if (item.type && item.type !== 'event') continue;

        console.log('[EVENT]', attrs.title || attrs.name, start);
        capturedEvents.push({
          title:       attrs.title || attrs.name || '（タイトルなし）',
          start_at:    start,
          all_day:     attrs.all_day || attrs.allDay || false,
          description: attrs.description || attrs.note || '',
        });
      }

      // フラット配列形式 [{ start_at, title, ... }]
      if (Array.isArray(json)) {
        for (const item of json) {
          const start = item.start_at || item.startAt;
          if (!start) continue;
          console.log('[EVENT]', item.title || item.name, start);
          capturedEvents.push({
            title:       item.title || item.name || '（タイトルなし）',
            start_at:    start,
            all_day:     item.all_day || item.allDay || false,
            description: item.description || item.note || '',
          });
        }
      }
    } catch (_) {}
  });

  // ── ログイン ────────────────────────────────────────
  console.log('=== ログイン開始 ===');
  await page.goto('https://timetreeapp.com/signin', { waitUntil: 'networkidle', timeout: 30000 });
  await page.screenshot({ path: 'debug_1_signin.png' });

  // メール入力
  const emailInput = page.locator('input[type="email"]').first();
  await emailInput.waitFor({ timeout: 10000 });
  await emailInput.click();
  await emailInput.type(EMAIL, { delay: 50 });
  await page.waitForTimeout(500);

  // パスワード入力
  const pwdInput = page.locator('input[type="password"]').first();
  await pwdInput.click();
  await pwdInput.type(PASSWORD, { delay: 50 });
  await page.waitForTimeout(500);
  await page.screenshot({ path: 'debug_2_filled.png' });

  // 送信
  const submitBtn = page.locator('button[type="submit"]').first();
  if (await submitBtn.count() > 0) {
    await submitBtn.click();
  } else {
    await pwdInput.press('Enter');
  }

  // カレンダーページへの遷移を待つ
  await page.waitForURL(url => !url.includes('/signin'), { timeout: 20000 });
  console.log('ログイン成功！URL:', page.url());

  // カレンダーのデータ読み込みを待つ
  await page.waitForTimeout(6000);
  await page.screenshot({ path: 'debug_3_calendar.png' });

  // ── 来月へ移動して追加のデータを取得 ───────────────
  try {
    const nextSelectors = [
      'button[aria-label*="next" i]',
      'button[aria-label*="翌月"]',
      'button[aria-label*="Next"]',
      '[data-testid*="next"]',
    ];
    for (const sel of nextSelectors) {
      const btn = page.locator(sel).first();
      if (await btn.count() > 0) {
        await btn.click();
        console.log('来月へ移動:', sel);
        await page.waitForTimeout(4000);
        break;
      }
    }
  } catch (_) {
    console.log('来月ボタンが見つかりませんでした');
  }

  await browser.close();

  // ── 重複除去 ────────────────────────────────────────
  const seen = new Set();
  const uniqueEvents = capturedEvents.filter(ev => {
    const key = ev.title + '|' + ev.start_at;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });

  console.log(`\n取得した予定: ${uniqueEvents.length} 件`);
  if (uniqueEvents.length === 0) {
    console.log('予定が取得できませんでした');
    process.exit(0);
  }

  // ── GAS に送信 ──────────────────────────────────────
  console.log('GAS に送信中...');
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
