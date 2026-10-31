---
name: visual-dev-loop
description: Orchestrates an autonomous Visual Development & UI Verification Loop in Google Antigravity. Enables the agent to run local dev servers, inspect live application viewports, capture artifacts, and self-heal UI regressions.
---

# Visual Development & UI Verification Loop (สร้างไป ตรวจไป)

This skill guides the agent through iterative frontend engineering with immediate visual feedback. It mirrors modern AI dev experiences (e.g., Cursor, Windsurf, Devin) inside Google Antigravity.

---

## 1. Visual Loop Architecture

```text
+-------------------+      +--------------------+      +--------------------+
|  Agent Code Edit  | ---> |  Local Dev Server  | ---> |  Visual Inspection |
|  (HTML/CSS/JS)    |      |  (HMR Hot-Reload)  |      |  (Snapshot/Subagent|
+-------------------+      +--------------------+      +--------------------+
          ^                                                      |
          |                  Audit Passes / Fails                |
          +------------------------------------------------------+
```

---

## 2. Core Execution Procedures

### Step 1: Start Dev Server Daemon
Launch the development server in background mode using `run_command` with `IsDaemon: true`:
```powershell
npm run dev
# Or: npx vite --port 5173
```
Confirm the local port (e.g., `http://localhost:5173`) from terminal output.

### Step 2: Visual Inspection (Choose Best Modality)

#### Modality A: Native `browser_subagent` (Recommended for Dynamic Workflows)
Call the native Antigravity `browser_subagent` to actuate and verify interactive state:
- **Task**: "Navigate to http://localhost:5173. Verify navigation links, open the modal, and record visual state."
- **Output**: Generates full WebP video session and screenshots saved automatically in the Artifacts directory.

#### Modality B: Quick Multi-Viewport Snapshot (Fast Layout Audit)
Run the project capture utility to snapshot desktop, tablet, and mobile breakpoints:
```powershell
node tools/preview-capture.mjs http://localhost:5173 ./previews
```

#### Modality C: MCP Server Direct Tooling (`@playwright/mcp`)
When configured in `mcp_config.json`, invoke:
- `browser_navigate`: Target `http://localhost:5173`
- `browser_take_screenshot`: Capture immediate viewport buffer

---

## 3. Visual Self-Healing Checklist

Before concluding any frontend edit, audit the captured screen against these criteria:
1. **Typography & Hierarchy**: Fonts must render correctly (TH Sarabun New for Thai official docs; Inter / Outfit for modern web). No raw browser serif defaults (Times New Roman).
2. **Spacing & Alignment**: Respect 8px design grid. Ensure margins and paddings are balanced.
3. **Contrast & Color Palette**: Harmonious dark/light theme tokens; no raw saturated `#ff0000` or `#0000ff`.
4. **Responsive Overflow**: Check mobile viewport (390x844). No horizontal scroll bars on root containers.
5. **Interactive Feedback**: Hover and active transitions on buttons (0.15s - 0.2s cubic-bezier).
6. **Anti-Slop & Micro-Interaction Audit (`impeccable` + `emil-skills`)**: Ensure no generic purple-gradient card boilerplate, no unstyled default controls, no `scale(0)` entrances (use `scale(0.95)` + opacity), no sluggish `ease-in`, and verify tactile `:active` feedback on all clickable elements.
