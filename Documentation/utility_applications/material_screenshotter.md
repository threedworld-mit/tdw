# Material Screenshotter

The **Material Screenshotter** loads every material in the library and creates a small image of each material.

The images will be saved to `<home user directory>/TDWImages/MaterialImages/`

**You must run the  Material Screenshotter before running the [Material Visualizer](https://github.com/threedworld-mit/tdw_visualizers).**

# How to Run

```bash
cd <root>/Python
python3 screenshotter.py --type materials
```

```bash
<run build>
```

### Get a screenshot of a single material

```bash
cd <root>/Python
python3 screenshotter.py the_name_of_the_material --type materials
```

Replace `the_name_of_the_material` with a valid material name. Use [MaterialLibrarian](../Python/librarian/material_librarian.md) to get a list of valid material names.
