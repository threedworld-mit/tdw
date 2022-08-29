from tdw.librarian import ModelLibrarian

librarian = ModelLibrarian()
for record in librarian.records:
    if not record.do_not_use and len(record.container_shapes) > 0:
        print(record.name)