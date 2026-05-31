/* Capture the full MOHHO "hunt" flow (HawkHunt canvas) across phases for section 3.4. */
const { chromium } = require('playwright');
const OUT = '/Users/haowei/Documents/MIAAD/SMART/Harris2/reporte_final/img';
const BASE = 'http://localhost:3000';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  page.setDefaultTimeout(25000);

  await page.goto(BASE + '/simulacion', { waitUntil: 'networkidle' });
  await sleep(1200);

  // set population=40, iterations=220 for a longer, clearer hunt
  const ranges = await page.$$('input[type=range]');
  await ranges[0].evaluate((el) => { el.value = '40'; el.dispatchEvent(new Event('input', { bubbles: true })); });
  await ranges[1].evaluate((el) => { el.value = '220'; el.dispatchEvent(new Event('input', { bubbles: true })); });
  await sleep(300);

  const hawk = page.locator('div.relative:has(> canvas)').first();
  async function grab(name) {
    try { await hawk.scrollIntoViewIfNeeded(); await hawk.screenshot({ path: `${OUT}/${name}.png` }); console.log('  saved', name); }
    catch (e) { console.log('  FAIL', name, e.message.split('\n')[0]); }
  }

  await page.getByRole('button', { name: /Iniciar Simulaci/ }).click();
  console.log('run started (40 hawks, 220 iter)...');

  // capture at target progress fractions
  const targets = [
    [0.06, 'hunt_1_exploracion'],
    [0.22, 'hunt_2_exploracion2'],
    [0.42, 'hunt_3_transicion'],
    [0.63, 'hunt_4_transicion2'],
    [0.83, 'hunt_5_asedio'],
  ];
  let ti = 0;
  for (let i = 0; i < 400 && ti < targets.length; i++) {
    await sleep(250);
    const txt = await page.locator('body').innerText().catch(() => '');
    const m = txt.match(/Iteraci[oó]n\s*(\d+)\s*\/\s*(\d+)/i);
    const frac = m ? parseInt(m[1]) / parseInt(m[2]) : 0;
    if (frac >= targets[ti][0]) { console.log(`  frac ${frac.toFixed(2)} ->`, targets[ti][1]); await grab(targets[ti][1]); ti++; }
    if (await page.locator('text=Optimización Completada').count().catch(() => 0)) break;
  }

  // completion / capture frame
  await page.waitForSelector('text=Optimización Completada', { timeout: 90000 }).catch(() => {});
  await sleep(900);
  await grab('hunt_6_captura');

  await browser.close();
  console.log('DONE');
}
main().catch((e) => { console.error(e); process.exit(1); });
