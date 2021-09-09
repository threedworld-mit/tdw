##### Setup

# Upgrading TDW

## Upgrade TDW on a personal computer

1. OS X and Linux: **`sudo pip3 install tdw -U`** Windows: **`pip3 install tdw -U --user`**
2. The next time you run a controller, the TDW simulation application (the build) will automatically be updated. You can optionally download [the latest build of TDW](https://github.com/threedworld-mit/tdw/releases/latest/).
3. If this is a major upgrade (for example, from TDW v1.9.0 to TDW v1.10.0), read the [upgrade guide](../../upgrade_guides/v1.7_to_v1.8.md).
4. Read the [changelog](../../Changelog.md).

## Upgrade TDW on a remote Linux server

1. **`sudo pip3 install tdw -U`**
2. Download [the latest build of TDW](https://github.com/threedworld-mit/tdw/releases/latest/) and extract the zip file.
3. If this is a major upgrade (for example, from TDW v1.9.0 to TDW v1.10.0), read the [upgrade guide](../../upgrade_guides/v1.7_to_v1.8.md).
4. Read the [changelog](../../Changelog.md).

## When to upgrade (versioning in TDW)

- **The second number of the version (`9` in the case of `v1.9.0`) represents a *major* release.** Major releases usually introduce changes that can break a controller, such as removing commands or modifying Python function parameters. They typically also include new features. For example, TDW v1.8.0 added robotics to the API. In most cases, you'll be able to upgrade to a major release of TDW provided you edit your controller code. **Please read the [upgrade guide](../../upgrade_guides/v1.8_to_v1.9.md) and the [changelog](../../Changelog.md) before upgrading.**
- **The third number of version (`0` in the case of `v1.9.0`) represents a *minor* release.** These releases include bug fixes and new functionality such as new commands or Python wrapper functions. You should always upgrade to the latest minor release. Please read the [changelog](../../Changelog.md) before upgrading.
- **The Python module has an additional fourth number (`2` in the case of `1.9.0.2`).** These are minor patches that are almost always released to fix bugs, add models to the model library, or other features that don't actually involve the source code of the build. You should always upgrade to the latest patch release. Patch releases are not noted in the changelog.

***

**This is the end of the setup guide for TDW. We recommend you continue reading the [Core Concepts guide](../core_concepts/controller.md).**

[Return to the README](../../../README.md)
