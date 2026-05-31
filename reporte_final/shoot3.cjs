/* Capture a uniform viewport screenshot of every web-app section for the report gallery. */
const { chromium } = require('playwright');
const OUT = '/Users/haowei/Documents/MIAAD/SMART/Harris2/reporte_final/img';
const BASE = 'http://localhost:3000';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const PAGES = [
  ['/',             'gallery_index'],
  ['/modelo',       'gallery_modelo'],
  ['/algoritmo',    'gallery_algoritmo'],
  ['/pareto',       'gallery_pareto'],
  ['/asignacion',   'gallery_asignacion'],
  ['/impacto',      'gallery_impacto'],
  ['/convergencia', 'gallery_convergencia'],
  ['/datos',        'gallery_datos'],
  ['/analisis',     'gallery_analisis'],
];

async function main() {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  page.setDefaultTimeout(25000);

  for (const [route, name] of PAGES) {
    try {
      await page.goto(BASE + route, { waitUntil: 'networkidle' });
      await sleep(3000);                      // let charts/tables render
      await page.evaluate(() => window.scrollTo(0, 0));
      await sleep(400);
      await page.screenshot({ path: `${OUT}/${name}.png` });
      console.log('  saved', name);
    } catch (e) { console.log('  FAILED', name, '-', e.message.split('\n')[0]); }
  }

  // simulacion: capture a live, mid-run viewport
  try {
    await page.goto(BASE + '/simulacion', { waitUntil: 'networkidle' });
    await sleep(1200);
    await page.getByRole('button', { name: /Iniciar Simulaci/ }).click();
    await sleep(8000);                        // ~22 iterations in
    await page.evaluate(() => window.scrollTo(0, 0));
    await sleep(400);
    await page.screenshot({ path: `${OUT}/gallery_simulacion.png` });
    console.log('  saved gallery_simulacion');
  } catch (e) { console.log('  FAILED gallery_simulacion -', e.message.split('\n')[0]); }

  await browser.close();
  console.log('DONE');
}
main().catch((e) => { console.error(e); process.exit(1); });
