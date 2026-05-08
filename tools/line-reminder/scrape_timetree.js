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

  // ── ログイン後のAPIリクエストからヘッダーをキャプチャ ──
  // user_agreements / public_calendars / setting はログイン処理中なので除外
  let capturedHeaders = null;
  let headerLogged    = false;
  page.on('request', (req) => {
    const url = req.url();
    if (!url.includes('timetreeapp.com/api')) return;
    if (url.includes('/auth/email')      || url.includes('/signin') ||
        url.includes('/user_agreements') || url.includes('/public_calendars') ||
        url.includes('/user/setting'))    return;
    const h   = req.headers();
    const newH = {};
    for (const [k, v] of Object.entries(h)) {
      if (!['host', 'content-length'].includes(k)) newH[k] = v;
    }
    capturedHeaders = newH;   // 常に最新で上書き
    if (!headerLogged && Object.keys(newH).length > 0) {
      headerLogged = true;
      console.log('[CAPTURED] from:', url.slice(0, 80));
      console.log('[HEADERS]', Object.keys(newH).join(', '));
    }
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

  // ヘッダーキャプチャ & ページ安定待ち
  await page.waitForTimeout(10000);
  await page.screenshot({ path: 'debug_calendar.png' });

  if (!capturedHeaders || Object.keys(capturedHeaders).length === 0) {
    console.error('[ERROR] APIヘッダーをキャプチャできませんでした');
    await browser.close();
    process.exit(1);
  }
  console.log('[HEADERS FINAL]', Object.keys(capturedHeaders).join(', '));

  // ── ブラウザセッションが生きている間にAPIを叩く ──────
  // /events/sync はセッション内で一度アプリが呼ぶと差分だけ返すため、
  // ブラウザを閉じる前（セッション活性状態）に page.evaluate から呼ぶ
  console.log('=== 全カレンダーAPI取得 ===');
  const apiResult = await page.evaluate(async (headers) => {
    const logs   = [];
    const events = [];
    const h      = { ...headers, 'accept': 'application/json' };

    try {
      // カレンダー一覧
      const calRes = await fetch('https://timetreeapp.com/api/v2/calendars', {
        headers: h, credentials: 'include',
      });
      logs.push('calendars status: ' + calRes.status);
      if (!calRes.ok) {
        logs.push('body: ' + (await calRes.text()).slice(0, 200));
        return { logs, events };
      }

      const calJson   = await calRes.json();
      const calendars = calJson.data || calJson.calendars || [];
      logs.push('calendars count: ' + calendars.length);

      for (const cal of calendars) {
        const calId   = cal.id;
        const calName = (cal.attributes && cal.attributes.name) || cal.name || String(calId);

        // events/sync で全イベントを取得
        const evRes = await fetch(
          'https://timetreeapp.com/api/v1/calendar/' + calId + '/events/sync',
          { headers: h, credentials: 'include' }
        );
        logs.push('[' + calName + '] sync: ' + evRes.status);

        if (!evRes.ok) continue;

        const evText = await evRes.text();
        logs.push('  preview: ' + evText.slice(0, 120));

        let evJson;
        try { evJson = JSON.parse(evText); } catch(e) { logs.push('  parse err'); continue; }

        const evList = Array.isArray(evJson)       ? evJson
                     : Array.isArray(evJson.data)  ? evJson.data : [];
        logs.push('  events: ' + evList.length);

        for (const ev of evList) {
          const a = ev.attributes || ev;
          events.push({
            calName,
            title:       a.title || a.name || a.summary || '',
            start_at:    a.start_at || a.startAt || a.start || a.dt_start || '',
            all_day:     a.all_day  || a.allDay  || a.is_all_day || false,
            description: a.description || a.note || a.memo || '',
          });
        }
      }
    } catch (err) {
      logs.push('ERROR: ' + err.message);
    }

    return { logs, events };
  }, capturedHeaders);

  apiResult.logs.forEach(l => console.log('[API]', l));
  console.log('API取得イベント総数:', (apiResult.events || []).length);

  await browser.close();

  // ── フィルタリング & 重複除去 ──────────────────────────
  const seen   = new Set();
  const today  = todayJST();
  const output = [];

  for (const ev of (apiResult.events || [])) {
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
