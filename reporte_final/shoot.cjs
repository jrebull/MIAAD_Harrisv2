/* Captures screenshots of the Visa Predict AI web app for the LaTeX report. */
const { chromium } = require('playwright');

const OUT = '/Users/haowei/Documents/MIAAD/SMART/Harris2/reporte_final/img';
const BASE = 'http://localhost:3000';

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function shoot(loc, file, opts = {}) {
  try {
    await loc.scrollIntoViewIfNeeded({ timeout: 8000 });
    await sleep(500);
    await loc.screenshot({ path: `${OUT}/${file}`, ...opts });
    console.log('  saved', file);
  } catch (e) {
    console.log('  FAILED', file, '-', e.message.split('\n')[0]);
  }
}

async function main() {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const ctx = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 2,
  });
  const page = await ctx.newPage();
  page.setDefaultTimeout(20000);

  // ---------- LANDING ----------
  console.log('index');
  await page.goto(BASE, { waitUntil: 'networkidle' });
  await sleep(1500);
  await page.screenshot({ path: `${OUT}/index_hero.png` });

  // ---------- PARETO ----------
  console.log('pareto');
  await page.goto(`${BASE}/pareto`, { waitUntil: 'networkidle' });
  await sleep(3000);
  await shoot(page.locator('.card:has(canvas)').first(), 'pareto_scatter.png');
  // 3D pareto is the second chart card
  const paretoCards = page.locator('.card:has(canvas)');
  if (await paretoCards.count() > 1) await shoot(paretoCards.nth(1), 'pareto_3d.png');

  // ---------- CONVERGENCIA ----------
  console.log('convergencia');
  await page.goto(`${BASE}/convergencia`, { waitUntil: 'networkidle' });
  await sleep(3000);
  await shoot(page.locator('.card:has(canvas)').first(), 'convergencia.png');

  // ---------- IMPACTO ----------
  console.log('impacto');
  await page.goto(`${BASE}/impacto`, { waitUntil: 'networkidle' });
  await sleep(3000);
  await shoot(page.locator('.card:has(canvas)').first(), 'impacto.png');

  // ---------- SIMULACION (the star) ----------
  console.log('simulacion');
  await page.goto(`${BASE}/simulacion`, { waitUntil: 'networkidle' });
  await sleep(1500);
  // idle intro panel
  await page.screenshot({ path: `${OUT}/sim_idle.png` });

  // start the run
  await page.getByRole('button', { name: /Iniciar Simulaci/ }).click();
  console.log('  run started, polling progress...');

  // poll progress until mid-run
  const progressLoc = page.locator('text=/\\d+\\s*\\/\\s*\\d+/').first();
  let captured = false;
  for (let i = 0; i < 120; i++) {
    await sleep(400);
    const txt = await page.locator('body').innerText().catch(() => '');
    const m = txt.match(/Iteraci[oó]n\s*(\d+)\s*\/\s*(\d+)/i);
    let frac = 0;
    if (m) frac = parseInt(m[1]) / parseInt(m[2]);
    // capture mid-run between 45% and 72%
    if (!captured && frac >= 0.45 && frac <= 0.75) {
      console.log('  mid-run capture at frac', frac.toFixed(2));
      // dashboard (energy gauge + KPIs)
      await shoot(page.locator('section:has-text("Energía E(t)")').first(), 'sim_dashboard.png');
      // objective race bars
      await shoot(page.locator('section:has-text("Objetivos en Tiempo Real")').first(), 'sim_racebars.png');
      // hawk hunt canvas (root div with direct canvas child)
      await shoot(page.locator('div.relative:has(> canvas)').first(), 'sim_hawkhunt.png');
      captured = true;
    }
    // completion?
    const done = await page.locator('text=Optimización Completada').count().catch(() => 0);
    if (done > 0) { console.log('  completed'); break; }
  }

  // ensure completion
  await page.waitForSelector('text=Optimización Completada', { timeout: 60000 }).catch(() => {});
  await sleep(1500);

  // if mid-run capture missed, grab hawk hunt at completion anyway
  if (!captured) {
    await shoot(page.locator('div.relative:has(> canvas)').first(), 'sim_hawkhunt.png');
    await shoot(page.locator('section:has-text("Objetivos en Tiempo Real")').first(), 'sim_racebars.png');
  }

  // completion panel (MOHHO vs FIFO)
  await shoot(page.locator('section:has-text("MOHHO supera a FIFO")').first(), 'sim_complete.png');
  // hawk hunt final celebration state
  await shoot(page.locator('div.relative:has(> canvas)').first(), 'sim_hawkhunt_final.png');

  // wait for allocation heatmap to load
  await page.waitForSelector('text=Asignación de Visas', { timeout: 30000 }).catch(() => {});
  await sleep(2500);
  await shoot(page.locator('.card:has-text("Asignación: Solución Líder")').first(), 'sim_heatmap.png');
  // mission log
  await shoot(page.locator('section:has-text("Registro de Misión")').first(), 'sim_log.png');

  await browser.close();
  console.log('DONE');
}

main().catch((e) => { console.error(e); process.exit(1); });
