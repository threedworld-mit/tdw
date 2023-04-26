from math import pi, sin, cos
from enum import Enum
from typing import List, Dict
import numpy as np
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.replicant import Replicant
from tdw.add_ons.object_manager import ObjectManager
from tdw.replicant.arm import Arm
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.ik_plans.ik_plan_type import IkPlanType
from tdw.output_data import OutputData, Raycast
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class ReplicantState(Enum):
    """
    Enum values describing the current state of the Replicant.
    """

    moving_to_cube = 0  # The Replicant is moving to a cube it wants to carry to the stack.
    reaching_for_cube = 1  # The Replicant is reaching for a cube it wants to carry to the stack.
    grasping_cube = 2  # The Replicant is grasping for a cube it wants to carry to the stack.
    resetting_arm_with_cube = 3  # The Replicant is holding a cube and is resetting its arm to a neutral holding position.
    moving_to_stack = 4  # The Replicant is holding a cube and is carrying it towards the stack.
    reaching_above_stack = 5  # The Replicant is positioning a held cube above the stack.
    dropping_cube = 6  # The Replicant has dropped the cube. The cube is falling onto the stack.
    backing_away = 7  # The Replicant is backing away from the stack.


class StackObjects(Controller):
    """
    An example of how to use advanced features of the Replicant's arm articulation to stack objects.

    This is NOT a robust use-case example, nor is it meant to be.

    For more information, read: `Documentation/lessons/replicants/arm_articulation_4.md`
    """

    def __init__(self, object_scale: float = 0.3, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        """
        This is a standard `Controller` constructor with an additional field: `object_scale`.

        `object_scale` sets the scale factor of the cubes.
        """

        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        # Add a Replicant.
        self.replicant = Replicant()
        # Add a third-person camera.
        self.camera = ThirdPersonCamera(position={"x": 0, "y": 2.2, "z": -2.61},
                                        avatar_id="a",
                                        look_at=self.replicant.replicant_id)
        # Enable image capture for the third-person camera.
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("replicant_stack_objects")
        print(f"Images will be saved to: {path}")
        self.capture = ImageCapture(avatar_ids=["a"], path=path)
        # Add an ObjectManager. We'll use this to tell the Replicant to move towards objects.
        self.object_manager = ObjectManager(transforms=True, bounds=True, rigidbodies=False)

        # This tracks the current state of the Replicant.
        self.replicant_state: ReplicantState = ReplicantState.moving_to_cube

        # A list of IDs of each cube object in the scene.
        self.cubes: List[int] = list()
        # The index in `self.cubes` of the cube the Replicant is trying to put on the stack.
        self.cube_index: int = 0

        # The position of the stack.
        # For the simplicity's sake, this is always (0, 0, 0) but you could put it somewhere else, randomize it, etc.
        self.stack_position: Dict[str, float] = {"x": 0, "y": 0, "z": 0}

        # The current height of the stack of cubes.
        # This is used to determine whether the Replicant successfully placed a cube on the stack.
        self.stack_y: float = 0

        # Each cube will be scaled by this factor.
        self.object_scale_factor: Dict[str, float] = {"x": object_scale, "y": object_scale, "z": object_scale}

        # When the Replicant is holding a cube and walking, its right hand will be at this position relative to its body.
        self.hold_object_position = {"x": 0.2, "y": 1, "z": 0.7}

    def run(self, random_seed: int = None, num_objects: int = 3) -> None:
        """
        Run a trial.

        A trial starts with a Replicant in the center of the room and cubes scattered around it.

        A trial ends when either the Replicant stacks all the cubes.

        If there is an error during the trial, it will hang indefinitely.

        :param random_seed: The random seed for the trial. If None, the seed is random.
        :param num_objects: The number of cubes in the scene.
        """

        # Reset the add-ons.
        self.add_ons.clear()
        self.replicant.reset()
        self.camera.initialized = False
        self.capture.initialized = False
        self.object_manager.reset()
        # Reset the state and the stack.
        self.replicant_state = ReplicantState.moving_to_cube
        self.cubes.clear()
        self.stack_y = 0
        self.cube_index = 0
        # Initialize the scene.
        commands = [{"$type": "load_scene",
                     "scene_name": "ProcGenScene"},
                    TDWUtils.create_empty_room(12, 12)]
        # Create a random number generator.
        if random_seed is None:
            rng = np.random.RandomState()
        else:
            rng = np.random.RandomState(random_seed)
        # Get random colors for the cubes.
        color_arrs = rng.uniform(0, 1, num_objects * 3).reshape(num_objects, 3)
        colors = []
        for color in color_arrs:
            colors.append({"r": float(color[0]), "g": float(color[1]), "b": float(color[2]), "a": 1})
        # Get random rotations for the cubes.
        object_rotations = rng.uniform(-90, 90, num_objects)
        # Add cubes in a circle around the Replicant.
        angle = 2 * pi / num_objects
        for i in range(num_objects):
            # Get the distance of the object from the center of the room.
            cube_r = float(rng.uniform(1.5, 4.8))
            # Get the position of the object by multiplying the angle by the radius.
            position = {"x": cube_r * cos(angle * i), "y": 0, "z": cube_r * sin(angle * i)}
            # Get an object ID.
            object_id = Controller.get_unique_id()
            # Add the object.
            # Set high friction and low bounciness to make it easier for the cube to stay on the stack.
            commands.extend(Controller.get_add_physics_object(model_name="cube",
                                                              object_id=object_id,
                                                              library="models_flex.json",
                                                              position=position,
                                                              rotation={"x": 0, "y": object_rotations[i], "z": 0},
                                                              default_physics_values=False,
                                                              mass=1,
                                                              scale_factor=self.object_scale_factor,
                                                              dynamic_friction=0.95,
                                                              static_friction=0.95,
                                                              bounciness=0.01,
                                                              scale_mass=False))
            # Set a random color.
            commands.append({"$type": "set_color",
                             "id": object_id,
                             "color": colors[i]})
            # Remember the ID of the cube.
            self.cubes.append(object_id)
        # Move cubes to this position.
        self.stack_position = {"x": 0, "y": 0, "z": 0}
        # Add the Replicant, the ObjectManager, the OccupancyMap, and the EmptyObjectManager.
        self.add_ons.extend([self.replicant, self.object_manager])
        # Create the scene.
        self.communicate(commands)
        # Add a camera and enable image capture.
        self.add_ons.extend([self.camera, self.capture])
        # Bake the NavMesh.
        self.communicate([])
        # Start moving.
        self.start_moving_to_cube()
        # Build the stack.
        while not self.evaluate_replicant():
            self.communicate([])

    def evaluate_replicant(self) -> bool:
        # Navigate to the next cube.
        if self.replicant_state == ReplicantState.moving_to_cube:
            if self.replicant.action.status != ActionStatus.ongoing:
                self.replicant_state = ReplicantState.reaching_for_cube
                self.communicate([])

                # Reach for the cube.
                # This is a simple rotation that doesn't need to use the optional parameters.
                self.replicant.reach_for(target=self.cubes[self.cube_index], arm=Arm.right)
        # Reach for the next cube.
        elif self.replicant_state == ReplicantState.reaching_for_cube:
            if self.action_ended(error_message=f"reach for {self.cubes[self.cube_index]}"):
                self.replicant_state = ReplicantState.grasping_cube
                self.communicate([])

                # Start to grasp the cube.
                # `angle` and `axis` define the cube's rotation per `communicate()` call.
                # `relative_to_hand=True` means that `angle` and `axis` are relative to the hand.
                self.replicant.grasp(target=self.cubes[self.cube_index],
                                     arm=Arm.right,
                                     angle=0,
                                     axis="pitch",
                                     relative_to_hand=True)
        # Grasp the next cube.
        elif self.replicant_state == ReplicantState.grasping_cube:
            if self.action_ended(error_message=f"grasp {self.cubes[self.cube_index]}"):
                self.replicant_state = ReplicantState.resetting_arm_with_cube
                self.communicate([])

                # Start to reset the arm holding the cube to a neutral holding position.
                # `absolute=False` means that the target position is relative to the Replicant's position and rotation.
                self.replicant.reach_for(target=self.hold_object_position,
                                         arm=Arm.right,
                                         absolute=False)
        elif self.replicant_state == ReplicantState.resetting_arm_with_cube:
            if self.action_ended(error_message="reset arm holding cube"):
                self.replicant_state = ReplicantState.moving_to_stack
                self.communicate([])

                # Start to move to the stack.
                # The Replicant will travel directly towards the target, ignoring any obstacles in the way.
                # In an actual use-case, this would need to be multiple move actions and include navigation planning.
                # Set `arrived_at` to a relatively large value so that the Replicant doesn't knock over the stack.
                # Don't reset the arms to maintain the neutral holding position of the hand.
                self.replicant.move_to(target=self.stack_position, arrived_at=0.8, reset_arms=False)
        # Navigate to the stack.
        elif self.replicant_state == ReplicantState.moving_to_stack:
            if self.action_ended(error_message="move to stack"):
                self.replicant_state = ReplicantState.reaching_above_stack
                self.communicate([])
                # Get a target position above the stack.
                target_position = {k: v for k, v in self.stack_position.items()}
                target_position["y"] = self.object_scale_factor["y"] * (self.cube_index + 1)

                # Reach for the point above the stack.
                # `from_held` and `held_point` will offset `target_position` by the cube's top bound point.
                # `plan` subdivides the action into horizontal and vertical components so that the hand doesn't knock over the stack.
                self.replicant.reach_for(target=target_position,
                                         arm=Arm.right,
                                         from_held=True,
                                         held_point="top",
                                         plan=IkPlanType.vertical_horizontal)
        # Reach above the stack.
        elif self.replicant_state == ReplicantState.reaching_above_stack:
            if self.action_ended(error_message="reach above stack"):
                self.replicant_state = ReplicantState.dropping_cube

                # Get the target position for the cube.
                cube_position = np.copy(self.object_manager.transforms[self.cubes[self.cube_index]].position)
                # Set the x, z coordinates to be above the stack.
                cube_position[0] = 0
                cube_position[2] = 0

                # Drop the object.
                # `offset` will reposition the cube to be directly above the stack.
                self.replicant.drop(arm=Arm.right,
                                    offset=cube_position)
        # Drop the cube.
        elif self.replicant_state == ReplicantState.dropping_cube:
            if self.action_ended(error_message=f"drop {self.cubes[self.cube_index]}"):
                self.replicant_state = ReplicantState.backing_away
                self.communicate([])

                # Start to move away from the stack. This will allow the Replicant more room for its next move action.
                # This is a very simple system that would have to be far more sophisticated in an actual use-case.
                self.replicant.move_by(distance=-0.5)
        # Reset the arm.
        elif self.replicant_state == ReplicantState.backing_away:
            if self.action_ended(error_message="back away from stack"):
                self.communicate([])
                # Did the stack's height change?
                y1 = self.raycast_stack()
                if y1 > self.stack_y:
                    self.stack_y = y1
                    self.cube_index += 1
                    # We're done!
                    if self.cube_index >= len(self.cubes):
                        return True
                    # Start moving to the next cube.
                    else:
                        self.replicant_state = ReplicantState.moving_to_cube
                        self.start_moving_to_cube()
                else:
                    print(f"Warning! Failed drop the object at the stack position.")
                    self.communicate([])
        return False

    def start_moving_to_cube(self) -> None:
        """
        Start moving the Replicant to the next cube.
        """

        cube_position = TDWUtils.array_to_vector3(self.object_manager.transforms[self.cubes[self.cube_index]].position)
        cube_position["y"] = 0

        # Move to the cube.
        # `arrived_at` is set to make sure that the Replicant is at a distance at which it's easy to pick up the cube.
        self.replicant.move_to(target=self.cubes[self.cube_index], arrived_at=0.25)

    def raycast_stack(self) -> float:
        """
        Raycast the top of the stack of cubes.

        :return: The height of the stack.
        """

        raycast_id = 0
        resp = self.communicate([{"$type": "send_raycast",
                                  "origin": {"x": self.stack_position["x"], "y": 2.8, "z": self.stack_position["z"]},
                                  "destination": self.stack_position,
                                  "id": raycast_id}])
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "rayc":
                raycast = Raycast(resp[i])
                if raycast.get_raycast_id() == raycast_id:
                    if not raycast.get_hit():
                        print("Warning! Raycast didn't hit anything.")
                    return float(raycast.get_point()[1])
        return 0

    def action_ended(self, error_message: str) -> bool:
        """
        Check if the Replicant's action ended. Print a warning if there was a problem.

        Notice that the simulation won't end if there is an error, nor will the Replicant try to change its behavior.

        :param error_message: The *infix* of a warning message. For example, `"back away from stack"` will print as `"Warning! Failed to back away from the stack."`

        :return: True if the Replicant's action ended.
        """

        if self.replicant.action.status != ActionStatus.ongoing:
            if self.replicant.action.status != ActionStatus.success:
                print(f"Warning! Failed to {error_message}: {self.replicant.action.status}")
            return True
        return False


if __name__ == "__main__":
    c = StackObjects()
    c.run(random_seed=0)
    c.communicate({"$type": "terminate"})
