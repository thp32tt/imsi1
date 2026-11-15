# Private complete F50 external-model test kit

Date: 2026-11-16 KST

The public experiment branch intentionally does not contain the third-party external F50 binary or original OutRun game assets.

A complete private reproduction bundle is stored on the N100 work host at:

`/home/chatgpt-runner/car_importer_transfer_20261115/OutRun2006_F50_External_OVC_R26_TEST_KIT_20261116_COMPLETE.zip`

- ZIP size: 139,698,578 bytes
- ZIP SHA256: `4edc4b15838da370a42369537d9c7db82aaa268a3772dda5cb455c1802e9894d`
- Archive entries: 129

The private bundle contains:
- source external GLB
- all F50 external-overlay Blender POC checkpoints V01-V04 + final
- original OutRun F50 PMT source copies (4 files)
- original-PMT-derived Blender reference used for the comparison
- staged GLB + staged Blender
- generated F50 OVC and manifests
- importer + sidecar source/validation tools
- QA manifests and actual Blender renders

Key source SHA256:
- external GLB: `6aa960b4d79f5e9400aaa804c2301f3c344461a88abc264d131b567575cae2dc`
- final overlay Blender: `07301b12ab23de5e982f0e78a0252c18912f7b3e61be840e7a846055252360a2`
- stock `obj_plcar_f50_pmt.sz`: `10daa1312b6cff0267b38b4c440c6007c68b470a225ca15f0c324876fd80aeab`
- native reference Blender: `1ff620c4ede9a265b66440105c16cd318f4e9e3761ec2754d13866f0b7d7507e`
- staged GLB: `fbe63a7982391a314f93929ceb414edb61ecc2677ef2dafda469c2f486293b37`
- staged Blender: `f3d169a0125bd296de0371780c4ec7e604785227648b8710392efbd8d9d437c6`
- generated OVC: `f6d971a579966dc03937369801096e067897933b4f03cc8c3ae25fece2b67284`

The original OutRun assets are kept as source/reference copies and are not overwritten by the sidecar workflow.

Do not publicly redistribute the private complete bundle until the external model's underlying redistribution provenance is verified.
