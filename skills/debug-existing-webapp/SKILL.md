---
name: debug-existing-webapp
description: Diagnose and safely fix bugs in existing web applications while preserving unrelated behavior and user changes. Use for broken UI state, incorrect totals, failed API calls, stale deployment copies, visual misalignment, encoding problems, Google Apps Script or spreadsheet integration faults, and regressions in HTML, CSS, JavaScript, React, or static hosted sites.
---

# Debug Existing Web App

Find evidence before changing code. Fix the cause with the smallest coherent patch.

## Reconstruct the system

1. Identify the source of truth, entry page, shared assets, backend, data store, and deployment copy.
2. Read project notes and warnings, especially cohort, year, room, and production boundaries.
3. Check the worktree or file timestamps so user changes are not overwritten.
4. Reproduce the reported behavior when safe; otherwise inspect the exact state transition involved.

## Classify the failure

- **Presentation:** layout, responsive sizing, stacking, crop, font, contrast, or asset path.
- **Client state:** wrong derived value, stale state, race, duplicate handler, or boundary error.
- **Transport:** wrong URL, parameters, method, CORS, timeout, or malformed response.
- **Backend:** validation, concurrency, idempotency, authorization, or incorrect action routing.
- **Data:** wrong sheet, column, room, identifier, type, formula, or duplicate row.
- **Distribution:** source fixed but copied site, archive, cache, or deployed version is stale.

Do not mix categories until evidence connects them.

## Trace one failing path end to end

Follow:

`user action → handler → request → backend action → data read/write → response → rendered state`

At each boundary, compare expected and actual names, types, totals, IDs, and error behavior. For Apps Script integrations, explicitly verify the deployed URL, action name, room value, sheet name, header mapping, numeric conversion, and returned JSON shape.

## Fix safely

- Change the fewest lines that correct the invariant.
- Keep configuration centralized.
- Guard repeated clicks and concurrent writes.
- Reject insufficient balance and invalid progression on the server, not only in the UI.
- Preserve rollback assets and unrelated features.
- Never silently migrate or delete user data while fixing display logic.
- If a redesign is requested, separate it from the bug fix and state the changed behavior.

## Validate the repair

1. Run syntax, type, build, or parser checks appropriate to the project.
2. Test the failing case plus the nearest boundary cases.
3. Test a normal case that should remain unchanged.
4. Check console or server errors when available.
5. Confirm every source and deployment copy is synchronized.
6. Update the project report with the cause and durable fix, not a diary of commands.

For visual defects, compare against the actual asset dimensions and rendered coordinate system. Do not estimate from a cropped thumbnail when exact alignment matters.

Report the cause, the fix, validation, and any remaining uncertainty. Do not claim a browser or production test that was not actually performed.
