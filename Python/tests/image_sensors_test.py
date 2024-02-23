from tdw.controller import Controller
from tdw.output_data import ImageSensors


if __name__ == "__main__":
    c = Controller()
    resp = c.communicate([{"$type": "create_empty_environment"},
                          {"$type": "create_avatar", "id": "a", "type": "A_StickyMitten_Adult"},
                          {"$type": "send_image_sensors"}])
    for r in resp[:-1]:
        image_sensor = ImageSensors(r)
        print(image_sensor.get_avatar_id())
        print("")
        for i in range(image_sensor.get_num_sensors()):
            print(image_sensor.get_sensor_name(i))
            print(image_sensor.get_sensor_on(i))
            print(image_sensor.get_sensor_rotation(i))
            print("")
    c.communicate({"$type": "terminate"})
