from tdw.controller import Controller
from tdw.output_data import OutputData, Lights

"""
Load a streamed scene and received Lights output data.
"""

c = Controller()
resp = c.communicate([c.get_add_scene("tdw_room"),
                      {"$type": "send_lights"}])

for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    if r_id == "ligh":
        lights = Lights(resp[i])
        print("Directional lights:")
        for j in range(lights.get_num_directional_lights()):
            intensity = lights.get_directional_light_intensity(j)
            color = lights.get_directional_light_color(j)
            rotation = lights.get_directional_light_rotation(j)
            print(j, intensity, color, rotation)
        print("Point lights:")
        for j in range(lights.get_num_point_lights()):
            intensity = lights.get_point_light_intensity(j)
            color = lights.get_point_light_color(j)
            position = lights.get_point_light_position(j)
            light_range = lights.get_point_light_range(j)
            print(j, intensity, color, position, light_range)
c.communicate({"$type": "terminate"})
