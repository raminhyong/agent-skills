#!/usr/bin/env node
/**
 * pw.mjs — Playwright ที่ "เกาะ" Chrome ที่มีหน้าต่างจริงผ่าน CDP (ไม่เปิดเบราว์เซอร์ใหม่)
 *
 * หลักการ: live.sh เปิด Chrome (มีหน้าต่าง + โปรไฟล์ถาวร + CDP port) → สคริปต์นี้
 * connectOverCDP เข้าไปสั่งงานบนแท็บเดิม ทุกคลิก/พิมพ์/ถ่ายภาพจึงเกิดบนหน้าจอจริง
 * จบแล้ว `browser.close()` แค่ตัดการเชื่อมต่อ หน้าต่างยังเปิดอยู่
 *
 * สิ่งแวดล้อม:
 *   CDP=http://127.0.0.1:9222   ปลายทาง CDP
 *   PW_MATCH=reddit             เลือกแท็บที่มี URL ตรงคำนี้ (ถ้าเปิดหลายแท็บ)
 *
 * คำสั่ง:
 *   status                        แท็บทั้งหมด + title
 *   goto <url>                    เปิด/ย้ายแท็บปัจจุบัน
 *   shot <file>                   ภาพเฉพาะ viewport
 *   fullshot <file>               ภาพเต็มหน้า
 *   text                          อ่าน innerText (4000 ตัวอักษรแรก)
 *   click "<ข้อความ>"             คลิกด้วยข้อความ (ปุ่ม/ลิงก์/ตัวเลือก) — เมาส์จริงเท่านั้น
 *   clickjs "<ข้อความ>"           คลิกด้วย JS (เฉพาะงานทั่วไป ห้ามใช้ในห้องสอบ)
 *   clickcss "<selector>"         คลิกด้วย CSS selector
 *   fill "<label|placeholder>" "<ข้อความ>"
 *   press <key>                   Enter / Escape / Tab ...
 *   wait <ms>
 *   eval "<js expression>"
 *   links                         ลิงก์ทั้งหมด (text → href)
 *   buttons                       ปุ่มที่มองเห็น (text + พิกัดกลาง)
 *   download "<ข้อความปุ่ม>" <path>   รอดาวน์โหลดแล้ว saveAs
 *   fetchsave <url> <path>        ดึงไฟล์ที่ปุ่มเว็บเสิร์ฟด้วยคุกกี้ของแท็บ (ใช้เมื่อ download ไม่ทำงาน)
 */
import { chromium } from 'playwright';
import fs from 'fs';

const [, , cmd, a1, a2] = process.argv;
const ENDPOINT = process.env.CDP || 'http://127.0.0.1:9222';

const browser = await chromium.connectOverCDP(ENDPOINT);
const ctx = browser.contexts()[0];
const pages = ctx.pages();
const match = process.env.PW_MATCH || '';
let page = match ? pages.find(p => p.url().includes(match)) : pages[pages.length - 1];
const out = (...x) => console.log(...x);

async function need() {
  if (!page) page = await ctx.newPage();
  await page.bringToFront().catch(() => {});
  return page;
}

/** หา locator จากข้อความ: text → role=button → role=link → placeholder */
async function byText(p, t) {
  const cands = [
    p.getByText(t, { exact: false }).filter({ visible: true }).first(),
    p.getByRole('button', { name: t }).first(),
    p.getByRole('link', { name: t }).first(),
  ];
  for (const c of cands) if (await c.count()) return c;
  return null;
}

/** ---------- Cursor overlay (ให้เจ๊เห็นว่า agent ชี้ตรงไหน) ---------- */
const CURSOR_ON = (process.env.PW_CURSOR ?? '1') !== '0';
const CURSOR_LABEL = process.env.PW_CURSOR_LABEL ?? 'แพนเค้ก';

async function cursorInject(page) {
  await page.evaluate(({ label, v }) => {
    const old = document.getElementById('__hermes_cursor');
    if (old && window.__hc && window.__hc.v === v) return;
    const px = window.__hc ? window.__hc.x : 0, py = window.__hc ? window.__hc.y : 0;
    if (old) old.remove();
    const el = document.createElement('div');
    el.id = '__hermes_cursor';
    el.style.cssText = 'position:fixed;left:0;top:0;width:0;height:0;z-index:2147483647;pointer-events:none;';
    el.innerHTML =
      '<div style="position:absolute;left:-14px;top:-14px;width:28px;height:28px;border-radius:50%;background:radial-gradient(circle,rgba(255,140,0,.28),rgba(255,140,0,0) 70%);"></div>' +
      '<svg width="30" height="30" viewBox="0 0 24 24" style="position:absolute;transform:translate(-1px,-1px);filter:drop-shadow(0 3px 4px rgba(0,0,0,.45))">' +
      '<path d="M4 2 L20 12 L12.5 13.6 L16 21 L13 22.2 L9.6 14.8 L4 19 Z" fill="#ffffff" stroke="#111" stroke-width="1.3" stroke-linejoin="round"/></svg>' +
      '<div style="position:absolute;left:22px;top:22px;font:600 11px/1.2 system-ui,-apple-system,sans-serif;color:#111;background:#ffe9a8;border:1px solid #d9b84a;border-radius:999px;padding:2px 7px;white-space:nowrap;box-shadow:0 2px 6px rgba(0,0,0,.18);display:' +
      (label ? 'block' : 'none') + '">' + (label || '') + '</div>';
    document.documentElement.appendChild(el);
    el.style.transform = `translate(${px}px, ${py}px)`;
    window.__hc = { el, x: px, y: py, v };
  }, { label: CURSOR_LABEL, v: 'hc3|' + CURSOR_LABEL }).catch(() => {});
}

async function cursorMove(page, x, y, ms = 320) {
  if (!CURSOR_ON) return;
  await cursorInject(page);
  await page.evaluate(async ({ x, y, ms }) => {
    const c = window.__hc; if (!c) return;
    const sx = c.x, sy = c.y, t0 = performance.now();
    const ease = t => (t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t);
    await new Promise(res => {
      const step = (t) => {
        const p = Math.min(1, (t - t0) / ms), e = ease(p);
        c.x = sx + (x - sx) * e; c.y = sy + (y - sy) * e;
        c.el.style.transform = `translate(${c.x}px, ${c.y}px)`;
        p < 1 ? requestAnimationFrame(step) : res();
      };
      requestAnimationFrame(step);
    });
  }, { x, y, ms }).catch(() => {});
}

async function cursorRipple(page, x, y, ms = 380) {
  if (!CURSOR_ON) return;
  await page.evaluate(async ({ x, y, ms }) => {
    const c = window.__hc; if (!c) return;
    const r = document.createElement('div');
    r.style.cssText = `position:absolute;left:${x - 12}px;top:${y - 12}px;width:24px;height:24px;border-radius:50%;` +
      `border:2px solid #ff8c00;background:rgba(255,140,0,.18);transition:transform ${ms}ms ease-out,opacity ${ms}ms ease-out;`;
    c.el.appendChild(r);
    requestAnimationFrame(() => { r.style.transform = 'scale(2.4)'; r.style.opacity = '0'; });
    await new Promise(res => setTimeout(res, ms));
    r.remove();
  }, { x, y, ms }).catch(() => {});
}

/** ชี้ไปกลาง element ก่อนคลิกจริง */
async function pointAt(page, loc) {
  if (!CURSOR_ON) return;
  const box = await loc.boundingBox().catch(() => null);
  if (!box) return;
  const x = Math.round(box.x + box.width / 2), y = Math.round(box.y + box.height / 2);
  await cursorMove(page, x, y);
  await cursorRipple(page, x, y);
  await page.waitForTimeout(120);
}

/** ---------------------------------------------------------------- */

try {
  switch (cmd) {
    case 'status':
      out(JSON.stringify({ pages: pages.length, urls: pages.map(p => p.url()), title: page ? await page.title() : null }));
      break;

    case 'newtab':
      await need();
      page = await ctx.newPage();
      if (a1) { await page.goto(a1, { waitUntil: 'domcontentloaded', timeout: 60000 }); await page.waitForTimeout(800); }
      out('new tab:', page.url(), '| tabs:', ctx.pages().length);
      break;

    case 'goto':
      await need();
      await page.goto(a1, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await page.waitForTimeout(1200);
      out('title:', await page.title(), '\nurl:', page.url());
      break;

    case 'shot':
    case 'fullshot':
      await need();
      await page.screenshot({ path: a1 || 'shot.png', fullPage: cmd === 'fullshot' });
      out('saved:', a1 || 'shot.png');
      break;

    case 'text':
      await need();
      out((await page.innerText('body')).slice(0, 4000));
      break;

    case 'click': {
      await need();
      const loc = await byText(page, a1);
      if (!loc) { out('NOT_FOUND:', a1); break; }
      await loc.scrollIntoViewIfNeeded().catch(() => {});
      await pointAt(page, loc);                        // ให้เห็นเมาส์ชี้ก่อนคลิก
      try {
        await loc.click({ timeout: 10000 });           // เมาส์จริง
      } catch (e) {
        out('CLICK_BLOCKED:', (String(e).match(/outside of the viewport|intercepts pointer events|Timeout/i) || ['timeout'])[0]);
        out('HINT: เลื่อนหน้าจอ/ปิด overlay ก่อน แล้วคลิกใหม่ (ห้ามใช้ clickjs ในห้องสอบ)');
        break;
      }
      await page.waitForTimeout(1000);
      out('clicked:', a1, '\nurl:', page.url(), '\ntitle:', await page.title());
      break;
    }

    case 'clickjs': {
      await need();
      const hit = await page.evaluate((txt) => {
        const els = [...document.querySelectorAll('button, a, [role=button], label')];
        const norm = s => (s || '').replace(/\s+/g, ' ').trim();
        const el = els.find(e => norm(e.innerText) === txt) || els.find(e => norm(e.innerText).includes(txt));
        if (!el) return false;
        el.scrollIntoView({ block: 'center' });
        el.click();
        return true;
      }, a1);
      out(hit ? 'clicked(js): ' + a1 : 'NOT_FOUND: ' + a1);
      await page.waitForTimeout(800);
      break;
    }

    case 'clickcss': {
      await need();
      const loc = page.locator(a1).first();
      await loc.scrollIntoViewIfNeeded().catch(() => {});
      await pointAt(page, loc);
      await loc.click({ timeout: 15000 });
      await page.waitForTimeout(800);
      out('clicked selector:', a1);
      break;
    }

    case 'point': {
      await need();
      const loc = await byText(page, a1);
      if (!loc) { out('NOT_FOUND:', a1); break; }
      await loc.scrollIntoViewIfNeeded().catch(() => {});
      await pointAt(page, loc);
      out('pointing at:', a1);
      break;
    }

    case 'closetab':
      await need();
      await page.close();
      out('closed | tabs left:', ctx.pages().length);
      break;

    case 'cursor': {
      await need();
      if (a1 === 'off' || a1 === 'on') {
        out('cursor overlay ตั้งค่าด้วย env PW_CURSOR=0|1 (ตอนนี้:', CURSOR_ON ? 'on' : 'off', ')');
        break;
      }
      const vp = page.viewportSize() || { width: 1280, height: 800 };
      const x = Math.round(vp.width / 2), y = Math.round(vp.height / 2);
      await cursorMove(page, x, y, 420);
      await cursorRipple(page, x, y, 500);
      out('cursor at', x, y, '| overlay:', CURSOR_ON ? 'on' : 'off');
      break;
    }

    case 'fill': {
      await need();
      const f = page.getByLabel(a1).or(page.getByPlaceholder(a1)).first();
      await pointAt(page, f);
      await f.fill(a2 ?? '');
      out('filled:', a1);
      break;
    }

    case 'press':
      await need();
      await page.keyboard.press(a1);
      await page.waitForTimeout(600);
      out('pressed:', a1);
      break;

    case 'wait':
      await need();
      await page.waitForTimeout(Number(a1 || 1000));
      out('waited ms:', a1 || 1000);
      break;

    case 'eval':
      await need();
      out(JSON.stringify(await page.evaluate(a1)));
      break;

    case 'links':
      await need();
      out(JSON.stringify(await page.$$eval('a', els => els.map(e => ({ t: (e.innerText || '').trim().slice(0, 60), h: e.href })).filter(x => x.t).slice(0, 80))));
      break;

    case 'buttons':
      await need();
      out(JSON.stringify(await page.$$eval('button, [role=button], input[type=submit]', els => els.map(e => {
        const r = e.getBoundingClientRect();
        return { t: (e.innerText || e.value || '').trim().slice(0, 50), x: Math.round(r.x + r.width / 2), y: Math.round(r.y + r.height / 2), vis: r.width > 0 && r.height > 0 };
      }).filter(x => x.t && x.vis).slice(0, 60))));
      break;

    case 'download': {
      await need();
      const loc = await byText(page, a1);
      if (!loc) { out('NOT_FOUND:', a1); break; }
      try {
        const [dl] = await Promise.all([page.waitForEvent('download', { timeout: 30000 }), loc.click({ timeout: 15000 })]);
        await dl.saveAs(a2);
        out('downloaded:', dl.suggestedFilename(), '→', a2);
      } catch (e) {
        out('DOWNLOAD_FAILED:', String(e).slice(0, 160));
        out('HINT: ปุ่มมักเป็น <a target=_blank> → ใช้ fetchsave กับ URL ของมัน');
      }
      break;
    }

    case 'fetchsave': {
      await need();
      const b64 = await page.evaluate(async (u) => {
        const r = await fetch(u, { credentials: 'include' });
        if (!r.ok) return 'ERR:' + r.status;
        const bytes = new Uint8Array(await r.arrayBuffer());
        let s = '';
        for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
        return btoa(s);
      }, a1);
      if (String(b64).startsWith('ERR:')) { out('FETCH_FAILED', b64); break; }
      fs.writeFileSync(a2, Buffer.from(b64, 'base64'));
      out('saved:', a2, fs.statSync(a2).size, 'bytes');
      break;
    }

    default:
      out('usage: status|goto|shot|fullshot|text|click|clickjs|clickcss|fill|press|wait|eval|links|buttons|download|fetchsave');
  }
} finally {
  await browser.close(); // ตัดการเชื่อมต่อเท่านั้น — Chrome ยังเปิดอยู่
}
