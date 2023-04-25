from enum import Enum
from typing import List, Dict
from itertools import permutations
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
    moving_to_cube = 0
    reaching_for_cube = 1
    grasping_cube = 2
    resetting_arm_with_cube = 3
    moving_to_stack = 4
    reaching_above_stack = 5
    dropping_cube = 6
    backing_away = 7


class StackObjects(Controller):
    def __init__(self, object_scale: float = 0.3, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.replicant = Replicant()
        self.camera = ThirdPersonCamera(position={"x": 0, "y": 2.2, "z": -2.61},
                                        avatar_id="a",
                                        look_at=self.replicant.replicant_id)
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("replicant_stack_objects")
        print(f"Images will be saved to: {path}")
        self.capture = ImageCapture(avatar_ids=["a"], path=path)
        self.object_manager = ObjectManager(transforms=True, bounds=True, rigidbodies=False)
        self.replicant_state: ReplicantState = ReplicantState.moving_to_cube
        self.cubes: List[int] = list()
        self.stack_position: Dict[str, float] = dict()
        self.stack_y: float = 0
        self.cube_index: int = 0
        self.object_scale: float = object_scale
        self.hold_object_positions: Dict[Arm, Dict[str, float]] = {arm: {"x": x, "y": 1, "z": 0.7} for arm, x in zip([Arm.left, Arm.right], [-0.2, 0.2])}

    def run(self, random_seed: int = None, num_objects: int = 5) -> None:
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
        # Create an occupancy map. This works because we know that there is only one room and we know its dimensions.
        xs = np.linspace(-4.8, 4.8, 10)
        zs = xs.copy()
        indices = np.array(list(permutations(np.arange(0, xs.shape[0], dtype=int), 2)))
        indices_indices = np.arange(0, indices.shape[0], dtype=int)
        # Create a random number generator.
        if random_seed is None:
            rng = np.random.RandomState()
        else:
            rng = np.random.RandomState(random_seed)
        # Get random positions.
        rng.shuffle(indices_indices)
        object_rotations = rng.uniform(-90, 90, num_objects)
        # Get random colors.
        color_arrs = rng.uniform(0, 1, num_objects * 3).reshape(num_objects, 3)
        colors = []
        for color in color_arrs:
            colors.append({"r": float(color[0]), "g": float(color[1]), "b": float(color[2]), "a": 1})
        # Get the scale of the cubes.
        object_scale_factor = {"x": self.object_scale, "y": self.object_scale, "z": self.object_scale}
        # Add the objects.
        for i in range(num_objects):
            object_id = Controller.get_unique_id()
            # Get the indices of the next position.
            ix, iz = indices[indices_indices[i]]
            # Get the position.
            position = {"x": float(xs[ix]), "y": 0, "z": float(zs[iz])}
            # Get the rotation.
            rotation = float(object_rotations[i])
            # Add the object.
            commands.extend(Controller.get_add_physics_object(model_name="cube",
                                                              object_id=object_id,
                                                              library="models_flex.json",
                                                              position=position,
                                                              rotation={"x": 0, "y": rotation, "z": 0},
                                                              default_physics_values=False,
                                                              mass=1,
                                                              scale_factor=object_scale_factor,
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
        # Set a position for the stack.
        ix, iz = indices[indices_indices[num_objects]]
        self.stack_position = {"x": float(xs[ix]), "y": 0, "z": float(zs[iz])}
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
                # Reach for the cube.
                self.replicant_state = ReplicantState.reaching_for_cube
                self.communicate([])
                self.replicant.reach_for(target=self.cubes[self.cube_index], arm=Arm.right)
        # Reach for the next cube.
        elif self.replicant_state == ReplicantState.reaching_for_cube:
            if self.action_ended(error_message=f"reach for {self.cubes[self.cube_index]}"):
                # Start to grasp the cube.
                self.replicant_state = ReplicantState.grasping_cube
                self.communicate([])
                self.replicant.grasp(target=self.cubes[self.cube_index],
                                     arm=Arm.right,
                                     angle=0,
                                     axis="pitch",
                                     relative_to_hand=False)
        # Grasp the next cube.
        elif self.replicant_state == ReplicantState.grasping_cube:
            if self.action_ended(error_message=f"grasp {self.cubes[self.cube_index]}"):
                # Start to reset the arm holding the cube.
                self.replicant_state = ReplicantState.resetting_arm_with_cube
                self.communicate([])
                # Reach for a relative position.
                self.replicant.reach_for(target=self.hold_object_positions[Arm.right], arm=Arm.right, absolute=False)
        elif self.replicant_state == ReplicantState.resetting_arm_with_cube:
            if self.action_ended(error_message="reset arm holding cube"):
                # Start to move to the stack.
                self.replicant_state = ReplicantState.moving_to_stack
                self.communicate([])
                self.replicant.move_to(target=self.stack_position, arrived_at=0.8, reset_arms=False)
        # Navigate to the stack.
        elif self.replicant_state == ReplicantState.moving_to_stack:
            if self.action_ended(error_message="move to stack"):
                self.communicate([])
                # Get the target position above the stack.
                target_position = {k: v for k, v in self.stack_position.items()}
                target_position["y"] = self.object_scale * (self.cube_index + 1)
                # Reach for the point above the stack. Offset the target by the held object. Use an IK plan.
                self.replicant.reach_for(target=target_position,
                                         arm=Arm.right,
                                         from_held=True,
                                         held_point="top",
                                         plan=IkPlanType.vertical_horizontal,
                                         arrived_at=0.02)
                # Set the state.
                self.replicant_state = ReplicantState.reaching_above_stack
        # Reach above the stack.
        elif self.replicant_state == ReplicantState.reaching_above_stack:
            if self.action_ended(error_message="reach above stack"):
                # Start to drop the cube.
                self.replicant_state = ReplicantState.dropping_cube
                # Drop the object. Set the `offset_distance` to 0 so that the object falls directly down.
                self.replicant.drop(arm=Arm.right,
                                    offset_distance=0)
        # Drop the cube.
        elif self.replicant_state == ReplicantState.dropping_cube:
            if self.action_ended(error_message=f"drop {self.cubes[self.cube_index]}"):
                # Start to move away.
                self.replicant_state = ReplicantState.backing_away
                self.communicate([])
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
                    self.communicate([{"$type": "add_position_marker",
                                       "color": {"r": 0, "g": 1, "b": 0, "a": 1},
                                       "position": self.stack_position},
                                      {"$type": "pause_editor"}])
        return False

    def start_moving_to_cube(self) -> None:
        """
        Start moving the Replicant to the next cube.
        """

        cube_position = TDWUtils.array_to_vector3(self.object_manager.transforms[self.cubes[self.cube_index]].position)
        cube_position["y"] = 0
        self.replicant.move_to(target=self.cubes[self.cube_index], arrived_at=0.25)

    def raycast_stack(self) -> float:
        """
        Raycast the top of the stack of cubes.

        :return: The height of the stack.
        """

        raycast_id = 0
        # End the action. Raycast the top of the stack.
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
                    # There is something here on the stack. Raise the target to be above the stack.
                    if raycast.get_hit_object():
                        return float(raycast.get_point()[1])
        return 0

    def action_ended(self, error_message: str) -> bool:
        """
        Check if the Replicant's action ended. Print a warning if there was a problem.

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
