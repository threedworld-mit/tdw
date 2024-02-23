from tdw.output_data import OutputData, Volumes
from tdw.controller import Controller


if __name__ == "__main__":
    c = Controller()
    resp = c.communicate([{"$type": "create_empty_environment"},
                          c.get_add_object("rh10", object_id=0),
                          {"$type": "send_volumes",
                           "frequency": "once"}])
    assert len(resp) > 1
    assert OutputData.get_data_type_id(resp[0]) == "volu"
    volumes = Volumes(resp[0])
    assert volumes.get_num() == 1
    assert volumes.get_object_id(0) == 0
    print(volumes.get_volume(0))
    c.communicate({"$type": "terminate"})
