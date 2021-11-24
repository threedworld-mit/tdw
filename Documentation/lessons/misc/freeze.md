# Freezing your code

"Freezing" code means creating an executable binary (`.exe`, `.app`, etc.) of your controller. This executable includes all of its dependencies, which means that you can launch it on a computer that doesn't have Python or TDW installed.

## Requirements

1. Install `tdw` module
2. Clone this repo
3. Write your controller

## Usage

1. `cd path/to/tdw/Python` Replace path/to with the actual path.
2. `python3 freeze.py --controller path/to/my_controller.py` Replace path/to/my_controller.py with the actual path.

## Result

`freeze.py` will create an executable located in `~/tdw_build/tdw_controller`, where `~` is your home directory. **You can run it like an other application** by double-clicking it or running it in the terminal. Likewise, you can supply arguments to the executable like you can to a Python controller.

On Linux, you need to supply a `DISPLAY` environment to run the controller if [the launch_build parameter in the Controller constructor is True](../core_concepts/launch_build.md):

```bash
DISPLAY=:0.0 ./my_controller
```

## Limitations

`freeze.py` can only freeze code for the operating system it is running on. For example, if it is running on OS X, it can create `tdw_controller.app` for OS X but *not* `tdw_controller.exe` for Windows. This is a limitation inherent to Python.

***

[Return to the README](../../../README.md)