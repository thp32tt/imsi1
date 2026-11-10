# Actual Blender PMT cockpit render comparisons (2026-11-10)

These are **actual source-derived Blender Workbench captures** laid out as two-column BEFORE/AFTER panels. The only processing is resizing, labels and arrangement. **No AI-generated or fabricated image content was inserted.** They are NOT in-game screenshots, not photorealistic, and do not establish whole-car QA PASS.

## Ferrari 360 Spider
- Center-console BEFORE: `artifacts/slot_A/360spider/center_console_20261110/before_oblique.png`
- Center-console AFTER: `artifacts/slot_A/360spider/center_console_20261110/after_oblique.png`
- Isolated dashboard BEFORE: `artifacts/slot_A/360spider/dashboard_20261110/dashboard_isolated_seated_before.png`
- Isolated dashboard AFTER: `artifacts/slot_A/360spider/dashboard_20261110/dashboard_isolated_seated_after.png`
- Note: These are targeted PMT source-mesh views, **not a full-cockpit camera screenshot**.

## Ferrari F355 Spider
- Native cockpit context BEFORE: `artifacts/slot_C/f355spider/cross_cockpit_qa_v1/native_context_baseline.png`
- Native cockpit context AFTER: `artifacts/slot_C/f355spider/cross_cockpit_qa_v1/native_context_accepted.png`
- Steering-wheel BEFORE: `artifacts/slot_C/f355spider/steering_wheel_v1/wheel_before.png`
- Steering-wheel AFTER: `artifacts/slot_C/f355spider/steering_wheel_v1/wheel_after.png`
- Note: Oblique native context and steering close-up; not a complete calibrated driver-eye view.

Each pair keeps the matched camera framing supplied by its existing native Blender capture. These comparisons deliberately show the modest actual geometry change rather than inventing dramatic effects. PBR/texturing and full in-game validation are outside scope.

**This file documents an arrangement of existing real renders. No new whole-cockpit Blender scene was rendered for these boards.**
