##### Troubleshooting

# How to report an issue

If you encounter a bug or problem in TDW, please try to follow the steps in this document to ensure that we can resolve the issue as fast as possible.

**Before reporting a bug or problem, please read the following:**

- [This list of common errors and solutions.](common_errors.md)
- Any relevant tutorial documentation. For example, if you are having trouble setting up a robotics simulation, read [the robotics tutorial](../robots/overview.md).

**To report a bug or problem, create a new [GitHub Issue](https://github.com/threedworld-mit/tdw/issues).** Please include the following:

- A concise explanation of the problem.
- The version of the `tdw` module you're using. You can find this via `pip3 show tdw`.
- A small controller that will reproduce the bug.

- Any relevant output from the Python console (such as error messages).
- [The player log](https://docs.unity3d.com/Manual/LogFiles.html) (attach this as a file to the Issue page).

[This GitHub Issue is a good example.](https://github.com/threedworld-mit/tdw/issues/218) It includes a clear explanation of the bug, code that will reproduce the bug, and even a .gif showing the faulty behavior.

Once a bug has been fixed, one of two things will happen:

1. If it was a small bug, we may choose to merge the fix into master and upload a new TDW release. In this case, we will post on the Issue to let you know it's been resolve and then close it.
2. In some cases, especially if it's difficult for us to reproduce the bug, we might open a Pull Request and ask you to test it. After merging the Pull Request to master, we'll upload a new TDW release.

***

**Next: [Common errors](common_errors.md)**

[Return to the README](../../../README.md)