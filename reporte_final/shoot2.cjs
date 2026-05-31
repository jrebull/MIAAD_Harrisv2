/* Re-capture completion panel + allocation heatmap from the live simulation. */
const { chromium } = require('playwright');
const OUT = '/Users/haowei/Documents/MIAAD/SMART/Harris2/reporte_final/img';
const BASE = 'http://localhost:3000';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function shoot(loc, file) {
  try {
    await loc.scrollIntoViewIfNeeded({ timeout: 8000 });
    await sleep(600);
    await loc.screenshot({ path: `${OUT}/${file}` });
    console.log('  saved', file);
  } catch (e) { console.log('  FAILED', file, '-', e.message.split('\n')[0]); }
}

async function main() {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  page.setDefaultTimeout(20000);

  await page.goto(`${BASE}/simulacion`, { waitUntil: 'networkidle' });
  await sleep(1200);
  await page.getByRole('button', { name: /Iniciar Simulaci/ }).click();
  console.log('run started...');

  await page.waitForSelector('text=Pareto-óptimas encontradas', { timeout: 90000 }).catch(() => {});
  await sleep(1500);

  // completion panel (unique subtitle phrase)
  await shoot(page.locator('section:has-text("Pareto-óptimas encontradas")').first(), 'sim_complete.png');

  // allocation: wait for header DOM text, then grab the last canvas-card (heatmap)
  await page.waitForSelector('text=Asignación de Visas', { timeout: 30000 }).catch(() => {});
  await sleep(3000);
  await shoot(page.locator('.card:has(canvas)').last(), 'sim_heatmap.png');
  // header card with fitness summary too
  await shoot(page.locator('.card:has-text("Asignación de Visas")').first(), 'sim_alloc_header.png');

  await browser.close();
  console.log('DONE');
}
main().catch((e) => { console.error(e); process.exit(1); });
