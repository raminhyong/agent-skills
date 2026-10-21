---
name: thai-subapp-blueprint
description: Master Layout and Micro-Frontend Architecture Blueprint for all Thai PW Hub sub-applications. Use when designing, building, restructuring, or checking any sub-application in the Thai PW Hub ecosystem.
---

# Thai PW Hub Sub-App Master Architecture Blueprint

พิมพ์เขียวมาตรฐานสถาปัตยกรรมแถบหัว, แถบเมนูนำทาง, และการทำงานของ Micro-Frontend Workspace Runner สำหรับทุกแอปย่อยใน **Thai PW Hub (โรงเรียนพูลเจริญวิทยาคม)**

---

## 1. กฎเหล็กโครงสร้างแถบหัวแอปย่อย (Master Sub-App Header)

### 1.1 ความกว้างและการจัดวาง
- **ความกว้าง**: กว้างเต็ม 100% (Edge-to-edge) ไร้กรอบลอยหรือ Boxed เล็ก
- **สไตล์หลัก**:
  - พื้นหลังสีเขียวมรกตราชการ (`background: #064e3b` หรือเกรเดียนต์ `linear-gradient(135deg, #064e3b 0%, #065f46 100%)`)
  - เส้นขอบล่างสีทองคำหรูหรา (`border-bottom: 2px solid #d4a72c`)
  - ความสูงแถบประมาณ 64px – 68px พร้อม `backdrop-filter: blur(12px)`

### 1.2 องค์ประกอบฝั่งซ้าย (Identity & Two-Line Title)
- **โลโก้แอปย่อย**: ตราประจำระบบในกรอบสี่เหลี่ยมมน (`border-radius: 12px`), ขอบสีทอง (`#d4a72c`), ขนาด 42x42px หรือ 44x44px, เมื่อคลิกสามารถกลับหน้าหลัก Hub ได้
- **ชื่อระบบ 2 บรรทัด (Two-Line Hierarchy)**:
  - **บรรทัดที่ 1 (ภาษาไทย)**: ฟอนต์ขนาด 1.15rem – 1.25rem ตัวหนา สีนวลทอง/ขาว (เช่น *"ระบบจัดครูสอนแทน"*, *"บันทึกข้อความอัจฉริยะ"*)
  - **บรรทัดที่ 2 (ภาษาอังกฤษ)**: เคาะลงมาบรรทัดที่ 2 ฟอนต์ขนาด 0.78rem – 0.82rem สีนวล/ทองจางๆ อักษรนำตัวใหญ่ (เช่น *"Smart Substitute Teacher System"*, *"Thai Smart Memo"*)
  - ⛔ **กฎเหล็กเด็ดขาด**: **ห้ามมีชื่อกลุ่มสาระการเรียนรู้ และชื่อโรงเรียนพูลเจริญวิทยาคมบนแถบหัวของแอปย่อยเด็ดขาด** (เพราะแสดงอยู่บนแถบหลักของ Hub ด้านบนแล้ว เพื่อขจัดความซ้ำซ้อน 100%)

### 1.3 องค์ประกอบกึ่งกลาง (Status Badges)
- ป้ายสถานะทรงแคปซูล เช่น `● ภาคเรียนที่ 1/2569`, `ระบบพร้อมทำงาน`, หรือสถานะโมเดล AI (`TypeSafe (Jev)`, `Gemini 3.8 Flash`)

### 1.4 องค์ประกอบฝั่งขวา (3 Master Control Buttons)
มี 3 ปุ่มมาตรฐานเสมอ เรียงลำดับจากซ้ายไปขวา:
1. **ปุ่มรีเฟรช (🔄)**: รีเซ็ตข้อมูลหรือรีโหลดแอปย่อย
2. **ปุ่มเปิดแยกแท็บใหม่ (↗️)**: เปิด URL ของแอปย่อยในแท็บเบราว์เซอร์ใหม่ (`target="_blank"`)
3. **ปุ่มขยาย-ย่อ (⤢ / ⤡)**: สลับมุมมองตามสถาปัตยกรรม Workspace

---

## 2. ลำดับชั้นสถานะและการทำงานของปุ่ม "ขยาย / ย่อ" (State & Lifecycle Protocol)

แอปย่อยฝังตัวทำงานอยู่ใน **Thai PW Hub** ผ่าน iframe ภายใน Workspace Runner (`#runnerOverlay`)

### สภาวะที่ 1: โหมดปกติใน Workspace (Docked Mode)
- **การจัดวาง**: หน้าต่างแอปย่อยจะวางตัวอยู่ในกรอบ Workspace ของ Hub
- **หน้าจอรวม**: แถบหลัก Hub ด้านบน (Thai PW Hub, ค้นหา, TypeSafe AI) และ Sidebar เมนูหมวดหมู่ซ้าย ยังคงแสดงอยู่ครบถ้วน
- **ปุ่มบนขวาสุด**: ต้องแสดงเป็น **`[ ⤢ ขยาย ]`**
  - คลาส: `.app-ctrl-btn.app-ctrl-btn-expand`
  - สี: พื้นเขียวอ่อน `#ecfdf5`, ขอบเขียว `#10b981`, ข้อความ `#065f46`, ลูกศรชี้ออก 4 ทิศ
  - Tooltip: `"ขยายเต็มหน้าจอ"`

### สภาวะที่ 2: โหมดขยายเต็มหน้าจอ (Expanded Fullscreen Mode)
- **เมื่อกดปุ่ม "ขยาย"**:
  - แอปย่อยส่ง `postMessage({ type: 'requestFullscreen' }, '*')` ไปยัง Hub Runner
  - Runner สั่ง `overlay.requestFullscreen()` เพื่อกางเต็มจอ 100vw × 100vh ปิดแถบหัวและ Sidebar ชั่วคราว เพื่อเพิ่มพื้นที่การทำงานสูงสุด
- **ปุ่มบนขวาสุด**: จะสลับเป็น **`[ ⤡ ย่อ ]`**
  - คลาส: `.app-ctrl-btn.app-ctrl-btn-expand.is-fullscreen`
  - สี: สีนวลทองอำพัน `#fffbeb` ถึง `#fef3c7`, ขอบส้มทอง `#f59e0b`, ข้อความ `#92400e`, ลูกศรชี้เข้า 4 ทิศ
  - Tooltip: `"ย่อกลับมาหน้าปกติ"`

### เมื่อกดปุ่ม "ย่อ" (Restore Layout Action)
- **การทำงาน**: ส่ง `postMessage({ type: 'exitFullscreen' }, '*')`
- **การฟื้นฟู**: Hub Runner ออกจาก Fullscreen หดขนาดแอปย่อยกลับมาอยู่ในกรอบ Workspace ทันที
- **ความสมบูรณ์ของข้อมูล**: แถบหัว Hub และ Sidebar กลับมาแสดงตามเดิม โดยที่ **ข้อมูลที่กรอกในฟอร์มไม่สูญหาย ไม่มีการรีโหลดหรือเปลี่ยนหน้าเว็บ (In-memory State Preservation)**
- ⛔ **ข้อห้ามเด็ดขาด**: **ห้ามใช้ `window.location.href` หรือ reload หนีออกจากหน้าเด็ดขาด** การกดย่อคือการ Restore Window ขนาดปกติเท่านั้น
- **ปุ่มบนขวา**: ดีดกลับเป็น **`[ ⤢ ขยาย ]`** ตามวัฏจักร

---

## 3. แถบนำทางเมนูหลักของแอปย่อย (Horizontal Main Navigation Bar)

- **ตำแหน่ง**: วางพาดต่อจากแถบหัวแอปย่อยทันทีแบบแนวนอน (`.sub-main-tabs-bar`) เชื่อมต่อแบบ Sticky Header (`top: 64px - 68px`)
- **การจัดวาง**: เต็มความกว้าง 100% บรรจุแท็บฟังก์ชันทั้งหมดของแอปย่อย
- ⛔ **การตัดสิ่งซ้ำซ้อน**: **ยกเลิก / ลบกล่องเมนูเครื่องมือแนวตั้งเดิมที่เคยอยู่ฝั่งซ้ายของแอปย่อยออกทั้งหมด 100%** เพื่อไม่ให้ไปชนหรือซ้ำซ้อนกับ Sidebar ของ Hub

---

## 4. โค้ดแม่แบบมาตรฐาน (Reusable Reference Snippets)

### 4.1 CSS Styles สำหรับปุ่มควบคุม
```css
.app-ctrl-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 36px;
  padding: 0 12px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid rgba(255, 255, 255, 0.25);
  background: rgba(255, 255, 255, 0.95);
  color: #1e293b;
}

/* ปุ่มขยาย (ปกติใน Workspace) */
.app-ctrl-btn-expand {
  background: #ecfdf5;
  border-color: #10b981;
  color: #065f46;
}
.app-ctrl-btn-expand:hover {
  background: #d1fae5;
  border-color: #059669;
}

/* ปุ่มย่อ (เมื่ออยู่ใน Fullscreen) */
.app-ctrl-btn-expand.is-fullscreen {
  background: linear-gradient(180deg, #fffbeb 0%, #fef3c7 100%);
  border-color: #f59e0b;
  color: #92400e;
  box-shadow: 
    inset 0 1.5px 0 #ffffff,
    inset 0 -1.5px 0 rgba(217, 119, 6, 0.2),
    0 2.5px 0 rgba(180, 83, 9, 0.35),
    0 4px 10px rgba(245, 158, 11, 0.25);
}
.app-ctrl-btn-expand.is-fullscreen:hover {
  background: #ffffff;
  color: #b45309;
  border-color: #d97706;
}
```

### 4.2 React State & PostMessage Handler
```javascript
const [isFullscreen, setIsFullscreen] = useState(false);

useEffect(() => {
  const handleFsChange = () => {
    setIsFullscreen(!!document.fullscreenElement);
  };
  const handleMsg = (e) => {
    if (!e.data) return;
    if (e.data.type === 'fullscreenStateChanged' && typeof e.data.isFullscreen === 'boolean') {
      setIsFullscreen(e.data.isFullscreen);
    }
  };
  document.addEventListener('fullscreenchange', handleFsChange);
  document.addEventListener('webkitfullscreenchange', handleFsChange);
  window.addEventListener('message', handleMsg);
  return () => {
    document.removeEventListener('fullscreenchange', handleFsChange);
    document.removeEventListener('webkitfullscreenchange', handleFsChange);
    window.removeEventListener('message', handleMsg);
  };
}, []);

const toggleFullscreen = () => {
  if (window.parent && window.parent !== window) {
    try {
      if (isFullscreen) {
        window.parent.postMessage({ type: 'exitFullscreen' }, '*');
      } else {
        window.parent.postMessage({ type: 'requestFullscreen' }, '*');
      }
    } catch (_) {
      if (isFullscreen) {
        document.exitFullscreen?.().catch(() => {});
      } else {
        document.documentElement.requestFullscreen?.().catch(() => {});
      }
    }
  } else {
    // Standalone mode: จัดการ Native Fullscreen API เท่านั้น
    // ห้ามใส่ window.location.href หรือ reload หนีออกจากหน้าเด็ดขาด
    if (document.fullscreenElement) {
      document.exitFullscreen?.().catch(() => {});
    } else {
      document.documentElement.requestFullscreen?.().catch(() => {});
    }
  }
};
```

---

## 5. กระบวนการตรวจสอบคุณภาพก่อนส่งมอบ (Double QC Checklist)

ก่อนส่งมอบงานแอปย่อยทุกครั้ง ให้รัน Browser Subagent ถ่ายภาพหน้าจอจริง:
1. [ ] **ตรวจใน Hub**: เปิดแอปผ่าน Hub (`index.html`) ตรวจว่าแถบหลัก Hub และ Sidebar ยังอยู่ และแอปย่อยวางใน Workspace อย่างเรียบร้อย
2. [ ] **ตรวจชื่อและป้าย**: โลโก้ซ้ายสุด, บรรทัดที่ 1 ภาษาไทย, บรรทัดที่ 2 ภาษาอังกฤษ, **ไร้ชื่อกลุ่มสาระและโรงเรียน**
3. [ ] **ตรวจปุ่มเริ่มต้น**: ปุ่มบนขวาสุดต้องแสดงเป็น **`[ ⤢ ขยาย ]`** สีเขียว
4. [ ] **ตรวจเมนูแนวนอน**: เมนูหลักของแอปย่อยเป็นแนวนอนใต้แถบหัว และกล่องเมนูแนวตั้งเดิมถูกลบออก 100%
5. [ ] **ตรวจการย่อ/ขยาย**: เมื่อกดขยาย เข้าสู่โหมดเต็มจอพร้อมปุ่มสีทอง **`[ ⤡ ย่อ ]`** และเมื่อกดย่อ กลับสู่โหมด Workspace พร้อมปุ่ม **`[ ⤢ ขยาย ]`** โดยไม่มีการรีโหลดหน้าเว็บ
