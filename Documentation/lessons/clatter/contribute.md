##### Clatter

# How to Contribute to Clatter

As described in the [overview](overview.md), Clatter is a separated repo from `tdw` and the private repo that the build is in. [This is the repo.](https://github.com/alters-mit/clatter/) You can fork the repo and open a pull request.

To update Clatter in the build, you need to have access to the private TDWBase repo.

1. In the Clatter repo, make sure the solution is set to "Release" and then build Clatter.Core.dll and Clatter.Unity.dll
2. Make a new branch in TDWBase.
3. Copy+paste the .dll files into `TDWBase/TDWBase/Assets/Clatter`
4. Commit and push.

In some cases, you'll also need to adjust the Clatter C# commands in TDWBase to be able to reference changes to the Clatter library. These changes should be included in the same branch as the one with the new .dll files.

If the C# commands change, you'll probably need to update the `Clatter` add-on as well. Make a new branch in the `tdw` repo, make your changes, commit, and push.

***

**This is the last document in the "Clatter" tutorial.**

[Return to the README](../../../README.md)