---
name: build-learning-webapp
description: Design and implement focused classroom learning web apps, gamified activities, progress journeys, point or stamp systems, and student-facing dashboards. Use when creating or substantially redesigning an educational HTML, CSS, JavaScript, React, or Apps Script application, especially when the activity must stay simple, mobile-friendly, visually coherent, and connected to an existing classroom data source.
---

# Build Learning Web App

Build the learning loop first; treat screens and decoration as support.

## Establish the contract

1. State the learning outcome in one sentence.
2. Identify the single repeated student action.
3. Define the reward, cost, progress unit, completion condition, and teacher control.
4. Separate historical simulations, school years, rooms, and production cohorts before editing files or data.
5. Record content caveats when the activity presents literature, belief, history, or simulation rather than current scientific fact.

If the user asks to simplify, remove secondary economies, shops, inventories, and extra screens before polishing.

## Inspect before building

- Read the current plan, notes, entry page, shared styles, data adapter, deployment folder, and warnings.
- Search for every old course name, room, semester, URL, sheet name, and feature label before replacing it.
- Preserve unrelated user changes and previous assets for rollback.
- Reuse a working architecture unless the requested behavior truly requires a structural change.

## Design the student experience

- Prefer one clear screen and one primary action.
- Make current progress, available balance, next action, and completion state visible without explanation.
- Use language students understand; hide implementation vocabulary.
- Design mobile-first with large touch targets, readable Thai text, keyboard focus, loading, empty, error, and completed states.
- Tie visual milestones to meaningful learning stages, not arbitrary decoration.
- Keep the visual theme consistent across the entry screen, activity, feedback, and banner.
- Lock visual identity with a project `DESIGN.md`: query `ui-ux-pro-max` (`scripts/search.py`) for cohesive palettes, typography pairings (e.g. Prompt/Kanit + Outfit), and accessible contrast (4.5:1).
- Apply `emil-skills` micro-interactions: tactile button press (`:active { transform: scale(0.97); }`), custom ease-out (`cubic-bezier(0.23, 1, 0.32, 1)`), animations < 250ms, and celebration spring physics on rewards.


## Design the data flow

Define one authoritative state response containing:

- student identity and cohort;
- earned, spent, and available balance;
- completed units and next unit;
- milestone or stage state;
- completion state.

Make mutations idempotent when possible. Re-read authoritative state after a successful mutation instead of trusting optimistic client arithmetic. Validate room, student, balance, limits, and duplicate submissions on the server.

## Implement in a focused pass

1. Patch the smallest coherent set of files.
2. Keep configuration values such as API URL, room, totals, and stage thresholds together.
3. Derive UI from state instead of duplicating progress logic across handlers.
4. Disable the primary action while saving.
5. Show a useful success or error message, then restore a safe state.
6. Update deployment copies and durable project notes after the source is correct.

## Validate

- Parse or build the code.
- Verify initial, intermediate, insufficient-balance, duplicate-action, final, and network-error states.
- Check totals and thresholds at boundaries.
- Confirm every distribution copy contains the same source and required assets.
- Perform visual browser testing only when requested or when the environment explicitly supports it.

Deliver the working result first, then summarize the learning loop, important assumptions, validation, and files the user must publish.
