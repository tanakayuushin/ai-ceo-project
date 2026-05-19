#!/usr/bin/env python3
"""
月次カレンダー画像生成 & LINE Notify 送信スクリプト

使い方:
  python calendar_image.py              # 当月
  python calendar_image.py 2026 6       # 指定月

環境変数 (.env に書くか OS に設定):
  LINE_NOTIFY_TOKEN  LINE Notifyのトークン
  GOOGLE_SHEET_ID    スプレッドシートID
  GOOGLE_CREDS_JSON  サービスアカウントJSONのパス（省略時はOAuth）
"""

import asyncio, calendar, os, sys
from datetime import date, timedelta
from pathlib import Path

import requests


# ── Google Sheets から予定を取得 ──────────────────────────

def load_events(sheet_id: str, creds_path: str = '') -> dict:
    """{day: [{name, time}, ...]} 形式で当月の予定を返す"""
    try:
        import gspread
        if creds_path and Path(creds_path).exists():
            gc = gspread.service_account(filename=creds_path)
        else:
            gc = gspread.oauth()
        ws = gc.open_by_key(sheet_id).worksheet('events')
        rows = ws.get_all_values()[1:]
    except Exception as e:
        print(f'[WARN] Sheets読み込み失敗: {e}')
        return {}

    today = date.today()
    events: dict = {}
    for row in rows:
        if len(row) < 3:
            continue
        name, date_str, time_str = str(row[0]).strip(), str(row[1]).strip(), str(row[2]).strip()
        reminded = row[6].strip() if len(row) > 6 else ''
        if reminded == 'done' or not name:
            continue

        d = None
        for fmt in ('%Y/%m/%d', '%Y-%m-%d'):
            try:
                d = date(*[int(x) for x in date_str.replace('/', '-').split('-')])
                break
            except Exception:
                pass
        if not d or d.year != today.year or d.month != today.month:
            continue

        # 時刻を "H:MM" 形式に正規化（小数の場合も対処）
        t_str = ''
        try:
            val = float(time_str)
            mins = round(val * 24 * 60)
            t_str = f'{mins // 60}:{mins % 60:02d}'
        except ValueError:
            if ':' in time_str:
                parts = time_str.split(':')
                t_str = f'{int(parts[0])}:{parts[1]}'

        if d.day not in events:
            events[d.day] = []
        events[d.day].append({'name': name, 't': t_str})

    return events


# ── HTML カレンダー生成 ────────────────────────────────────

MONTH_EN = ['', 'JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE',
            'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']


def build_html(year: int, month: int, events: dict) -> str:
    today     = date.today()
    first     = date(year, month, 1)
    total     = calendar.monthrange(year, month)[1]
    # 日曜始まり: weekday() 0=Mon 6=Sun → SunFirst 0=Sun
    first_dow = (first.weekday() + 1) % 7
    start     = first - timedelta(days=first_dow)
    num_weeks = 6 if (first_dow + total) > 35 else 5

    rows = ''
    cur  = start
    for _ in range(num_weeks):
        rows += '<tr>'
        for dow in range(7):
            is_cur   = cur.month == month
            is_today = cur == today
            is_sun   = dow == 0
            is_sat   = dow == 6

            num_cls = ('gray' if not is_cur
                       else 'red bold' if is_today
                       else 'red'  if is_sun
                       else 'blue' if is_sat
                       else '')
            td_cls  = 'day' + ('' if is_cur else ' other') + (' today' if is_today else '')

            ev_html = ''
            if is_cur and cur.day in events:
                for ev in events[cur.day]:
                    t = f'<div class="ev-t">{ev["t"]}~</div>' if ev['t'] else ''
                    ev_html += f'<div class="ev"><div class="ev-n">{ev["name"]}</div>{t}</div>'

            rows += f'<td class="{td_cls}"><span class="n {num_cls}">{cur.day}</span>{ev_html}</td>'
            cur  += timedelta(days=1)
        rows += '</tr>'

    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:700px;background:#ccddd4;font-family:"Helvetica Neue",Arial,sans-serif;padding:36px 32px 28px}}
.hdr{{display:flex;align-items:flex-start;margin-bottom:22px}}
.hl{{flex:1}}.hy{{font-size:28px;font-weight:900;color:#1a5c3a;line-height:1}}
.hlb{{font-size:10px;font-weight:700;color:#1a5c3a;letter-spacing:2px;margin-top:4px}}
.hm{{text-align:center;flex:1.2}}
.mn{{font-size:80px;font-weight:900;color:#1a5c3a;line-height:1;letter-spacing:-2px}}
.me{{font-size:13px;font-weight:700;color:#1a5c3a;letter-spacing:4px;margin-top:2px}}
table{{width:100%;border-collapse:collapse}}
.dh th{{background:#1a5c3a;color:#fff;font-size:11px;font-weight:700;
        letter-spacing:1px;padding:9px 0;text-align:center}}
td.day{{background:#f5f0e4;height:108px;width:calc(100%/7);vertical-align:top;
        padding:7px 6px 5px;border:1.5px solid #ccddd4}}
td.other{{background:#eae5d8;height:108px;vertical-align:top;
          padding:7px 6px 5px;border:1.5px solid #ccddd4}}
td.today{{box-shadow:inset 0 0 0 2.5px #1a5c3a}}
.n{{font-size:16px;font-weight:600;color:#2d2d2d;display:block;margin-bottom:3px}}
.n.gray{{color:#bbb;font-weight:400}}.n.red{{color:#c0392b}}.n.blue{{color:#2471a3}}
.n.bold{{font-weight:900}}
.ev{{background:#1a5c3a;color:#fff;border-radius:4px;padding:4px 6px;margin-top:3px}}
.ev-n{{font-size:11px;font-weight:700;word-break:break-all;line-height:1.35}}
.ev-t{{font-size:9.5px;opacity:.9;margin-top:1px}}
.ft{{text-align:center;margin-top:14px;font-size:11px;font-weight:700;color:#1a5c3a;letter-spacing:3px}}
</style></head>
<body>
<div class="hdr">
  <div class="hl"><div class="hy">{year}</div><div class="hlb">MONTHLY CALENDAR</div></div>
  <div class="hm"><div class="mn">{month:02d}</div><div class="me">{MONTH_EN[month]}</div></div>
  <div style="flex:1"></div>
</div>
<table>
  <tr class="dh"><th>SUN</th><th>MON</th><th>TUE</th><th>WED</th><th>THU</th><th>FRI</th><th>SAT</th></tr>
  {rows}
</table>
<div class="ft">LINE REMINDER</div>
</body></html>'''


# ── Playwright で PNG レンダリング ────────────────────────

async def render_png(html: str) -> bytes:
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page    = await browser.new_page(viewport={'width': 700, 'height': 900})
        await page.set_content(html, wait_until='networkidle')
        await page.wait_for_timeout(300)
        png = await page.screenshot(full_page=True)
        await browser.close()
    return png


# ── LINE Notify で送信 ────────────────────────────────────

def send_line_notify(png: bytes, token: str, msg: str = '\n📅 今月のカレンダー') -> int:
    r = requests.post(
        'https://notify-api.line.me/api/notify',
        headers={'Authorization': f'Bearer {token}'},
        data={'message': msg},
        files={'imageFile': ('calendar.png', png, 'image/png')},
    )
    return r.status_code


# ── メイン ───────────────────────────────────────────────

async def main():
    today  = date.today()
    year   = int(sys.argv[1]) if len(sys.argv) > 1 else today.year
    month  = int(sys.argv[2]) if len(sys.argv) > 2 else today.month

    # .env 読み込み（python-dotenv がなくてもOK）
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).parent / '.env')
    except ImportError:
        pass

    token      = os.environ.get('LINE_NOTIFY_TOKEN', '')
    sheet_id   = os.environ.get('GOOGLE_SHEET_ID', '')
    creds_path = os.environ.get('GOOGLE_CREDS_JSON', '')

    print(f'[INFO] {year}年{month}月のカレンダーを生成中...')
    events = load_events(sheet_id, creds_path) if sheet_id else {}
    print(f'[INFO] 予定: {sum(len(v) for v in events.values())}件')

    html = build_html(year, month, events)
    png  = await render_png(html)

    out = Path(__file__).parent / f'calendar_{year}_{month:02d}.png'
    out.write_bytes(png)
    print(f'[INFO] 保存: {out}')

    if token:
        code = send_line_notify(png, token)
        print(f'[INFO] LINE Notify 送信: HTTP {code}')
    else:
        print('[WARN] LINE_NOTIFY_TOKEN 未設定 → 画像のみ保存（送信スキップ）')


if __name__ == '__main__':
    asyncio.run(main())
