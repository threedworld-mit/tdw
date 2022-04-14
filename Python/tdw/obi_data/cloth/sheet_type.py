from enum import Enum


class SheetType(Enum):
    """
    Enum values for cloth sheets.
    """

    cloth = 1  # Low-resolution cloth sheet.
    cloth_hd = 2  # Medium-resolution cloth sheet.
    cloth_vhd = 3  # High-resolution cloth sheet.

