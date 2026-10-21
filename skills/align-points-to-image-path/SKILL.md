---
name: align-points-to-image-path
description: Place, audit, and refine interactive UI points, milestones, labels, or sprites along a route embedded in a background image. Use when dots drift off a winding path, sparse anchor interpolation cuts corners, responsive scaling breaks coordinates, or an agent must convert image-space locations into precise CSS percentage positions for HTML, CSS, JavaScript, canvas, maps, games, and learning journeys.
---

# Align Points to an Image Path

Treat the image as the coordinate source of truth. Use normalized percentages only after preserving the image's rendered geometry.

## Preserve the coordinate system

1. Read the image's exact pixel dimensions.
2. Render the route container at the same aspect ratio.
3. Use an uncropped image mapping such as `background-size: 100% 100%` or an absolutely positioned `<img>` filling the same box.
4. Do not use `cover` for a coordinate overlay unless crop offsets are calculated.
5. Position each point with `left: x%`, `top: y%`, and `transform: translate(-50%, -50%)`.

Normalized conversion:

```text
xPercent = xPixel / imageWidth × 100
yPercent = yPixel / imageHeight × 100
```

## Choose the placement method

Use direct coordinates when:

- the route has tight S-curves, loops, or irregular turns;
- the number of visible points is fixed;
- exact visual placement matters more than generating arbitrary counts.

Use interpolation only when the control points are dense enough to represent every turn. Never connect sparse anchors with straight segments across a winding painted path; the generated points will cut corners.

## Build an evidence overlay

Create a numbered preview before editing the app:

```bash
python scripts/render_path_overlay.py background.png points.json overlay.png
```

`points.json` may be a list:

```json
[{"x": 49.5, "y": 8.78}, {"x": 52.16, "y": 12.04}]
```

or an object keyed by step:

```json
{"1": {"x": 49.5, "y": 8.78}, "2": {"x": 52.16, "y": 12.04}}
```

Inspect the original-size preview. Check the first point, last point, every tight turn, and any point that overlaps a milestone image.

## Refine efficiently

1. Establish the route direction and the semantic start and end.
2. Place points at turns first.
3. Fill long sections at visually even travel distances.
4. Generate the numbered overlay.
5. Move only inaccurate points; preserve the confirmed coordinates.
6. Repeat until every center lies within the painted route.
7. Patch the application with direct coordinates and remove obsolete interpolation code.

When the route itself contains a special origin or destination, align the relevant point to that semantic center rather than the geometric center of the surrounding stroke.

## Validate in the application

- Confirm the asset filename and aspect ratio.
- Confirm the coordinate container and background share the same bounds.
- Count the rendered points and verify their order.
- Test narrow and wide widths without changing the image mapping.
- Check that stage art offsets do not make the points appear misplaced.
- Update deployment copies after the source is correct.

Use the bundled overlay script for deterministic inspection. Do not ship the diagnostic overlay as a production asset.
