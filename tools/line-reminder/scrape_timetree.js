// TimeTree スクレイパー（全カレンダー対応）
const { chromium } = require('playwright');

const EMAIL       = process.env.TIMETREE_EMAIL;
const PASSWORD    = process.env.TIMETREE_PASSWORD;
const WEBHOOK_URL = process.env.GAS_WEBHOOK_URL;

const SKIP_KEYWORDS = ['birthday', 'Birthday', 'BIRTHDAY', '誕生日', 'バースデー', 'お誕生日'];

function isBirthdayOrPersonal(title) {
  return SKIP_KEYWORDS.some(kw => title.includes(kw));
}

function toJSTDateStr(start) {
  const ms = (typeof start === 'number' || /^\d{10,}$/.test(String(start)))
    ? Number(start) : new Date(start).getTime();
  return new Date(ms + 9 * 3600 * 1000).toISOString().slice(0, 10).replace(/-/g, '/');
}

function todayJST() {
  return new Date(Date.now() + 9 * 3600 * 1000).toISOString().slice(0, 10).replace(/-/g, '/');
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

  // ── ログイン後の認証済みAPIリクエストからヘッダーをキャプチャ ──
  // user_agreements / public_calendars / setting はログイン処理中の事前認証呼び出しなので除外
  let capturedHeaders = null;
  page.on('request', (req) => {
    if (capturedHeaders) return;
    const url = req.url();
    if (!url.includes('timetreeapp.com/api')) return;
    if (url.includes('/auth/email')     || url.includes('/signin')          ||
        url.includes('/user_agreements')|| url.includes('/public_calendars') ||
        url.includes('/user/setting'))   return;
    const h = req.headers();
    capturedHeaders = {};
    for (const [k, v] of Object.entries(h)) {
      if (!['host', 'content-length'].includes(k)) capturedHeaders[k] = v;
    }
    console.log('[CAPTURED] from:', url.slice(0, 80));
    console.log('[HEADERS]', Object.keys(capturedHeaders).join(', '));
  });

  // ── ログイン ──────────────────────────────────────────
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

  await page.waitForURL(url => !url.toString().includes('/signin'), { timeout: 20000 });
  console.log('ログイン成功！URL:', page.url());

  // 認証ヘッダーがキャプチャされるまで待つ（最大15秒）
  for (let i = 0; i < 30 && !capturedHeaders; i++) {
    await page.waitForTimeout(500);
  }
  await page.screenshot({ path: 'debug_calendar.png' });

  if (!capturedHeaders) {
    console.warn('[WARN] APIリクエストをキャプチャできませんでした。cookieのみで試みます');
    capturedHeaders = {
      'accept': 'application/json',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    };
  }

  // Cookie も取得してヘッダーに追加
  const cookies = await context.cookies('https://timetreeapp.com');
  console.log('Cookie 数:', cookies.length, cookies.map(c => c.name).join(', '));
  if (cookies.length > 0) {
    capturedHeaders['cookie'] = cookies.map(c => `${c.name}=${c.value}`).join('; ');
  }

  await browser.close();

  // ── Node.js から直接 API を呼び出す ──────────────────
  const reqHeaders = { ...capturedHeaders, 'accept': 'application/json' };

  console.log('=== カレンダー一覧取得 ===');
  const calRes  = await fetch('https://timetreeapp.com/api/v2/calendars', { headers: reqHeaders });
  const calText = await calRes.text();
  console.log('status:', calRes.status);
  console.log('response preview:', calText.slice(0, 400));

  if (!calRes.ok) {
    console.error('calendars error');
    process.exit(1);
  }

  const calJson   = JSON.parse(calText);
  // data 配列 または calendars 配列の両方に対応
  const calendars = calJson.data || calJson.calendars || [];
  console.log('カレンダー数:', calendars.length);
  calendars.forEach(c => console.log(' -', c.id, (c.attributes && c.attributes.name) || (c.name) || ''));

  // ── 各カレンダーのイベントを取得 ──────────────────────
  const allRawEvents = [];
  for (const cal of calendars) {
    const calId   = cal.id;
    const calName = (cal.attributes && cal.attributes.name) || String(calId);

    const evRes = await fetch(
      `https://timetreeapp.com/api/v1/calendar/${calId}/events/sync`,
      { headers: reqHeaders }
    );
    if (!evRes.ok) {
      console.log(`[SKIP CAL] ${calName}: status ${evRes.status}`);
      continue;
    }

    const evJson = await evRes.json();
    const evList = Array.isArray(evJson)       ? evJson
                 : Array.isArray(evJson.data)  ? evJson.data : [];
    console.log(`[CAL] ${calName}: ${evList.length} イベント`);

    for (const ev of evList) {
      const a = ev.attributes || ev;
      allRawEvents.push({
        calName,
        title:       a.title || a.name || a.summary || '',
        start_at:    a.start_at || a.startAt || a.start || a.dt_start || '',
        all_day:     a.all_day  || a.allDay  || a.is_all_day || false,
        description: a.description || a.note || a.memo || '',
      });
    }
  }
  console.log('全イベント総数:', allRawEvents.length);

  // ── フィルタリング & 重複除去 ──────────────────────────
  const seen   = new Set();
  const today  = todayJST();
  const output = [];

  for (const ev of allRawEvents) {
    if (!ev.start_at || !ev.title) continue;
    if (isBirthdayOrPersonal(ev.title)) {
      console.log('[SKIP birthday]', ev.title);
      continue;
    }
    const dateStr = toJSTDateStr(ev.start_at);
    if (dateStr < today) {
      console.log('[SKIP past]', ev.title, dateStr);
      continue;
    }
    const key = ev.title + '|' + ev.start_at;
    if (seen.has(key)) continue;
    seen.add(key);
    console.log('[EVENT]', ev.title, dateStr, '(' + ev.calName + ')');
    output.push(ev);
  }

  console.log('\n取得した予定:', output.length, '件');
  output.forEach(ev => console.log(' -', ev.title, toJSTDateStr(ev.start_at)));

  if (output.length === 0) {
    console.log('予定が取得できませんでした');
    process.exit(0);
  }

  console.log('\nGAS に送信中...');
  const gasRes = await fetch(WEBHOOK_URL, {
    method:   'POST',
    headers:  { 'Content-Type': 'application/json' },
    body:     JSON.stringify({ events: output }),
    redirect: 'follow',
  });
  const result = await gasRes.text();
  console.log('GAS レスポンス:', result);
  console.log('完了！');
})();
