const { chromium } = require('playwright');

const formData = {
  name:     '田中悠清',
  furigana: 'タナカ ユウセイ',
  company:  'Emport AI',
  tel:      '080-2947-0736',
  email:    'yuubisinesu@gmail.com',
  body: `はじめてご連絡いたします。
山口県を拠点に、中小企業向けのAI活用支援での起業を目指している
Emport AI（個人事業主）の田中悠清と申します。

山口県内の中小企業様のお役に立てないかと活動を始めたばかりで、
まずは地域の支援機関の皆様にご挨拶とご意見を伺えればと思い、
ご連絡させていただきました。

もしよろしければ、15〜20分ほどお時間をいただき、
担当の方にお話を聞いていただける機会をいただけますと幸いです。
対面・オンラインいずれでも対応可能です。

お忙しいところ恐れ入りますが、どうぞよろしくお願いいたします。

━━━━━━━━━━━━━━━━━━
Emport AI
田中悠清
Email: yuubisinesu@gmail.com
TEL: 080-2947-0736
山口県山口市黒川995-1
━━━━━━━━━━━━━━━━━━`
};

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 300 });
  const page = await browser.newPage();

  console.log('お問い合わせページへアクセス中...');
  await page.goto('https://yipf.or.jp/contact/', { waitUntil: 'networkidle' });

  // name属性で直接指定（フィールド構成が判明済み）
  await page.locator('input[name="お名前"]').fill(formData.name);
  console.log('お名前 ✅');

  await page.locator('input[name="お名前（フリガナ）"]').fill(formData.furigana);
  console.log('フリガナ ✅');

  await page.locator('input[name="会社名・団体名"]').fill(formData.company);
  console.log('会社名・団体名 ✅');

  await page.locator('input[name="電話番号"]').fill(formData.tel);
  console.log('電話番号 ✅');

  await page.locator('input[name="mail"]').fill(formData.email);
  console.log('メールアドレス ✅');

  await page.locator('input[name="mail2"]').fill(formData.email);
  console.log('メールアドレス（確認用）✅');

  await page.locator('textarea[name="内容"]').fill(formData.body);
  console.log('お問い合わせ内容 ✅');

  // 個人情報同意チェックボックス
  const checkbox = page.locator('input[name="同意[data][]"]');
  if (await checkbox.count() > 0) {
    await checkbox.check();
    console.log('同意チェックボックス ✅');
  }

  // トップにスクロールしてスクリーンショット
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(600);
  await page.screenshot({ path: 'tools/form-screenshot-top.png' });

  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(600);
  await page.screenshot({ path: 'tools/form-screenshot-bottom.png' });

  console.log('\n✅ 全フィールド入力完了！送信ボタンの手前で停止中です。');
  console.log('ブラウザを確認して送信してください。Enterで閉じます...');

  await new Promise(resolve => process.stdin.once('data', resolve));
  await browser.close();
})();
