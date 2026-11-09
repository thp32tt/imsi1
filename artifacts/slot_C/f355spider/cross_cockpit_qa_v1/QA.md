# F355 Spider — SLOT C cross-cockpit native QA

Status: QA_WAITING_INPUT, NOT a full-vehicle PASS. This is a one-time source audit, not a new mesh edit.

Original PMT / initial import / accepted integrated .blend SHA256: d9af341653ef44371e8df2efc4024af92d7ca03665acef04a4c3c65200bb7b11 / 4fa9bdc314c5e30ab890adcff160377436540646588a36f1c4c1649c5df7186e / 354b2d8b67839cdabdaf838d596771750f6fb8d9919fd023a4dae2c24df52518.

Accepted chain: source import -> console -> seat -> cluster -> dashboard -> steering, all five receipt SHA links match.

Independent Blender reopening of both native scenes: PASS, 96 original mesh identities; five allowed native objects changed and 91 fully unchanged, including front glass, A pillars and borders. Topology, UV, transforms and counts are invariant.

Source-space two-render image is diagnostic only. Real OutRun camera eye and photo-registered matching are NOT verified.

Photos: 2/8 views verified, six required views missing: 01_driver_eye, 03_gauges_closeup, 04_steering_closeup, 06_seats, 07_door_trim, 08_windshield_frame. Driver controls/inner door remain BLOCKED. No further same-input QA or P0 smoothing retry. No new .blend or mesh modification in this audit.