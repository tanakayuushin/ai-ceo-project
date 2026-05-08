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

  // ── フォーム要素を確認 ─────────────────────────────
  // ページ上の全 input を列挙してデバッグ
  const inputs = await page.evaluate(() =>
    [...document.querySelectorAll('input')].map(el => ({
      type: el.type, name: el.name, id: el.id,
      placeholder: el.placeholder, autocomplete: el.autocomplete
    }))
  );
  console.log('input 要素:', JSON.stringify(inputs));

  // ページ上の全 button を列挙
  const buttons = await page.evaluate(() =>
    [...document.querySelectorAll('button')].map(el => ({
      type: el.type, text: el.innerText.trim().slice(0, 40), id: el.id
    }))
  );
  console.log('button 要素:', JSON.stringify(buttons));

  // ── メール入力 ──────────────────────────────────────
  const emailInput = page.locator('input[type="email"]').first();
  const emailCount = await emailInput.count();
  console.log('メール input 数:', emailCount);

  if (emailCount > 0) {
    await emailInput.click();
    await emailInput.fill('');
    await page.waitForTimeout(300);
    await emailInput.type(EMAIL, { delay: 50 });
    console.log('メールアドレスを入力しました');
  }

  await page.waitForTimeout(500);
  await page.screenshot({ path: 'debug_2_email_filled.png' });

  // ── パスワード入力 ──────────────────────────────────
  const pwdInput = page.locator('input[type="password"]').first();
  const pwdCount = await pwdInput.count();
  console.log('パスワード input 数:', pwdCount);

  if (pwdCount > 0) {
    await pwdInput.click();
    await pwdInput.fill('');
    await page.waitForTimeout(300);
    await pwdInput.type(PASSWORD, { delay: 50 });
    console.log('パスワードを入力しました');
  }

  await page.screenshot({ path: 'debug_2_filled.png' });
  await page.waitForTimeout(500);

  // ── 送信：複数の方法を順番に試す ───────────────────
  // 方法1: type="submit" のボタンをクリック
  const submitBtn = page.locator('button[type="submit"]').first();
  if (await submitBtn.count() > 0) {
    console.log('submitボタンをクリック');
    await submitBtn.click();
  } else {
    // 方法2: Enter キーで送信
    console.log('Enter キーで送信');
    await pwdInput.press('Enter');
  }

  // ログイン完了を URL の変化で検知（最大20秒待つ）
  try {
    await page.waitForURL(url => !url.includes('/signin'), { timeout: 20000 });
    console.log('ログイン成功！');
  } catch (_) {
    console.log('ログインできませんでした。認証情報を確認してください。');
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
