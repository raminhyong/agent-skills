import { chromium } from 'playwright';

const targetSpeed = process.argv[2] || '2x';
const speedText = targetSpeed.endsWith('x') ? targetSpeed : `${targetSpeed}x`;

const browser = await chromium.connectOverCDP(process.env.CDP || 'http://127.0.0.1:9222');
const page = browser.contexts()[0].pages().at(-1);

console.log(`Setting video playback speed to ${speedText}...`);

// 1. Move mouse over video to activate controls
const video = page.locator('video').first();
const vb = await video.boundingBox();
if (vb) {
  await page.mouse.move(vb.x + vb.width / 2, vb.y + vb.height - 30);
  await page.waitForTimeout(500);
}

// 2. Find and hover over Speed button
const speedBtn = page.locator('div.xgplayer-icon:has(span.icon-text:text-is("Speed")), [class*="playbackrate"]').first();
const sb = await speedBtn.boundingBox().catch(() => null);
if (sb) {
  await page.mouse.move(sb.x + sb.width / 2, sb.y + sb.height / 2);
  await page.waitForTimeout(600);
}

// 3. Click the desired speed option
const speedOption = page.locator(`li.option-item:has-text("${speedText}"), [class*="item"]:has-text("${speedText}")`).first();
const tb = await speedOption.boundingBox().catch(() => null);
if (tb) {
  await page.mouse.move(tb.x + tb.width / 2, tb.y + tb.height / 2);
  await page.waitForTimeout(200);
  await page.mouse.down();
  await page.mouse.up();
  console.log(`Clicked ${speedText} on screen via mouse!`);
} else {
  // Direct click if visible
  await speedOption.click().catch(() => {});
}

await page.waitForTimeout(800);
const rate = await page.$eval('video', v => v.playbackRate).catch(() => null);
console.log(`Current video playbackRate: ${rate}`);

await browser.close();
