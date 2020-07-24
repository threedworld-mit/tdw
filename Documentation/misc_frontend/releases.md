# TDW Releases

There are three types of releases in TDW:

### 1. Latest stable release

The **latest stable release** is usually what we recommend users download, unless they need cutting-edge functionality. This release is often behind the latest commit in `master` but always corresponds to a tagged commit such as `v1.6.0`

The [`tdw` Python module](../python/tdw.md) always matches the latest stable release.

### 2. Unstable release

The **unstable release** contains code and functionality that is still a work-in-progress and might alter the API such that you must rewrite your controller (for example, by removing a command).

The unstable release is removed when the next stable release is uploaded (for example, `v1.6.0_unstable` is removed when `v1.6.0` is uploaded).

The unstable release is always up-to-date with the latest commit on `master`. On the Releases page, it is always marked `pre-release`. 

To update the `tdw` module to an unstable release, you must uninstall and reinstall the module:

1. `pip3 uninstall tdw`
2. `cd path/to/tdw/Python` (Replace `path/to` with the actual path.)
3. `git checkout master`
4. `pip3 install -e .` (Don't forget the `.`)

### 3. Old stable releases

To downgrade to an older stable release:

1. `pip3 install tdw==version` (Replace version with a valid version, such as `v1.6.0`)
2. Download the appropriate build from the Releases page.

Additionally, each release is a tagged commit that you can checkout to, for example: 

`git checkout v1.6.0`

## Versioning

### Minor Releases

_Example:_ `v1.6.0` → `v1.6.1`

These are incremental updates. You can safely upgrade without having to alter your own code.

### Major Releases

_Example:_ `v1.6.2` → `v1.7.0`

These releases usually introduce major additions to TDW. They also typically introduce API-breaking changes (such as removing or modifying commands).

## Updates

When you first run a controller on a machine, it will automatically download a build from the same version.  The build will be downloaded to: `~/tdw_build` (where `~` is your home directory). To prevent the build from launching:

```python
c = Controller(launch_build=False)
```

The controller will check to make sure that you have an up-to-date version of the `tdw` Python module by querying PyPi; if there is a mis-match  (`1.6.0` vs. `1.6.1`; `1.6.1` vs. `1.7.0`, etc.) it will offer suggestions for how to upgrade.

Then, the controller will compare your installed version of TDW to the version of the downloaded build. If the downloaded build is out-of-date, it will be replaced with a newer version.

To suppress all version checks:

```python
c = Controller(check_version=False)
```

## Changelog

All changes to TDW are recorded in the [changelog](../Changelog.md).