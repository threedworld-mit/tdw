from pathlib import Path
from typing import Union, Dict
from pathlib import Path
import numpy as np

# A target position or object: an integer (an object ID), a numpy array (a position), or a dictionary (a position).
TARGET = Union[int, np.ndarray, Dict[str,  float]]

# A position: A numpy array or a dictionary.
POSITION = Union[np.ndarray, Dict[str, float]]

# A rotation: A numpy array or a dictionary.
ROTATION = Union[np.ndarray, Dict[str, float]]

# A string of a path or a Path-like object.
PATH = Union[str, Path]
