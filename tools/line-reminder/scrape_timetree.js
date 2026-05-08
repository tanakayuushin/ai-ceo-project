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

  // セッション確立を待つ
  await page.waitForTimeout(8000);
  await page.screenshot({ path: 'debug_calendar.png' });

  // ── 全カレンダーのイベントをAPIで直接取得 ─────────────
  // ブラウザのセッション（Cookie）をそのまま使うので認証不要
  console.log('=== 全カレンダーAPI取得 ===');
  const apiResult = await page.evaluate(async () => {
    const logs   = [];
    const events = [];

    try {
      // カレンダー一覧を取得
      const calRes = await fetch('/api/v2/calendars', {
        credentials: 'include',
        headers: { 'Accept': 'application/json' },
      });
      logs.push('calendars status: ' + calRes.status);
      if (!calRes.ok) {
        logs.push('preview: ' + (await calRes.text()).slice(0, 200));
        return { logs, events };
      }

      const calJson  = await calRes.json();
      const calendars = calJson.data || [];
      logs.push('calendars found: ' + calendars.length);

      for (const cal of calendars) {
        const calId   = cal.id;
        const calName = (cal.attributes && cal.attributes.name) || String(calId);
        logs.push('[CAL] ' + calId + ' : ' + calName);

        // そのカレンダーのイベントを同期取得
        const evRes = await fetch('/api/v1/calendar/' + calId + '/events/sync', {
          credentials: 'include',
          headers: { 'Accept': 'application/json' },
        });
        if (!evRes.ok) {
          logs.push('  → error: ' + evRes.status);
          continue;
        }

        const evJson = await evRes.json();
        const evList = Array.isArray(evJson)       ? evJson
                     : Array.isArray(evJson.data)  ? evJson.data
                     : [];
        logs.push('  → events: ' + evList.length);

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
  });

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
  const response = await fetch(WEBHOOK_URL, {
    method:   'POST',
    headers:  { 'Content-Type': 'application/json' },
    body:     JSON.stringify({ events: output }),
    redirect: 'follow',
  });
  const result = await response.text();
  console.log('GAS レスポンス:', result);
  console.log('完了！');
})();
