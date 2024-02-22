from pathlib import Path
from tdw.librarian import ModelLibrarian

"""
Verify that the records of each new model are ok.
"""

lib_full = ModelLibrarian("models_full.json")
lib_core = ModelLibrarian("models_core.json")
models = Path("full_to_core.txt").read_text().strip().split("\n")
for m in models:
    record_core = lib_core.get_record(m)
    if record_core is not None:
        print(f"{m} is already in models_core.json")
        continue
    record_full = lib_full.get_record(m)
    if record_full is None:
        print(f"{m} doesn't exist in models_full.json")
        continue
    if record_full.do_not_use:
        print(f"{m} is do_not_use because {record_full.do_not_use_reason}")
