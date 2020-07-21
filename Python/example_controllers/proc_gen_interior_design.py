import numpy as np
import random
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.output_data import Bounds, Transforms


"""
Procedurally furnish a room with basic relational semantic rules.
"""


class ProcGenInteriorDesign(Controller):
    SIDE_TABLE = ["coffee_table_glass_round", "de_castelli_placas_table", "lg_table_white", "lg_table_marble_green",
                  "sm_table_white", "glass_table_round", "side_table_wood", "trapezoidal_table"]
    SIDE_TABLE_ON = ["candle", "f10_apple_iphone_4", "vase_01",
                     "vase_02", "vase_03", "vase_05", "vase_06", "macbook_air", "zenblocks",
                     "baton_table_lamp_dark", "black_lamp", "desk_lamp", "kevin_reilly_pattern_table_lamp",
                     "lamp_02", "red_lamp", "rope_table_lamp", "spunlight_designermesh_lamp", "white_lamp"]
    CIRCULAR_TABLE = ["coffee_table_glass_round", "de_castelli_placas_table", "de_castelli_placas_table_low",
                      "glass_table_round"]

    SOFA = ["alivar_tech_bench_sofa", "arflex_hollywood_sofa", "arflex_strips_sofa", "barcelona_bench_sofa",
            "meridiani_belmondo_bench_sofa", "meridiani_freeman_sofa", "minotti_helion_3_seater_sofa",
            "molteni_turner_sofa", "napoleon_iii_sofa", "on_the_rocks_sofa", "poliform_atollo_curved_sofa",
            "sayonara_sofa"]
    SOFA_FRONT_OF = ["luggage_bag_1", "macbook_air"]
    SOFA_SIDE_OF = ["alma_floor_lamp", "arturoalvarez_v_floor_lamp", "bakerparisfloorlamp03", "bastone_floor_lamp"]
    DINING_TABLE = ["willisau_varion_w3_table"]
    DINING_CHAIR = ["brown_leather_dining_chair", "chair_billiani_doll", "chair_willisau_riale", "wood_chair"]
    DINING_TABLE_SETTING = ["spoon2", "servingfork"]
    DINING_TABLE_CENTERPIECE = ['candle', 'serving_bowl', 'vase_01',
                                'vase_02', 'vase_03', 'vase_05', 'vase_06', 'jug01', 'jug02', 'jug03', 'jug04', 'jug05',
                                'skillet_open', 'pot', 'kettle']

    def run(self):
        self.start()

        width = 12
        length = 12

        # Create an empty room.
        self.communicate(TDWUtils.create_empty_room(width, length))

        # Disable physics.
        self.communicate({"$type": "simulate_physics",
                          "value": False})

        # Add the avatar.
        self.communicate(TDWUtils.create_avatar(position={"x": -5, "y": 10, "z": -2},
                                                look_at=TDWUtils.VECTOR3_ZERO))

        # Create the dining table.
        self.dining_table()

        # Create the sofa.
        self.sofa(width, length)

        # Bake the NavMesh.
        self.communicate({"$type": "bake_nav_mesh",
                          "carve_type": "none"})
        # Get a random position on the NavMesh.
        position = TDWUtils.get_random_position_on_nav_mesh(self, width, length)
        position = TDWUtils.array_to_vector3(position)
        # Add a side table.
        self.side_table(position)

    def all_objects_look_at(self, object_ids, target_position=TDWUtils.VECTOR3_ZERO):
        commands = []
        for object_id in object_ids:
            commands.append({"$type": "object_look_at_position",
                             "id": object_id,
                             "position": target_position})
        self.communicate(commands)

    def get_transforms_data(self, object_ids):
        resp = self.communicate({"$type": "send_transforms",
                                 "frequency": "once",
                                 "ids": object_ids})

        transforms = Transforms(resp[0])
        return transforms

    def get_bounds_data(self, object_id):
        resp = self.communicate({"$type": "send_bounds",
                                 "frequency": "once",
                                 "ids": [object_id]})
        return Bounds(resp[0])

    def move_objects_along_forward(self, transforms: Transforms, delta, y=0):
        commands = []
        for i in range(transforms.get_num()):
            object_id = transforms.get_id(i)
            position = transforms.get_position(i)
            forward = transforms.get_forward(i)

            deltas = [d * delta for d in forward]

            position = {"x": position[0] + deltas[0],
                        "y": y,
                        "z": position[2] + deltas[2]}
            commands.append({"$type": "teleport_object",
                             "id": object_id,
                             "position": position})
        self.communicate(commands)

    def random_rotation(self, object_ids, max_angle=45):
        commands = []
        for object_id in object_ids:
            commands.append({"$type": "rotate_object_by",
                             "angle": random.uniform(-max_angle, max_angle),
                             "axis": "yaw",
                             "id": object_id,
                             "is_world": True})
        self.communicate(commands)

    def dining_table(self):
        """
        1. Create a dining table in the center of the room.
        2. Create four chairs, one on each side of the table.
        3. Create "table settings" in front of each chair on the table.
        4. Create a centerpiece on the table.
        """

        # Create a dining table in the center of the room.
        dining_table_id = self.add_object(random.choice(ProcGenInteriorDesign.DINING_TABLE))

        # Get the table bounds.
        dining_table_bounds = self.get_bounds_data(dining_table_id)

        # Create the chairs.
        # Get the model.
        chair_model_name = random.choice(ProcGenInteriorDesign.DINING_CHAIR)

        # Get the chair positions.
        chair_positions = [dining_table_bounds.get_left(0),
                           dining_table_bounds.get_right(0),
                           dining_table_bounds.get_front(0),
                           dining_table_bounds.get_back(0)]

        top = dining_table_bounds.get_top(0)

        chair_ids = []
        for chair_pos in chair_positions:
            # Create the chair.
            chair_id = self.add_object(chair_model_name,
                                       position={"x": chair_pos[0], "y": 0, "z": chair_pos[2]})
            chair_ids.append(chair_id)

        # Look at the table.
        self.all_objects_look_at(chair_ids)

        # Get transforms data.
        transforms = self.get_transforms_data(chair_ids)

        # Move the chairs away.
        self.move_objects_along_forward(transforms, -0.5)

        # Create table place settings.
        setting_ids = []

        for chair_pos in chair_positions:
            # Add a random object.
            setting_id = self.add_object(random.choice(ProcGenInteriorDesign.DINING_TABLE_SETTING),
                                         position={"x": chair_pos[0], "y": top[1], "z": chair_pos[2]})
            setting_ids.append(setting_id)

        # Look at the table.
        self.all_objects_look_at(setting_ids, target_position={"x": 0, "y": top[1], "z": 0})

        # Get transforms data.
        transforms = self.get_transforms_data(setting_ids)

        # Move the settings onto the table.
        self.move_objects_along_forward(transforms, 0.25, y=top[1])

        # Rotate the settings randomly.
        self.random_rotation(setting_ids)

        # Create a centerpiece.
        self.add_object(random.choice(ProcGenInteriorDesign.DINING_TABLE_CENTERPIECE),
                        position={"x": 0, "y": top[1], "z": 0},
                        rotation={"x": 0, "y": random.uniform(-45, 45), "z": 0})

    def sofa(self, width, length):
        """
        1. Create a sofa in the corner in the room.
        2. Create some objects in front of the sofa.
        3. Create some objects the sides of the sofa.

        :param width: The width of the room.
        :param length: The length of the room.
        """

        # Add the sofa in the corner of the room.
        sofa_position = {"x": width / 2 - 2, "y": 0, "z": length / 2 - 2}
        sofa_id = self.add_object(random.choice(ProcGenInteriorDesign.SOFA),
                                  position=sofa_position)

        # Rotate the sofa to face the center of the room.
        self.communicate({"$type": "object_look_at_position",
                          "id": sofa_id,
                          "position": TDWUtils.VECTOR3_ZERO})

        sofa_bounds = self.get_bounds_data(sofa_id)

        # Set the rotation to match the sofa.
        sofa_transform = self.get_transforms_data([sofa_id])
        sofa_rotation = sofa_transform.get_rotation(0)
        sofa_rotation = {"x": sofa_rotation[0],
                         "y": sofa_rotation[1],
                         "z": sofa_rotation[2],
                         "w": sofa_rotation[3]}

        # Get a focal point for objects to place in front of the sofa.
        centerpoint = TDWUtils.extend_line(np.array(sofa_bounds.get_center(0)), np.array(sofa_bounds.get_front(0)), 0.5)
        centerpoint[1] = 0

        # Place objects in front of the sofa at various positions near the centerpoint.
        for i in range(random.randint(1, 3)):
            pos = TDWUtils.get_random_point_in_circle(centerpoint, 0.125)
            pos = TDWUtils.array_to_vector3(pos)
            self.add_object(random.choice(ProcGenInteriorDesign.SOFA_FRONT_OF),
                            position=pos,
                            rotation={"x": 0, "y": random.uniform(-30, 30), "z": 0})

        # Create 1-2 objects to the sides of the sofa.
        positions = [sofa_bounds.get_left(0), sofa_bounds.get_right(0)]
        random.shuffle(positions)
        if random.random() > 0.5:
            positions.pop(0)

        for side_position in positions:
            side_position = [side_position[0], 0, side_position[2]]
            side_position = TDWUtils.array_to_vector3(side_position)
            # Create a side table.
            if random.random() > 0.5:
                self.side_table(side_position, (sofa_position, sofa_rotation))
            # Create some other object.
            else:
                # Create the object.
                side_id = self.add_object(random.choice(ProcGenInteriorDesign.SOFA_SIDE_OF),
                                          position=side_position)

                self.side_of(side_id, sofa_position, sofa_rotation)

    def side_of(self, object_id, parent_position, parent_rotation):
        """
        Create an object to the another object.

        :param object_id: This object's ID.
        :param parent_position: The position of the parent object (Vector3).
        :param parent_rotation: The rotation of the parent object (Quaternion).
        """

        # Look at the parent.
        self.communicate({"$type": "object_look_at_position",
                          "id": object_id,
                          "position": parent_position})
        # Move away from the parent.
        self.move_objects_along_forward(self.get_transforms_data([object_id]), -0.25)

        # Set the rotation of this object to match the parent.
        self.communicate({"$type": "rotate_object_to",
                          "id": object_id,
                          "rotation": parent_rotation})

    def side_table(self, position, parent=None):
        """
        1. Create a side table.
        2. Maybe create an object on the side table.

        :param position: The position of the table (Vector3).
        :param parent: THe parent parameters: (position, rotation).
        """

        # Create the table.
        table_id = self.add_object(random.choice(ProcGenInteriorDesign.SIDE_TABLE),
                                   position=position)

        if parent:
            # Place the object to the side of the parent and match its rotation.
            parent_position = parent[0]
            parent_rotation = parent[1]

            self.side_of(table_id, parent_position, parent_rotation)
        else:
            # Apply a random rotation.
            self.communicate({"$type": "rotate_object_by",
                              "angle": random.uniform(-45, 45),
                              "axis": "yaw",
                              "id": table_id,
                              "is_world": True})
        # Maybe put an object on the table.
        if random.random() > 0.25:
            # Get the top position of the table.
            table_bounds = self.get_bounds_data(table_id)
            on_pos = table_bounds.get_top(0)
            on_y = on_pos[1]
            # Perturb the position slightly.
            on_pos = TDWUtils.get_random_point_in_circle(np.array(on_pos), 0.125)
            on_pos[1] = on_y
            on_pos = TDWUtils.array_to_vector3(on_pos)
            on_rot = {"x": 0, "y": random.uniform(-45, 45), "z": 0}
            # Add the object.
            self.add_object(random.choice(ProcGenInteriorDesign.SIDE_TABLE_ON),
                            position=on_pos,
                            rotation=on_rot)


if __name__ == "__main__":
    ProcGenInteriorDesign().run()
