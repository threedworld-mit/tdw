# `single_object.py`

**Seth Alter
October 2019**

## Overview

`single_object.py` is the final iteration of the controller used to generate image datasets for Martin Schrimpf's and Jonas Kubilius' ImageNet transfer research.

This controller will search the records databases for all model categories in the TDW library. It will then add the object to the scene, and then generate a target number of images per category, using all models in that category. Each model is added in sequentially to the scene; there is always exactly 1 model in the scene.

To increase variability, each image has randomized camera and positional parameters, and may have additional random parameters, such as the angle of sunlight or the visual materials of the model. This randomness is constrained somewhat in order to guarantee a degree of compositional quality (namely, that the object is guaranteed to always be at least partially in the frame).

`single_object.py` uses the highest-quality rendering available in TDW. Given that it is therefore necessarily slower than simulations rendering at low quality (or not at all), this controller is _highly_ optimized to be as fast as _possible_.

Standard datasets have 1300000 "train" images and 50000 "val" images. A full dataset requires approximately 8 hours to generate using high-end hardware.

## Usage

### Option A: Run `single_object.py` from the terminal

1. `cd <root>/Python/use_cases/single_object`
2. `python3 single_object.py [ARGUMENTS]`
4. `<run build>`

#### Arguments

| Argument           | Type  | Default          | Description                                                  |
| ------------------ | ----- | ---------------- | ------------------------------------------------------------ |
| `--scene_name`     | str   | tdw_room         | The name of the scene. See [SceneLibrarian documentation](../librarian/scene_librarian.md). |
| `--output_dir`     | str   | D:/Test          | The absolute path to the output directory.                   |
| `--materials`      |       |                  | Set random visual materials per frame.                       |
| `--new`            |       |                  | Start a new dataset (erases the log of completed models).    |
| `--screen_size`    | int   | 256              | The screen size of the build.                                |
| `--output_size`    | int   | 256              | Images are resized to this from the screen size.             |
| `--hdri`           |       |                  | Use a random HDRI skybox per frame.                          |
| `--hide`           |       |                  | Hide all objects.                                            |
| `--clamp_rotation` |       |                  | Clamp rotation to +/- 30 degrees on each axis, rather than totally random. |
| `--port`           | int   | 1071             | The port for the controller and build.                       |
| `--max_height`     | float | 1                | Objects and avatars can be at this percentage of the scene bounds height. Must be between 0 and 1. |
| `--grayscale`      | float | 0.5              | Target grayscale value. Must be between 0 and 1. Higher value = better composition and slower FPS. |
| `--less_dark`      |       |                  | Prefer fewer "dark" skyboxes.                                |
| `--id_pass`        |       |                  | Include the _id pass.                                        |
| `--no_overwrite`   |       |                  | If true, don't overwrite existing images, and start indexing after the highest index. |
| `--zip`            |       |                  | Zip the images after finishing the dataset. Requires Windows and 7zip. |
| `--train`          | int   | 1300000          | Total number of train images.                                |
| `--val`            | int   | 50000            | Total number of val images.                                  |
| `--library`        | str   | models_core.json | The path to the [model library records file](../librarian/model_librarian.md). |
| `--launch_build`   |       |                  | Automatically launch the build; download the build if one isn't present or if the build is the wrong version. |

### Option B: Use the `SingleObject` controller class

```python
from single_object import SingleObject

s = SingleObject()
s.run("D:/output_directory")
```

See `SingleObject.__init__` for a complete list of constructor parameters.

### Option C: `multi_env.py`

1. `cd <root>/Python/use_cases/single_object`
2. `python3 multi_env.py [ARGUMENTS]`
4. `<run build>`

`multi_env.py` creates a `SingleObject` instance and then generates a full dataset using six different scenes. The parameters used in this script are meant to be as "optimized" as possible in terms of transfer results.

#### Arguments

| Argument    | Type | Default            | Description                                           |
| ----------- | ---- | ------------------ | ----------------------------------------------------- |
| `--library` | str  | `models_full.json` | The [model library](../librarian/model_librarian.md). |
| `--dir`     | str  |                    | The output directory.                                 |

## How It Works

### 1. Generate metadata

Every dataset has an associated `metadata.txt` file, which contains a serialized JSON object of all of the parameters used to generate this dataset. This can be very useful if you are generating many datasets with slightly different parameters.

### 2. Initialize the scene

Each dataset uses exactly 1 scene (`multi_env.py` sidesteps this limitation by running 6 datasets sequentially). The scene's global parameters and post-processing parameters are initialized.

Each scene has one more more "environments", which are spatial boxes in which you expect images to look reasonable. It is possible in TDW to instantiate objects and avatars beyond these limits, but they will be in a blank void. In `single_object.py`, the avatar and object positions are always constrained to the scene's environments.`initialize_scene` returns a list of these environments.

### 3. Fetch records

The controller fetches a list of all model categories ("wnids") in the model library. It removes the category `99999999` (reserved for special-case models) and any models flagged as `do_not_use`. Any remaining non-empty categories will be included in the dataset.

### 4. Iterate through each wnid

The controller fetches a list of all records in the wnid. If the model has been "processed" (that is, `single_object.py` generated all of the images for this model), the model is skipped over.

### 5. Iterate through each model

#### 5a. Set the starting index

Images are always saved as `<filename>_<index>.jpg`. If `SingleObject.no_overwrite == False`, the starting index is always `0000`. Otherwise, the starting index will be the number after the last index (if any). This is mostly useful for cases like `multi_env.py` in which you don't want sequential datasets to overwrite each other's images. If you're using only one scene, you probably want images to be overwritten to avoid generating extras if you have to restart the controller.

#### 5b. Add the object and set the scene for grayscale capture

_If you see the window become tiny, this is expected behavior!_

To generate images, `single_object` runs each model through two loops. The first loop captures camera and object positions, rotations, etc. Then, these cached positions are played back in the second loop to generate images. Image capture is divided this way because the first loop will "reject" a lot of images with poor composition; this rejection system doesn't require image data, and so sending image data would slow down the entire controller.

`single_object.py` relies on [`IdPassGrayscale`](../../api/output_data.md) data to determine whether an image has good composition. This data reduces the rendered frame of an `_id` pass to a single pixel and returns the grayscale value of that pixel. The `IdPassGrayscale` has obvious limitations, but it's big advantage is that it is the fastest way to receive any observation data from the TDW build. It also doesn't need a large window size to be useful; in fact, it runs faster if the window is smaller. So, to start the positional loop, the entire window is resized to 32x32 and render quality is set to minimal.

Each object, once instantiated, is set to "unit scale", with its longest extent being set to 1 meter. This way, `single_object.py` can reliably frame every object using the same positional and rotational parameters.

#### 5c. Positional Loop

Gather valid `ImagePosition` objects until the list of `ImagePositions` equals the target number of images to capture. An `ImagePosition` object contains:

- The avatar position
- The camera rotation
- The object position
- The object rotation

Each iteration in the loop has two steps:

1. "Optimal" grayscale. Teleport the avatar and the object high above the scene. Set the positions and rotations of the avatar and the object, and return the `IdPassGrayscale` value. This gives the controller an "ideal" grayscale value, in which nothing occludes the object.
2. "Real" grayscale. Teleport the avatar and object back to a reasonable height within the scene. Apply the exact same positional and rotational commands as in the "Optimal" step and get a new grayscale value.

Then, compare the "real" grayscale to the "optimal" grayscale:

- If `real_grayscale / optimal_grayscale > grayscale_threshold`, then this is a "good" image. The `ImagePosition` is cached in the list.
- Otherwise, the object is too occluded and these positional/rotational parameters are rejected.

#### 5d. Image Loop

Once `single_object.py` has enough cached `ImagePosition` data, it can begin to actually generate images. Image quality is now set to maximum, and the screen size is set to the desired image capture size (by default, 256x256).

Every iteration, the object and avatar are positioned and rotated according to the cached `ImagePosition` data. Image data is received and written to disk. This image saving is handled via threading to prevent the controller from slowing down.

##### Optional Additional Commands

- If the `visual_material_swapping` parameter of the constructor was `True`: Per frame, all of the object's visual materials will be randomly set to materials from the material library.
- If the `hdri` parameter of the constructor was `True`: Periodically set a new HDRI skybox. Per frame, set a random rotation for the HDRI skybox.

#### 5e. Cleanup

Destroy the model and unload its asset bundle from memory.

### 6. Create a .zip file

After generating the whole dataset, `single_object.py` will zip the dataset directory and destroy the original files. If you don't want the controller to do this, set `do_zip` to `False` in the constructor.

## Known Limitations

- `SingleObject` can't include physics simulations. If it allowed objects to "fall" or otherwise move before image capture, the positional loop wouldn't work at all (because the object would immediately fall out of frame during the "optimal" pass). This is not to say that large physics-driven datasets are not _possible_ in TDW, just that this particular controller is not at all suited for them.
- As per the name, `SingleObject` only works if there's one model in the scene. All of the image composition logic assumes that there is only one object to rotate, position, frame, etc.
- There's no built-in way to automatically transfer a large dataset between machines. This is due to limitations in Windows file transfer options, but there are probably reasonable workarounds available with Ubuntu for Windows.
- `single_object.py` has been tested almost exclusively on Windows.