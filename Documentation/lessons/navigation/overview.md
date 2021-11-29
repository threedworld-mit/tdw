##### Navigation

# Overview

Typically, agents learn to navigate using RGB-D image data. [Read this for more information.](../visual_perception/overview.md) It is also possible to navigate using audio data, or a combination of audio+visual data; [read this for more information.](../audio/audio_perception.md)

This tutorial covers two navigation aids in TDW that *don't* utilize perception data:

- [NavMeshes](nav_mesh.md) are Unity's built-in pathfinding system. It is possible to request a navigation path  on the NavMesh.
- [Occupancy maps](occupancy_maps.md) are numpy arrays that divide a scene into a grid of cells, where each cell is occupied, out of bounds, or free. 

***

**Next: [NavMesh pathfinding](nav_mesh.md)**

[Return to the README](../../../README.md)

