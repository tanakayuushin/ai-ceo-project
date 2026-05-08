// TimeTree スクレイパー
// GitHub Actions から定期実行し、予定を GAS webhook に送信する
//
// 必要な環境変数:
//   TIMETREE_EMAIL      - TimeTree ログインメールアドレス
//   TIMETREE_PASSWORD   - TimeTree ログインパスワード
//   GAS_WEBHOOK_URL     - GAS ウェブアプリの URL

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
  });
  const page = await context.newPage();

  const capturedEvents = [];

  // TimeTree 内部 API のレスポンスを横取りしてイベントデータを取得
  page.on('response', async (response) => {
    const url = response.url();
    const isEventApi =
      url.includes('timetreeapis.com') ||
      url.includes('timetreeapp.com/api') ||
      (url.includes('timetreeapp.com') && url.includes('event'));

    if (!isEventApi || response.status() !== 200) return;

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
  });

  // ── ログイン ────────────────────────────────────────
  console.log('TimeTree にログイン中...');
  await page.goto('https://timetreeapp.com/signin', { waitUntil: 'networkidle', timeout: 30000 });

  // メールアドレスを入力
  const emailSelector = [
    'input[type="email"]',
    'input[name="email"]',
    'input[placeholder*="メール"]',
    'input[placeholder*="mail" i]',
  ].join(', ');
  await page.fill(emailSelector, EMAIL);

  // パスワードを入力
  await page.fill('input[type="password"]', PASSWORD);

  // ログインボタンをクリック
  const loginBtn = [
    'button[type="submit"]',
    'button:has-text("ログイン")',
    'button:has-text("Sign in")',
    'input[type="submit"]',
  ].join(', ');
  await page.click(loginBtn);

  // カレンダー画面が表示されるまで待つ
  await page.waitForTimeout(5000);
  console.log('ログイン完了');

  // ── 今月＋来月の予定を取得 ──────────────────────────
  // ページ遷移で内部 API が叩かれるため、少し待ちながら画面操作する
  await page.waitForTimeout(3000);

  // 来月へ移動（来月分のイベントも取得）
  try {
    const nextBtn = await page.$([
      '[aria-label="next month"]',
      '[aria-label="翌月"]',
      'button:has-text(">")',
      '.navigation-next',
      '[data-testid="next-month"]',
    ].join(', '));
    if (nextBtn) {
      await nextBtn.click();
      await page.waitForTimeout(3000);
      console.log('来月に移動して予定を取得');
    }
  } catch (_) {}

  await browser.close();

  // ── 重複除去 ────────────────────────────────────────
  const seen = new Set();
  const uniqueEvents = capturedEvents.filter(ev => {
    const key = ev.title + '|' + ev.start_at;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });

  console.log(`取得した予定: ${uniqueEvents.length} 件`);

  if (uniqueEvents.length === 0) {
    console.log('予定が見つかりませんでした。終了します。');
    process.exit(0);
  }

  // ── GAS webhook に送信 ──────────────────────────────
  console.log('GAS に送信中...');
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
