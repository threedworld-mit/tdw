from tdw.controller import Controller
from tdw.output_data import OutputData, Meshes

"""
Test Meshes data.
"""

if __name__ == "__main__":
    c = Controller()
    resp = c.communicate([{"$type": "create_empty_environment"},
                          c.get_add_object("trunck", object_id=0),
                          {"$type": "send_meshes"}])
    assert len(resp) > 1
    assert OutputData.get_data_type_id(resp[0]) == "mesh"

    m = Meshes(resp[0])
    print(m.get_vertices(0))
    print(m.get_triangles(0))
    c.communicate({"$type": "terminate"})
