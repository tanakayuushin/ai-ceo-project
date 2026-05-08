// TimeTree スクレイパー（DOM読み取り版）
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

  // ── ログイン ────────────────────────────────────────
  console.log('=== ログイン開始 ===');
  await page.goto('https://timetreeapp.com/signin', { waitUntil: 'networkidle', timeout: 30000 });
  await page.screenshot({ path: 'debug_1_signin.png' });

  // メール入力
  const emailSel = 'input[type="email"], input[name="email"], input[autocomplete="email"]';
  await page.waitForSelector(emailSel, { timeout: 10000 });
  await page.click(emailSel);
  await page.fill(emailSel, EMAIL);
  await page.waitForTimeout(500);

  // パスワード入力欄が出るまで待つ（2ステップログインに対応）
  await page.press(emailSel, 'Enter');
  await page.waitForTimeout(1500);

  const pwdSel = 'input[type="password"]';
  await page.waitForSelector(pwdSel, { timeout: 8000 });
  await page.fill(pwdSel, PASSWORD);
  await page.screenshot({ path: 'debug_2_filled.png' });
  await page.waitForTimeout(500);

  // Enter キーで送信（ボタンクリックより確実）
  await page.press(pwdSel, 'Enter');

  // ログイン完了を URL の変化で検知
  try {
    await page.waitForURL(url => !url.includes('/signin'), { timeout: 15000 });
    console.log('ログイン成功！');
  } catch (_) {
    console.log('ログインに失敗した可能性があります');
    await page.screenshot({ path: 'debug_error_login.png' });
  }

  await page.waitForTimeout(5000);
  await page.screenshot({ path: 'debug_3_after_login.png' });
  console.log('ログイン後 URL:', page.url());
  console.log('ページタイトル:', await page.title());

  // ── DOM からイベントを探す ──────────────────────────
  console.log('\n=== DOM 解析開始 ===');

  // ページ内のテキストをすべて取得して状況確認
  const bodyText = await page.evaluate(() => document.body.innerText.slice(0, 500));
  console.log('ページ内テキスト(先頭500文字):\n', bodyText);

  // よく使われるイベント要素のセレクタを順番に試す
  const candidateSelectors = [
    '[class*="event"]',
    '[class*="Event"]',
    '[class*="schedule"]',
    '[class*="Schedule"]',
    '[class*="item"]',
    '[data-testid*="event"]',
    '[role="button"][class*="event"]',
    'li[class*="event"]',
    'div[class*="event-title"]',
    'span[class*="event"]',
  ];

  let foundEvents = [];
  for (const sel of candidateSelectors) {
    const count = await page.locator(sel).count();
    if (count > 0) {
      console.log(`セレクタ "${sel}" で ${count} 件ヒット`);
      // 最初の5件のテキストを表示
      for (let i = 0; i < Math.min(count, 5); i++) {
        const text = await page.locator(sel).nth(i).innerText().catch(() => '');
        if (text.trim()) console.log(`  [${i}] "${text.trim().slice(0, 80)}"`);
      }
    }
  }

  // ── イベントデータを取得 ────────────────────────────
  // DOM内の全クラス名を収集してデバッグ
  const allClasses = await page.evaluate(() => {
    const classes = new Set();
    document.querySelectorAll('[class]').forEach(el => {
      el.className.toString().split(/\s+/).forEach(c => {
        if (c && (c.toLowerCase().includes('event') || c.toLowerCase().includes('schedule') || c.toLowerCase().includes('item'))) {
          classes.add(c);
        }
    });
    });
    return [...classes].slice(0, 30);
  });
  console.log('\n関連クラス名:', allClasses.join(', '));

  // JavaScriptの状態からイベントデータを取得（Reactのstoreなど）
  const jsEvents = await page.evaluate(() => {
    // window オブジェクトからカレンダーデータを探す
    const keys = Object.keys(window).filter(k =>
      k.toLowerCase().includes('event') ||
      k.toLowerCase().includes('calendar') ||
      k.toLowerCase().includes('schedule')
    );
    return keys.slice(0, 10);
  });
  console.log('\nwindow のイベント関連キー:', jsEvents);

  await page.screenshot({ path: 'debug_4_calendar.png' });
  await browser.close();

  console.log('\n=== 完了 ===');
  console.log('スクリーンショットを確認して、どんな画面が表示されているか教えてください。');
})();
