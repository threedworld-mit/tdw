# ReplicantStatic

`from tdw.replicant.replicant_static import ReplicantStatic`

Static data for the Replicant.

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `ARM_JOINTS` | Dict[Arm, List[ReplicantBodyPart]] | A dictionary of arms and their constituent joints. | `{Arm.left: [__b for __b in ReplicantBodyPart if __b.name.endswith("_l")],` |

***

## Fields

- `replicant_id` The ID of the Replicant.

- `avatar_id` The ID of the Replicant's avatar (camera). This is used internally for API calls.

- `body_parts` Body parts by name. Key = [`ReplicantBodyPart`](replicant_body_part.md). Value = Object ID.

- `segmentation_color` The Replicant's segmentation color.

- `hands` The Replicant's hands. Key = [`Arm`](arm.md). Value = Hand ID.

- `body_parts_by_id` Body parts by ID. Key = Object ID. Value = [`ReplicantBodyPart`](replicant_body_part.md).

***

## Functions

#### \_\_init\_\_

**`ReplicantStatic(replicant_id, resp)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| replicant_id |  int |  | The ID of the Replicant. |
| resp |  List[bytes] |  | The response from the build. |

