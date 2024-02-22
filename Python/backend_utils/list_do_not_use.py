from tdw.librarian import ModelLibrarian

for library in ModelLibrarian.get_library_filenames():
    print(library + ":\n")
    records = ModelLibrarian(library).records
    records = [r for r in records if r.do_not_use]

    records = sorted(records, key=lambda r: r.name)

    if len(records) == 0:
        print("")
        continue

    output = "| Model | Reason |\n| --- | --- |"

    for r in records:
        output += "\n| " + r.name + " | " + r.do_not_use_reason + " | "

    print(output)
    print("")
