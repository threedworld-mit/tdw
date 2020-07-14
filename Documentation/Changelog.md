# CHANGELOG

# v1.6.x

## v1.6.0

This changelog is only for the _frontend_ of TDW. If you are a backend developer, or are looking for changes prior to v1.6.0, please refer to the changelog in TDWBase.

### New Features

- **Began new `tdw` repo (split from the private dev `TDWBase` repo).**
  - Removed backend scripts and documentation (they are still in `TDWBase`).

### Command API

#### Modified Commands

| Command                               | Modification                                                 |
| ------------------------------------- | ------------------------------------------------------------ |
| `create_avatar`                       | Parameter `id` now has a default value: `"a"`.               |
| `set_rendering_quality`               | Parameter `render_quality` now has a default value: `5`      |
| `scale_avatar`                        | Parameter `scale_factor` now has a default value: `{"x": 1, "y": 1, "z": 1}` |
| `set_avatar_collision_detection_mode` | Parameter `mode` now has a default value: `"continuous_speculative"`. |
| `set_avatar_forward`                  | Parameter `forward` now has a default value: `{"x": 0, "y": 0, "z": 1}` |
| `set_field_of_view`                   | Parameter `field_of_view` now has a default value: `35`      |
| `apply_force_to_avatar`               | Parameter `direction` now has a default value: `{"x": 0, "y": 0, "z": 1}` |
| `apply_force_to_object`               | Parameter `force` now has a default value: `{"x": 0, "y": 0, "z": 1}` |
| `scale_object`                        | Parameter `scale_factor` now has a default value: `{"x": 1, "y": 1, "z": 1}` |
| `set_object_collision_detection_mode` | Parameter `mode` now has a default value: `"continuous_speculative"`. |
| `send_collisions`                     | Default values for `stay` and `exit` are `False` (both were `True`) |
| `bake_nav_mesh` | Replaced parameters `carve` and `carve_only_stationary` with new parameter `carve_type`. |

#### Removed Commands

| Command                       | Reason                                                       |
| ----------------------------- | ------------------------------------------------------------ |
| `set_day_night`               | This command enabled/disabled all lights in the scene; HDRI skyboxes can be used for *far* better results. |
| `set_material_from_resources` | Only usable in forked versions of TDWBase with extra materials in Resources/. Functionality can be replicated with local material asset bundles. |
| `set_semantic_material`       | Always sets the material as `"undefined"` (because visual materials are, as yet, unclassified). Note: `set_semantic_material_to` is still in the Command API. |
| `update_flex_container`       | Deprecated in v1.5                                           |
| `set_gravity` | Doesn't work as advertised (it makes objects kinematic too).<br>Functionality overlaps with `set_kinematic_state`, `simulate_physics`, and `set_gravity_vector`. |
| `set_shadows` | Functionality can be replicated via: `{"$type": "set_render_quality", "render_quality": 0}`<br>Note: `set_shadow_strength`, a different command, hasn't been removed. |

### Asset Bundle Libraries

- **Updated asset bundle URLs for every asset bundle.** The URLs now point towards binaries stored in the `tdw-public` and `tdw-private` S3 buckets.

#### Models

##### `models_full.json`

- **All models in `models_full.json` that are not also in `models_core.json` ("non-free models") now require S3 access keys in order to download.**

### Python

- Set default `--library` value in `multi_env.py` to `models_full.json` (was `models_core.json`)
- Slight efficiency improvements in `single_object.py`

### Documentation

#### New Documentation

| Document      | Description                                        |
| ------------- | -------------------------------------------------- |
| `releases.md` | Overview of how TDW releases and versioning works. |

#### Modified Documentation

| Document | Modification |
| -------- | ------------ |
| `command_api.md` | _Many_ adjustments to the command descriptions, such as removing obsolete or misleading info, links to other docs, and minor clarifications.<br>Added a reference for all Asset Bundle Commands to their associated wrapper functions (e.g. `add_object` -> `Controller.get_add_object`).<br>Added a note for how to format the URL of a local asset bundle.<br>Clarified which "destroy" commands (e.g. `destroy_object`) retain the cached asset bundle in memory.<br>Grouped humanoid commands into a "Humanoid Command" section.<br>Converted many references to other documents into URLs. |
| `README.md` | Removed links to backend documentation. |
| `getting_started.md` | Updated for `v1.6.0` |
| `command_api_guide.md` | Added a few more examples.<br>Added a section explaining default parameter values. |
| `models_full.md` | Added optional instruction to run the screenshotter. |
| `doc_gen.md` | Extensive rewrite based on the new functionality. |
| `machine_performance.md` | Removed links to TDWBase Issues. |
| `flex.md` | Removed links to TDWBase Issues. |
| `impact_sounds.md` | Fixed a bad link. |
| `shapenet.md` | Fixed a bad link. |
| `video.md` | Fixed a bad link. |

#### Removed Documentation

- Removed all backend documentation from this repo.