// TimeTree スクレイパー（デバッグ強化版）
const { chromium } = require('playwright');
const fs = require('fs');

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
  });
  const page = await context.newPage();

  const capturedEvents = [];
  const seenUrls = new Set();

  // ── 全レスポンスを監視してデバッグ ──────────────────
  page.on('response', async (response) => {
    const url = response.url();

    // timetree 関連の URL をすべてログ出力
    if (url.includes('timetree')) {
      if (!seenUrls.has(url)) {
        seenUrls.add(url);
        console.log('[API]', response.status(), url);
      }

      if (response.status() !== 200) return;

      try {
        const text = await response.text();
        if (!text.startsWith('{') && !text.startsWith('[')) return;

        const json = JSON.parse(text);
        const items = json.data
          ? (Array.isArray(json.data) ? json.data : [json.data])
          : [];

        for (const item of items) {
          if (item.type === 'event' && item.attributes && item.attributes.start_at) {
            const attrs = item.attributes;
            console.log('[EVENT]', attrs.title, attrs.start_at);
            capturedEvents.push({
              title:       attrs.title       || '（タイトルなし）',
              start_at:    attrs.start_at,
              end_at:      attrs.end_at      || '',
              all_day:     attrs.all_day     || false,
              description: attrs.description || attrs.note || '',
            });
          }
        }
      } catch (_) {}
    }
  });

  // ── ログイン ────────────────────────────────────────
  console.log('=== ログイン開始 ===');
  await page.goto('https://timetreeapp.com/signin', { waitUntil: 'networkidle', timeout: 30000 });
  await page.screenshot({ path: 'debug_1_signin.png' });
  console.log('サインインページを開きました');

  // メールアドレス入力
  const emailSelectors = [
    'input[type="email"]',
    'input[name="email"]',
    'input[placeholder*="メール"]',
    'input[placeholder*="mail" i]',
    'input[autocomplete="email"]',
  ];
  let emailFilled = false;
  for (const sel of emailSelectors) {
    try {
      await page.fill(sel, EMAIL, { timeout: 3000 });
      console.log('メール入力成功:', sel);
      emailFilled = true;
      break;
    } catch (_) {}
  }
  if (!emailFilled) {
    console.error('メール入力欄が見つかりません');
    await page.screenshot({ path: 'debug_error_no_email.png' });
  }

  // パスワード入力
  try {
    await page.fill('input[type="password"]', PASSWORD, { timeout: 5000 });
    console.log('パスワード入力成功');
  } catch (_) {
    console.error('パスワード入力欄が見つかりません');
  }

  await page.screenshot({ path: 'debug_2_filled.png' });

  // ログインボタンをクリック
  const loginSelectors = [
    'button[type="submit"]',
    'button:has-text("ログイン")',
    'button:has-text("Sign in")',
    'button:has-text("Log in")',
    'input[type="submit"]',
  ];
  let clicked = false;
  for (const sel of loginSelectors) {
    try {
      await page.click(sel, { timeout: 3000 });
      console.log('ログインボタンクリック成功:', sel);
      clicked = true;
      break;
    } catch (_) {}
  }
  if (!clicked) {
    console.error('ログインボタンが見つかりません');
    await page.screenshot({ path: 'debug_error_no_button.png' });
  }

  // カレンダー画面が表示されるまで待つ
  await page.waitForTimeout(6000);
  await page.screenshot({ path: 'debug_3_after_login.png' });
  console.log('ログイン後のURL:', page.url());
  console.log('=== ログイン完了 ===');

  // ── 来月へ移動 ──────────────────────────────────────
  await page.waitForTimeout(3000);
  console.log('現在のURL:', page.url());

  try {
    const nextSelectors = [
      '[aria-label="next month"]',
      '[aria-label="翌月"]',
      'button:has-text(">")',
      '.navigation-next',
      '[data-testid="next-month"]',
      'button[aria-label*="next"]',
      'button[aria-label*="Next"]',
    ];
    for (const sel of nextSelectors) {
      try {
        await page.click(sel, { timeout: 2000 });
        console.log('来月ボタンクリック成功:', sel);
        await page.waitForTimeout(3000);
        break;
      } catch (_) {}
    }
  } catch (_) {
    console.log('来月ボタンが見つかりませんでした（スキップ）');
  }

  await page.screenshot({ path: 'debug_4_calendar.png' });

  await browser.close();

  // ── 結果サマリー ────────────────────────────────────
  console.log('=== 取得結果 ===');
  console.log('確認した API URL 数:', seenUrls.size);
  console.log('取得した予定数:', capturedEvents.length);

  if (capturedEvents.length === 0) {
    console.log('予定が取得できませんでした。スクリーンショットを確認してください。');
    process.exit(0);
  }

  // 重複除去
  const seen = new Set();
  const uniqueEvents = capturedEvents.filter(ev => {
    const key = ev.title + '|' + ev.start_at;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });

  console.log('ユニーク予定数:', uniqueEvents.length);

  // ── GAS に送信 ──────────────────────────────────────
  console.log('=== GAS に送信 ===');
  const payload = JSON.stringify({ events: uniqueEvents });

  const response = await fetch(WEBHOOK_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: payload,
    redirect: 'follow',
  });

  const result = await response.text();
  console.log('GAS レスポンス:', result);
  console.log('完了！');
})();
