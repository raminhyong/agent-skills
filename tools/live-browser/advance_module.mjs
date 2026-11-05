import { chromium } from 'playwright';

const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
const page = browser.contexts()[0].pages().at(-1);

console.log('Monitoring current video to finish...');

// 1. Wait for "ต้องการเรียนบทถัดไป" button
const nextBtn = page.locator('button:has-text("ต้องการเรียนบทถัดไป")').first();

let count = 0;
while (count < 60) { // up to 2 mins max
  if (await nextBtn.isVisible().catch(() => false)) {
    console.log('Next chapter dialog detected!');
    break;
  }
  const status = await page.evaluate(() => {
    const v = document.querySelector('video');
    return v ? { ct: Math.round(v.currentTime), dur: Math.round(v.duration), ended: v.ended } : null;
  }).catch(() => null);
  
  if (status && status.ended) {
    console.log('Video ended.');
    await page.waitForTimeout(1500);
    if (await nextBtn.isVisible().catch(() => false)) break;
  }
  
  await page.waitForTimeout(2000);
  count++;
}

// 2. Click "ต้องการเรียนบทถัดไป"
if (await nextBtn.isVisible().catch(() => false)) {
  console.log('Clicking "ต้องการเรียนบทถัดไป"...');
  await page.waitForTimeout(1500);
  await nextBtn.click();
  await page.waitForTimeout(3000);
} else {
  console.log('Dialog not visible after wait.');
}

// 3. Check what is active now
const currentModule = await page.evaluate(() => {
  const activeItem = document.querySelector('.course-item.active, [class*="active"]');
  const v = document.querySelector('video');
  const h1 = document.querySelector('h1, h2, h3');
  return {
    heading: h1 ? h1.innerText.trim() : null,
    videoDuration: v ? Math.round(v.duration) : null,
    url: location.href
  };
});
console.log('Current state:', JSON.stringify(currentModule));

// 4. Set speed to 2x if video is present
const video = page.locator('video').first();
if (await video.count()) {
  const vb = await video.boundingBox();
  if (vb) {
    await page.mouse.move(vb.x + vb.width / 2, vb.y + vb.height - 30);
    await page.waitForTimeout(500);
  }
  const speedBtn = page.locator('div.xgplayer-icon:has(span.icon-text:text-is("Speed"))').first();
  const sb = await speedBtn.boundingBox().catch(() => null);
  if (sb) {
    await page.mouse.move(sb.x + sb.width / 2, sb.y + sb.height / 2);
    await page.waitForTimeout(600);
    const twoX = page.locator('li.option-item:has-text("2x")').first();
    const tb = await twoX.boundingBox().catch(() => null);
    if (tb) {
      await page.mouse.move(tb.x + tb.width / 2, tb.y + tb.height / 2);
      await page.waitForTimeout(200);
      await page.mouse.down();
      await page.mouse.up();
      console.log('Speed set to 2x for new module!');
    }
  }
  await page.waitForTimeout(500);
  const rate = await page.$eval('video', v => v.playbackRate);
  console.log('New playback rate:', rate);
}

await browser.close();

