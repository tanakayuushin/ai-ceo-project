#!/usr/bin/env python3
"""
月次カレンダー画像生成 & LINE Messaging API 送信スクリプト

使い方:
  python calendar_image.py              # 当月
  python calendar_image.py 2026 6       # 指定月

.env に設定する値:
  LINE_CHANNEL_TOKEN  GASのスクリプトプロパティ LINE_TOKEN の値
  LINE_GROUP_ID       GASのスクリプトプロパティ LINE_GROUP_ID の値
  IMGUR_CLIENT_ID     Imgur の Client-ID（https://api.imgur.com/oauth2/addclient で取得）
  GOOGLE_SHEET_ID     スプレッドシートID（任意）
  GOOGLE_CREDS_JSON   サービスアカウントJSONのパス（任意）
"""

import asyncio, calendar, os, sys
from datetime import date, timedelta
from pathlib import Path

import requests


# ── GAS ウェブアプリから予定を取得 ──────────────────────

def load_events(gas_url: str, year: int, month: int) -> dict:
    """{day: [{name, t}, ...]} 形式で予定を返す"""
    if not gas_url:
        print('[WARN] GAS_WEB_APP_URL 未設定 → 予定なしで生成')
        return {}
    try:
        r = requests.get(
            gas_url,
            params={'action': 'events', 'year': year, 'month': month},
            timeout=15,
        )
        r.raise_for_status()
        rows = r.json()
    except Exception as e:
        print(f'[WARN] 予定取得失敗: {e}')
        return {}

    events: dict = {}
    for row in rows:
        day      = int(row.get('day', 0))
        name     = str(row.get('name', '')).strip()
        time_str = str(row.get('time', '')).strip()
        if not day or not name:
            continue

        # 時刻の正規化
        t_str = ''
        try:
            val  = float(time_str)
            mins = round(val * 24 * 60)
            t_str = f'{mins // 60}:{mins % 60:02d}'
        except ValueError:
            if ':' in time_str:
                h, m = time_str.split(':')[:2]
                t_str = f'{int(h)}:{m}'

        events.setdefault(day, []).append({'name': name, 't': t_str})

    print(f'[INFO] 予定取得: {sum(len(v) for v in events.values())}件')
    return events


# ── HTML カレンダー生成 ────────────────────────────────────

MONTH_EN = ['', 'JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE',
            'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']


def build_html(year: int, month: int, events: dict) -> str:
    today     = date.today()
    first     = date(year, month, 1)
    total     = calendar.monthrange(year, month)[1]
    first_dow = (first.weekday() + 1) % 7   # 日曜始まり: 0=Sun
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
                       else 'red'      if is_sun
                       else 'blue'     if is_sat
                       else '')
            td_cls = 'day' + ('' if is_cur else ' other') + (' today' if is_today else '')

            ev_html = ''
            if is_cur and cur.day in events:
                for ev in events[cur.day]:
                    t_tag = f'<div class="ev-t">{ev["t"]}~</div>' if ev['t'] else ''
                    ev_html += f'<div class="ev"><div class="ev-n">{ev["name"]}</div>{t_tag}</div>'

            rows += (f'<td class="{td_cls}">'
                     f'<span class="n {num_cls}">{cur.day}</span>'
                     f'{ev_html}</td>')
            cur += timedelta(days=1)
        rows += '</tr>'

    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:700px;background:#ccddd4;font-family:"Helvetica Neue",Arial,sans-serif;padding:36px 32px 28px}}
.hdr{{display:flex;align-items:flex-start;margin-bottom:22px}}
.hl{{flex:1}}
.hy{{font-size:28px;font-weight:900;color:#1a5c3a;line-height:1}}
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
.n.gray{{color:#bbb;font-weight:400}}
.n.red{{color:#c0392b}}
.n.blue{{color:#2471a3}}
.n.bold{{font-weight:900}}
.ev{{background:#1a5c3a;color:#fff;border-radius:4px;padding:4px 6px;margin-top:3px}}
.ev-n{{font-size:11px;font-weight:700;word-break:break-all;line-height:1.35}}
.ev-t{{font-size:9.5px;opacity:.9;margin-top:1px}}
.ft{{text-align:center;margin-top:14px;font-size:11px;font-weight:700;
     color:#1a5c3a;letter-spacing:3px}}
</style></head>
<body>
<div class="hdr">
  <div class="hl"><div class="hy">{year}</div><div class="hlb">MONTHLY CALENDAR</div></div>
  <div class="hm"><div class="mn">{month:02d}</div><div class="me">{MONTH_EN[month]}</div></div>
  <div style="flex:1"></div>
</div>
<table>
  <tr class="dh">
    <th>SUN</th><th>MON</th><th>TUE</th><th>WED</th><th>THU</th><th>FRI</th><th>SAT</th>
  </tr>
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


# ── catbox.moe に画像をアップロード → 公開URL取得（登録不要）──

def upload_image(png: bytes) -> str:
    r = requests.post(
        'https://catbox.moe/user/api.php',
        data={'reqtype': 'fileupload'},
        files={'fileToUpload': ('calendar.png', png, 'image/png')},
        timeout=30,
    )
    r.raise_for_status()
    return r.text.strip()   # https://files.catbox.moe/xxxxxx.png


# ── LINE Messaging API で画像を送信 ──────────────────────

def send_line_image(image_url: str, token: str, group_id: str) -> int:
    r = requests.post(
        'https://api.line.me/v2/bot/message/push',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type':  'application/json',
        },
        json={
            'to': group_id,
            'messages': [{
                'type':               'image',
                'originalContentUrl': image_url,
                'previewImageUrl':    image_url,
            }],
        },
        timeout=30,
    )
    return r.status_code


# ── メイン ───────────────────────────────────────────────

async def main():
    today  = date.today()
    year   = int(sys.argv[1]) if len(sys.argv) > 1 else today.year
    month  = int(sys.argv[2]) if len(sys.argv) > 2 else today.month

    # .env 読み込み
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).parent / '.env')
    except ImportError:
        pass

    line_token = os.environ.get('LINE_CHANNEL_TOKEN', '')
    group_id   = os.environ.get('LINE_GROUP_ID', '')
    gas_url    = os.environ.get('GAS_WEB_APP_URL', '')

    print(f'[INFO] {year}年{month}月のカレンダーを生成中...')
    events = load_events(gas_url, year, month)

    # PNG 生成
    html = build_html(year, month, events)
    png  = await render_png(html)

    # ローカル保存
    out = Path(__file__).parent / f'calendar_{year}_{month:02d}.png'
    out.write_bytes(png)
    print(f'[INFO] 保存: {out}')

    # catbox.moe にアップロード
    print('[INFO] catbox.moe にアップロード中...')
    image_url = upload_image(png)
    print(f'[INFO] URL: {image_url}')

    # LINE 送信
    if not line_token or not group_id:
        print('[WARN] LINE_CHANNEL_TOKEN または LINE_GROUP_ID 未設定 → 送信スキップ')
        return

    code = send_line_image(image_url, line_token, group_id)
    print(f'[INFO] LINE 送信: HTTP {code}')
    if code == 200:
        print('[INFO] 送信完了!')
    else:
        print(f'[ERROR] 送信失敗 (HTTP {code})')


if __name__ == '__main__':
    asyncio.run(main())
