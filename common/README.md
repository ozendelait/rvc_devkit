## Common tools for the Robust Vision Challenge 2020 dev kit

### Unified label space

Combining multiple datasets requires a joint label space (JLS). The dev kit provides a best-effort mapping but you are free to extend/change this mapping to your liking. 
During submission time the same mapping is applied backwards. This dev kit is provided as-is without warrenty. 
Each benchmark participating at the challenge still expects data in their respective format and will rank submissions based on this. Please remember that you should not emply methods to deliberatly train different versions for different benchmarks. Your training should try to fit the union of all training data.

The mapping file joint_mapping.json contains information to unify labels for all four task related to labels:
object detection, semantic segmentation, instance segmentation, panoptic segmentation

The resulting mappings have been generated in part from existing mappings:

[TODO: all contributions]



