#!/usr/bin/env node
/**
 * dl.mjs — ดาวน์โหลดไฟล์ผ่าน UI จริง โดยกำหนดโฟลเดอร์ปลายทางผ่าน CDP
 * ใช้เมื่อปุ่มเป็นลิงก์ที่ browser ไม่ยอม save ลง path ที่เราต้องการ
 *
 * ใช้: node dl.mjs "<selector>" "<โฟลเดอร์ปลายทาง>"
 */
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const [, , sel, dir] = process.argv;
const browser = await chromium.connectOverCDP(process.env.CDP || 'http://127.0.0.1:9222');
const page = browser.contexts()[0].pages().at(-1);

const before = new Set(fs.existsSync(dir) ? fs.readdirSync(dir) : []);
const cdp = await browser.newBrowserCDPSession();
await cdp.send('Browser.setDownloadBehavior', { behavior: 'allow', downloadPath: dir, eventsEnabled: true });

await page.bringToFront();
await page.locator(sel).first().click({ timeout: 15000 });
console.log('clicked:', sel);

let found = null;
for (let i = 0; i < 40; i++) {
  await new Promise(r => setTimeout(r, 500));
  const now = fs.existsSync(dir) ? fs.readdirSync(dir) : [];
  const fresh = now.filter(f => !before.has(f) && !f.endsWith('.crdownload'));
  if (fresh.length) { found = fresh[0]; break; }
}
console.log(found ? `FILE: ${found} ${fs.statSync(path.join(dir, found)).size} bytes` : 'NO_FILE');
await browser.close();
