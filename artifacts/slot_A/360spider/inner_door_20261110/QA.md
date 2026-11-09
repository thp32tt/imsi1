# 360 Spider / SLOT A / inner_door – BLOCKED

**Native PMT inspection only; no geometry edit, no checkpoint promotion, no dispatch consumed.**

- Original OutRun PMT SHA256: `a4b56d6e3ed126bcf2b2c88f149c4daeac124f96b6de2518e88436f618f076e6`
- Input/output accepted editable Blender SHA256 (unchanged): `5dabffb52ae4136b6b72f99c7975b629820f839afec2048e59035cb74d8ee612`
- Inspected existing original-native PMT geometry: `PMT_object00_group01_material006_a0` and `PMT_object00_group01_material010_a0`. The first contains disjoint outer side surfaces; the second contains mixed cabin-floor/seat supports. No separately attributable, safely editable interior door card/armrest/handle/speaker group was proven.
- Compared with private N100 Ferrari 360 Spider inner-door real photo showing black upper padded insert, armrest, silver lower speaker section. Original photo stays on N100.
- Protected front glass/frame/A-pillars/door-body and all 75 PMT-native source object geometry remains untouched. No new mesh, no exports, no textures.
- **BLOCKED**: No independently attributable native original interior-door trim/armrest/handle/speaker mesh. Candidate PMT_object00_group01_material006_a0 islands 2917-2934 and 2832-2870 render as exterior body-side surfaces, while material010 includes seat/floor/cockpit surfaces without a safely isolated inner-door part. Editing either would risk exterior or adjacent protected glass-fitting geometry; source-only target was rejected. No synthetic new door mesh allowed.
- Next target: `visible_seat` (same 360spider, SLOT=A). Not a whole-car QA PASS.

## Unmodified-source visual evidence

- [Original PMT body-side candidates – cabin view](door_from_interior.png)
- [Original PMT body-side candidates – exterior view](door_from_exterior.png)
- [Original PMT mixed material010 – cabin view](mat010_interior.png)