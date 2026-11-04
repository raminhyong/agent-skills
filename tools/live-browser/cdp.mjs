#!/usr/bin/env node
/**
 * cdp.mjs — CLI ขนาดเล็กสำหรับคุมแท็บที่เปิดอยู่ผ่าน CDP (ไม่ต้องใช้ Playwright API เต็ม)
 * ใช้เมื่ออยากได้คำสั่งสั้น ๆ: status | goto <url> | shot <file> | text | eval "<js>"
 * (pw.mjs คือตัวเต็ม — ใช้ cdp.mjs เป็นตัวสำรองเวลาต้องการเร็ว ๆ)
 */
import { chromium } from 'playwright';

const [, , cmd, arg] = process.argv;
const ENDPOINT = process.env.CDP || 'http://127.0.0.1:9222';

const browser = await chromium.connectOverCDP(ENDPOINT);
const ctx = browser.contexts()[0];
const pages = ctx.pages();
const match = process.env.PW_MATCH || '';
let page = match ? pages.find(p => p.url().includes(match)) : pages[pages.length - 1];

try {
  if (cmd === 'status') {
    console.log(JSON.stringify({ pages: pages.length, urls: pages.map(p => p.url()) }));
  } else if (cmd === 'goto') {
    if (!page) page = await ctx.newPage();
    await page.goto(arg, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(1500);
    console.log('title:', await page.title());
    console.log('url:', page.url());
  } else if (cmd === 'shot') {
    if (!page) page = await ctx.newPage();
    await page.screenshot({ path: arg || 'shot.png' });
    console.log('saved:', arg || 'shot.png');
  } else if (cmd === 'text') {
    if (!page) page = await ctx.newPage();
    console.log((await page.innerText('body')).slice(0, 4000));
  } else if (cmd === 'eval') {
    if (!page) page = await ctx.newPage();
    console.log(JSON.stringify(await page.evaluate(arg)));
  } else {
    console.log('usage: status|goto <url>|shot <file>|text|eval "<js>"');
  }
} finally {
  await browser.close();
}
