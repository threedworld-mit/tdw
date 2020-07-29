# `tdw` module

`tdw` is a Python module that contains scripts that are mandatory for any controller.

## Installation

```bash
pip3 install tdw
```

## Contents

### Frontend

| Script                                               | Description                                              |
| ---------------------------------------------------- | -------------------------------------------------------- |
| [Controller](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/controller.md)             | Base class for all controllers.                             |
| [TDWUtils](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/tdw_utils.md)                | Utility class.                                              |
| [AssetBundleCreator](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/asset_bundle_creator.md) | Covert 3D models into TDW-compatible asset bundles.         |
| [PyImpact](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/py_impact.md)                | Generate impact sounds at runtime.                          |
| [DebugController](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/debug_controller.md)  | Child class of `Controller` that has useful debug features. |
| [Librarian](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/librarian/librarian.md)     | "Librarians" hold asset bundle metadata records.            |
| [BinaryManager](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/binary_manager.md)      | Manage multiple instances of TDW builds on a remote server. |
| [FluidTypes](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/fluid_types.md)            | Access different NVIDIA Flex fluid types.                   |

### Backend

Read [this](backend.md). Don't use these scripts unless you're a backend developer of TDW.