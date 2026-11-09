## V4 authoritative workpack dispatch and measurable output (2026-11-09)

**This V4 section overrides all conflicting V3 cyclic part selection, stale windshield instructions and repeated QA send guidance below.** Controller source: thp32tt/OutRun2006Tweaks@chat-controller-downloads. Artifact SSOT: thp32tt/imsi1@main.

1. **Fetch before sending.** Controller reads the current queue and each A/C workpack through GitHub. Validate active car identity, current_component, part status, consumed dispatches and source evidence. Local breadth_dispatch_count is telemetry only, NEVER an assignment source. GitHub failure means no send.
2. **One checkpoint, one send.** Persist last_workpack_fingerprint_sent only on actual successful message delivery. When the same component/status/dispatch/accepted-blend fingerprint reappears, suppress the dispatch across chat rollover/redeployment. Do not consume tokens just for a repeat BLOCKED/QA report.
3. **No P0 loops or glass edits.** Dashboard and steering are held after dozens of historical passes. Never schedule them without explicit new user defect and separate approval. Front windshield, A-pillars and glass-fitting/border geometry are always observation-only.
4. **Hard 24h geometry stop.** After started_at_utc +24h, only a bounded QA/integration action is eligible. Do not silently mark PASS, switch active cars, resume exploratory geometry or keep polling ChatGPT. If QA is blocked, waiting for input, complete or has used 2/2 sends, park the slot until the workpack materially changes.
5. **Daytona integrated checkpoint priority.** Existing accepted full cabin is R45 SHA 224131c7...; R46 original PMT017 seat SHA e84c723... and R47 PMT015 gauge SHA 7367034... are independent original-import .blend files and are not merged into the R45 cabin. Before declaring whole-car improvement, carry out a non-destructive integration into a NEW versioned .blend: compare each original object ID, verify source vertex fingerprints, preserve all unrelated meshes including windshield-adjacent geometry, independently reopen, and render from the same seated camera. Record input/output SHA and failed guards. If it cannot be validated, record one WAITING_QA_INPUT and park.
6. **F50 integrated lineage but incomplete QA.** v40→v43→v44 is a chained native source-edit baseline; it is not a full-car PASS. Complete authentic calibrated seated-driver view/photo checks, or record missing evidence and WAITING_QA_INPUT once. No P0 cosmetic retries.
7. **Outcome-oriented acceptance.** Reports distinguish source_mesh_changed, integrated_into_accepted_scene, blender_independent_reopen, matched_driver_view and whole_car_qa_pass. No credit for doc-only commits, minor vertex/pixel-count changes or repeated same-source QA. Part COVERED_PARTIAL_QA is not a vehicle PASS.
8. **Safety and scope.** Original PMT packages, native game resource bundles and private authentic full photos remain off public GitHub; permitted files are only editable .blend, modeling scripts, QA receipts and non-proprietary comparison renders. No PMT/OVC/OVC3 conversion, runtime patch, new PBR, exterior modeling or windshield-adjacent edit.

**Deployment confirmation:** live controller build must change from 2026-11-09-ferrari-public-temp-v10, and per-slot state should report breadth_strategy_version=4 and dispatch_source=imsi1_workpack_main after its next approved send. If GitHub workpack has not changed, the gate should explain why no message was sent.

---

> Temporary workspace migration (2026-11-09): active SSOT/work artifacts now live in public repo `thp32tt/imsi1@main`. Modeling artifacts may be stored plaintext; raw original PMT packages and private reference photos remain off-repo. Encryption/secret gating is retired for this temporary workspace.

## Mandatory executable preflight / postflight gate (2026-11-09)
The actual source-mesh authoring workflow is unchanged. Before ANY new Blender geometry edit, fetch the latest imsi1@main queue/workpack and run:
- A: python3 tools/car_modeling/workspace_guard.py preflight --slot A
- C: python3 tools/car_modeling/workspace_guard.py preflight --slot C
If BLOCKED, do not edit, retry, or silently switch parts; record the blocker and advance the persisted dispatch index/workpack by the existing controller rule. Never reset the two-dispatch counter at chat rollover.
After the separate-process Blender reopen, require:
python3 tools/car_modeling/workspace_guard.py verify-receipt --slot <A|C> --receipt <receipt.json> --output-blend <saved.blend>
The receipt must be generated from real before/after native object/vertex fingerprints, not text-only assertions. A metadata-only GitHub Actions receipt check does NOT verify .blend bytes or prove full photo QA. Do not promote a checkpoint to COVERED_PARTIAL_QA if the postflight fails. Never mark full-car QA PASS from this guard. The protected windshield/A-pillar policy and prohibition on new synthetic models are unchanged.

## USER PROTECTED REGION — front windshield / glass boundary (2026-11-09)
- **DO NOT EDIT** front windshield glass, windshield frame, windshield-adjacent A-pillars, seals/borders, or any mesh whose geometry can affect the front glass fit/rendering.
- These regions are observation/QA-only. Never move vertices, add/delete faces, alter topology/transforms, or choose them as an automation target.
- Historical F50 v41 windshield-header/A-pillar edit is rejected from the accepted chain; F50 resumes from pre-windshield v40 SHA `03b96b1eb2293c151c60133919380055fa8393372b0acbf18045edf25faa949a`.
- Daytona never accepted a windshield edit and remains on R45. After inner-door coverage, proceed directly to **visible_seat**.

# Ferrari cockpit rework V3 — breadth-first, source-backed, timeboxed
Date: 2026-11-09 KST. This overrides the old P0-forever/day-long steering-wheel approach.
SSOT queue: docs/automation/FERRARI16_GEOMETRY_QUEUE.json; per-car workpacks: docs/automation/FERRARI_COCKPIT_WORKPACK_A_DAYTONA365.json and docs/automation/FERRARI_COCKPIT_WORKPACK_C_F50.json.
A/C have independent 24-hour car ownership and alternating :00/:30, :15/:45 sends. Model2, DX11, DX9Ex, DXVK, web porting and Dino are excluded.

## Diagnosis from actual GitHub history
As of 2026-11-09 07:30 KST, A is Daytona R41 and C is F50 v36. Both carried out repeated authentic PMT-derived dashboard/steering geometry edits, real private Blender saves/reopens and renders; other original driver-visible cockpit components remain underrepresented. The older acceptance process repeatedly called out incomplete seven authentic photo views, uncalibrated real-game driver-eye, native nonmanifold and blocked confidential .blend upload to GitHub-hosted VM. Those high-cost final QA prerequisites must NOT cause endless polishing of an already-edited steering wheel or substituting CI smoke work for modeling. Past work, file SHA, source provenance and gaps are retained in Git history.

## Hard priority: complete the *visible cockpit*, not one object
- P0 dashboard and steering wheel remain important, but **P0 means must pass by final QA**, NOT the exclusive subject of all interim geometry commits.
- A and C have already spent many iterations on dashboard/wheel. Starting next scheduled command, **put both P0 regions on polish hold** and start the missing source-native center console / shifter path. Do not reset the vehicle clock or overwrite any prior private .blend; start from the latest confirmed saved source-derived scene.
- Coverage work order for each car: (1) center console, gear selector and surround; (2) driver's controls, stalks and visible pedals; (3) inner door / door top and handle; (4) visible seat / immediate trim; (5) instrument cluster, bezels and vent openings; (6) dashboard whole-form fit; (7) steering only for *identified defects*; (8) cross-cockpit photo review / QA. Windshield/front-glass regions are permanently skipped.
- Prioritize user-visible geometry errors, silhouette, join/seam discontinuities and proportions over micrometer moves, mesh resolution increases, arbitrary subdivisions, shading-only tweaks and identical-camera pixel-change statistics. No invented fake wheel holes, no bolt tubes, no false lip/bridge.
- No new vehicle, unrelated GLB replacement, PMT/OVC/OVC3 conversion, game integration, texture/PBR/normal map, exterior/body/wheel.

## Timeboxes / WIP limits
- Each original-source cockpit component gets at most **two 30-minute dispatch turns** (one ~60-minute scheduling window) for its FIRST material improvement pass, or **two source-changing Blender checkpoints**, whichever arrives first. This is a dispatch-budget cap, NOT a guarantee of CPU run time.
- One dispatch means one material geometry edit to a previously unfinished component, save versioned source-derived private .blend, fresh-reopen if possible, a basic same-camera before/after screenshot, provenance SHA and a short workpack update. Do not spend a dispatch merely rehashing old PMT, running unchanged CI, rewriting history or retrying the same edit.
- After one source-backed geometric improvement passes local save/reopen and obvious visual sanity, mark that component \`COVERED_PARTIAL_QA\` and **move to the next**, even if full 7-view/hosted-run/original-game eye is still outstanding. \`COVERED_PARTIAL_QA\` is NOT \`COMPLETE\` or QA PASS.
- If the assigned component is absent, invisible from seat, unavailable in the original model, or two dispatches fail to deliver a source modification, record \`BLOCKED\` or \`OUT_OF_VIEW\` with concise evidence and **move to the next component within the SAME car**. Don't fabricate a replacement mesh.
- While any relevant region is \`NOT_STARTED\`, \`BLOCKED\` or \`OUT_OF_VIEW_UNVERIFIED\`, do **not** return to steering-wheel smoothing and repeat iterations. A specific *new user-reported* wheel defect or a safety/geometry blocker may preempt once, with a max two-turn repair and a written defect ID; then immediately resume the interrupted component.
- After breadth pass, use remaining 24h window to fix the **largest perceptually relevant** discrepancy per genuine photo comparison, not repeatedly touch all vertices. Each fix needs a distinct named defect and before/after screenshot; a failed attempt consumes its timebox. No automatic material changes after 24h absent targeted user approval or fail-closed gate diagnosis.
- Do not use seven-photo/hosted-private-scene QA as a reason to polish wheel again; log these as external \`QA_BLOCKERS\` and focus on another component during the 24h work window. No car advancement without existing independent final gate requirements. No idle loop on permanently unreachable gates.

## Dispatch progression and proof
- Controller must derive its assigned region from an independent, persisted A/C dispatch index, starting at center console for this migration; every **two actually sent messages** advances the region. It must not reset across new ChatGPT chats, 60-minute rollover or container restart. If a send fails, the index must not be consumed.
- Per-car JSON workpack records each part's state and source-backed evidence; initial dashboard and wheel are \`P0_POLISH_HOLD\` due to prior work, **not falsely declared PASS**. Per-car workpack files avoid A/C editing the same giant queue at each checkpoint.
- **Before every edit**: read latest queue active_by_slot, workpack, original asset path and source native PMT SHA, source-derived initial .blend hash and latest private .blend hash. If latest private file or original-game provenance cannot be verified -> \`BLOCKED_INPUT\`; never make a new car.
- **After every edit**: report region, original game mesh object names changed, input/output .blend SHA, actual Blender save/reopen result, matched image, unresolved issue, exact next region. Keep the checkpoint summary under 600 characters; preserve prior history in separate docs not append thousands of words to \`queue.cars[].notes\`.
- Final acceptance: P0 dashboard and wheel plus cockpit region coverage, genuine photo comparison, calibrated visibility, provenance, independent Blender audit and remaining visible defects. Mark interim areas \`COVERED_PARTIAL_QA\` only; final QA gate remains required. Do not fake QA PASS or change vehicle before all quality gates.
- For a whole-car blocking source file, flag \`BLOCKED_INPUT\` and do not create a surrogate. For a missing optional photo/view of ONE region, annotate its evidence gap and proceed to next geometry region.

## Order and first expected concrete outcomes
1. **A Daytona**: stop R41→R42 steering wheel/rim/bezel microiteration. Preserve true original Daytona PMT/import provenance and latest real private R41 editable .blend. Next genuine geometry edit should be the SOURCE-DERIVED center console / shifter support visible from the seat. Then driver's controls, door trim, windshield frame, visible seats; revisit P0 only after coverage.
2. **C F50**: stop v36→v37 spoke/rim/hub microiteration. Preserve original F50 PMT/import and latest real private v36 .blend. Next genuine geometry edit should be center console / switches / shifter visible to driver, then controls, inner doors, windscreen and visible seat contours; revisit P0 only after coverage.
3. If either car lacks an original-source component, identify original PMT submesh and prove absence; record blocker and continue with next visible region. No new full car, random GLB, or OVC3.

## How to verify governance
Run \`python3 tools/car_modeling/coverage_strategy.py --queue docs/automation/FERRARI16_GEOMETRY_QUEUE.json --slot A --state docs/automation/FERRARI_COCKPIT_WORKPACK_A_DAYTONA365.json\` (and C equivalent). Status is advisory for prioritizing actual edits; source evidence gates remain fail closed. Automated tests verify schedule alternation, two sends per component, migration at center console, no looping back to wheel while coverage gaps exist and no duplicate advancement merely on chat rollover.
