from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.image_frequency import ImageFrequency
from tdw.replicant.arm import Arm
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class PhysicsTest(Controller):
    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        # Set the Replicant in the constructor so that it can be referenced by multiple functions.
        self.replicant = Replicant(position={"x": -5, "y": 0, "z": -5},
                                   image_frequency=ImageFrequency.never)
        # Likewise, we'll need to reference two object IDs, so we'll set them here.
        # We'll set the other objects' IDs in `initialize_scene()` because we won't need to reference them again.
        self.table_id = Controller.get_unique_id()
        self.box_id = Controller.get_unique_id()
        self.ball_id1 = Controller.get_unique_id()
        self.ball_id2 = Controller.get_unique_id()

    def initialize_scene(self):
        # The camera and the image capture add-ons are instantiated here, rather than in the constructor, because we won't need to reference them again.
        camera = ThirdPersonCamera(position={"x": 2, "y": 3, "z": 0.3},
                                   look_at=self.replicant.replicant_id,
                                   avatar_id="a")
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("replicant_physics_test")
        print(f"Images will be saved to: {path}")
        capture = ImageCapture(avatar_ids=[camera.avatar_id], path=path)
        self.add_ons.extend([self.replicant, camera, capture])
        # Create the room. Set a target framerate.
        commands = [TDWUtils.create_empty_room(12, 20),
                    {"$type": "set_target_framerate",
                     "framerate": 60}]
        # Add some objects.
        commands.extend(Controller.get_add_physics_object(model_name="iron_box",
                                                          object_id=self.box_id,
                                                          position={"x": -1.575, "y": 0.35, "z": 2.25},
                                                          rotation={"x": 0, "y": 0, "z": 0}))
        commands.extend(Controller.get_add_physics_object(model_name="prim_sphere",
                                                          object_id=self.ball_id1,
                                                          position={"x": 3.5, "y": 0, "z": -3.5},
                                                          rotation={"x": 0, "y": 0, "z": 0},
                                                          scale_factor={"x": 0.2, "y": 0.2, "z": 0.2},
                                                          kinematic=True,
                                                          gravity=False,
                                                          library="models_special.json"))
        commands.extend(Controller.get_add_physics_object(model_name="prim_sphere",
                                                          object_id=self.ball_id2,
                                                          position={"x": -1, "y": 0, "z": -7.5},
                                                          rotation={"x": 0, "y": 0, "z": 0},
                                                          scale_factor={"x": 0.2, "y": 0.2, "z": 0.2},
                                                          kinematic=True,
                                                          gravity=False,
                                                          library="models_special.json"))
        commands.extend(Controller.get_add_physics_object(model_name="live_edge_coffee_table",
                                                          object_id=self.table_id,
                                                          position={"x": -1, "y": 0, "z": 2},
                                                          rotation={"x": 0, "y": 20, "z": 0},
                                                          library="models_core.json"))
        commands.extend(Controller.get_add_physics_object(model_name="zenblocks",
                                                          object_id=Controller.get_unique_id(),
                                                          position={"x": -0.38, "y": 0.35, "z": 1.885},
                                                          scale_factor={"x": 0.5, "y": 0.5, "z": 0.5},
                                                          rotation={"x": 0, "y": 0, "z": 0}))
        commands.extend(Controller.get_add_physics_object(model_name="basket_18inx18inx12iin_wicker",
                                                          object_id=Controller.get_unique_id(),
                                                          position={"x": -0.8, "y": 0.35, "z": 2},
                                                          rotation={"x": 0, "y": 90, "z": 0}))
        self.communicate(commands)

    def do_action(self) -> None:
        while self.replicant.action.status == ActionStatus.ongoing:
            self.communicate([])

    def run(self) -> None:
        # Initialize the scene.
        self.initialize_scene()
        # Move to the table.
        self.replicant.move_to(target=self.table_id)
        self.do_action()
        # Reach for the table.
        self.replicant.reach_for(target=self.table_id, arm=Arm.left)
        self.do_action()
        # Grasp the table.
        self.replicant.grasp(target=self.table_id, arm=Arm.left)
        self.do_action()
        # Move to the first ball.
        self.replicant.move_to(target=self.ball_id1)
        self.do_action()
        # Drop the table.
        self.replicant.drop(arm=Arm.left)
        self.do_action()
        # Reset the arm.
        self.replicant.reset_arm(arm=Arm.left)
        self.do_action()
        # Walk to the other ball.
        self.replicant.move_to(target=self.ball_id2)
        self.do_action()
        # End the simulation.
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = PhysicsTest()
    c.run()
