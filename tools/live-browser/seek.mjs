#!/usr/bin/env node
/**
 * seek.mjs — กรอวิดีโอ JW Player ไปปลายคลิป "ด้วยการคลิกแถบเวลาจริง" แล้วกดปุ่มต่อ
 *
 * ใช้กับคอร์สออนไลน์ที่ปล่อยวิดีโอยาว (KU MOOC ฯลฯ) เมื่อผู้ใช้สั่งให้เร็วขึ้น
 * หลักการ: ขยับเมาส์ให้คอนโทรลโผล่ → หาแถบเวลา → คลิกที่ตำแหน่ง ratio ของความกว้าง
 *          (เป็นการคลิก UI จริง ไม่ใช่การแก้ currentTime ผ่าน JS)
 *
 * ใช้: node seek.mjs [ratio=0.97] [ปุ่มต่อ="btn-continue-playing"]
 */
import { chromium } from 'playwright';

const ratio = Number(process.argv[2] || 0.97);
const nextBtn = process.argv[3] || 'button.btn-continue-playing';

const browser = await chromium.connectOverCDP(process.env.CDP || 'http://127.0.0.1:9222');
const page = browser.contexts()[0].pages().at(-1);
await page.bringToFront();

const v = page.locator('video').first();
const vb = await v.boundingBox();
if (!vb) { console.log('NO_VIDEO'); await browser.close(); process.exit(1); }

// ทำให้คอนโทรลโผล่ (JW Player ซ่อนเมื่อไม่ hover)
await page.mouse.move(vb.x + vb.width / 2, vb.y + vb.height / 2);
await page.waitForTimeout(600);
await page.mouse.move(vb.x + vb.width / 2, vb.y + vb.height - 30);
await page.waitForTimeout(800);

let bar = page.locator('.jw-progress, .jw-slider-time, [class*="jw-slider"]').first();
let bb = await bar.boundingBox().catch(() => null);
if (!bb) {
  const controls = page.locator('.jw-controls').first();
  bb = await controls.boundingBox().catch(() => null);
  if (!bb) { console.log('NO_SEEKBAR'); await browser.close(); process.exit(1); }
  bb = { x: bb.x, y: bb.y + bb.height - 12, width: bb.width, height: 8 };
}

await page.mouse.move(bb.x + bb.width * ratio, bb.y + bb.height / 2);
await page.waitForTimeout(300);
await page.mouse.down();
await page.mouse.up();
await page.waitForTimeout(1500);

console.log('AFTER_SEEK', JSON.stringify(await v.evaluate(el => ({ ct: Math.round(el.currentTime), dur: Math.round(el.duration), ended: el.ended }))));

// รอ dialog "เรียนจบ" แล้วกดต่อ (สูงสุด ~90 วิ)
for (let i = 0; i < 45; i++) {
  if (await page.locator(nextBtn).count()) {
    await page.waitForTimeout(2500 + Math.random() * 2000);
    await page.locator(nextBtn).first().click();
    await page.waitForTimeout(3000);
    break;
  }
  await page.waitForTimeout(2000);
}

console.log('NOW', JSON.stringify(await page.evaluate(() => {
  const v = document.querySelector('video');
  return { url: location.href, dur: v ? Math.round(v.duration) : null, ct: v ? Math.round(v.currentTime) : null };
})));
await browser.close();
