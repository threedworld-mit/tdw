# Model Screenshotter

The **Model Screenshotter** loads every model in the library and creates a small image of each model.

The images will be saved to `<home user directory>/TDWImages/ModelImages/`

**You must run the Model Screenshotter before running the [Model Visualizer](https://github.com/threedworld-mit/tdw_visualizers).**

## How to run

```bash
cd <root>/Python
python3 screenshotter.py
```

```bash
<run build>
```

By default, `screenshotter.py` will capture images only of the [`models_core`](../Python/librarian/model_librarian.md) library. To capture images of all models:

```bash
cd <root>/Python
python3 screenshotter.py --type models_full
```

### Get a screenshot of a single model

```bash
cd <root>/Python
python3 screenshotter.py the_name_of_the_model
```

Replace `the_name_of_the_model` with a valid model name. Use [ModelLibrarian](../Python/librarian/model_librarian.md) to get a list of valid model names.