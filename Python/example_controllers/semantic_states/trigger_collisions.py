from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.trigger_collision_manager import TriggerCollisionManager
from tdw.add_ons.third_person_camera import ThirdPersonCamera


class TriggerCollisions(Controller):
    """
    An example of how to attach trigger colliders to objects and listen for trigger collision events.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        # Create the trigger collision manager.
        self.trigger_collision_manager: TriggerCollisionManager = TriggerCollisionManager()
        # Create a camera.
        camera = ThirdPersonCamera(position={"x": 0.5, "y": 2, "z": 2},
                                   look_at={"x": 0, "y": 0.6, "z": 0})
        self.add_ons.extend([camera, self.trigger_collision_manager])
        # Create an empty scene.
        self.communicate(TDWUtils.create_empty_room(12, 12))

    def trial(self, basket_force: float, ball_force: float) -> None:
        # Reset the trigger collision manager between trials.
        self.trigger_collision_manager.reset()
        # Add the objects.
        basket_id = Controller.get_unique_id()
        commands = Controller.get_add_physics_object(model_name="basket_18inx18inx12iin_bamboo",
                                                     object_id=basket_id,
                                                     position={"x": 1, "y": 0.5, "z": 0},
                                                     rotation={"x": -90, "y": 0, "z": 90},
                                                     library="models_core.json")
        ball_id = Controller.get_unique_id()
        commands.extend(Controller.get_add_physics_object(model_name="sphere",
                                                          object_id=ball_id,
                                                          position={"x": -1, "y": 0, "z": 0},
                                                          scale_factor={"x": 0.3, "y": 0.3, "z": 0.3},
                                                          library="models_flex.json",
                                                          default_physics_values=False,
                                                          scale_mass=False,
                                                          mass=0.3))
        # Apply forces to the objects.
        commands.extend([{"$type": "apply_force_to_object",
                          "id": basket_id,
                          "force": {"x": -basket_force, "y": 0, "z": 0}},
                         {"$type": "apply_force_to_object",
                          "id": ball_id,
                          "force": {"x": ball_force, "y": 0, "z": 0}}])
        # Attach a trigger collider.
        self.trigger_collision_manager.add_box_collider(object_id=basket_id,
                                                        position={"x": 0, "y": 0.15855943, "z": 0},
                                                        scale={"x": 0.4396923, "y": 0.29288113, "z": 0.43977804})
        # Send the commands.
        self.communicate(commands)
        print(f"Basket ID: {basket_id}")
        print(f"Ball ID: {ball_id}")
        for i in range(200):
            for trigger_collision in self.trigger_collision_manager.collisions:
                if trigger_collision.collidee_id == basket_id:
                    if trigger_collision.state == "enter":
                        print(f"{i} {trigger_collision.collider_id} entered {trigger_collision.collidee_id}")
                    elif trigger_collision.state == "exit":
                        print(f"{i} {trigger_collision.collider_id} exited {trigger_collision.collidee_id}")
            self.communicate([])
        # Destroy the objects.
        self.communicate([{"$type": "destroy_object",
                           "id": basket_id},
                          {"$type": "destroy_object",
                           "id": ball_id}])


if __name__ == "__main__":
    c = TriggerCollisions(launch_build=False)
    c.trial(basket_force=8, ball_force=2)
    c.communicate({"$type": "terminate"})
