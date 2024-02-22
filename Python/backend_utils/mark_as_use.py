from argparse import ArgumentParser
from tdw.librarian import ModelLibrarian


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("model_name", type=str, help="The model name.")
    parser.add_argument("--library", type=str, default="models_core.json", help="The library that the model is in.")

    args = parser.parse_args()
    library = args.library
    # Update models_core.json and models_full.json
    if library == "models_core.json":
        libraries = ["models_core.json", "models_full.json"]
    # Update just this library.
    else:
        libraries = [library]
    any_changes = False
    for library in libraries:
        lib = ModelLibrarian(library)
        record = lib.get_record(args.model_name)
        if record is None:
            continue
        any_changes = True
        record.do_not_use = False
        record.do_not_use_reason = ""
        lib.add_or_update_record(record, overwrite=True, write=True)
    msg = "Flagged " + args.model_name + " as usable."
    if any_changes:
        print(msg)
    else:
        raise Exception(f"Couldn't find a record named: {args.model_name}")

