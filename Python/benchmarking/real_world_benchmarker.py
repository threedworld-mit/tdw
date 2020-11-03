from __future__ import division
import numpy as np
import math
import random
from platform import system
import time as tm
from argparse import ArgumentParser
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from benchmark_utils import PATH


class screen(object):
    def __init__(self):
        self.latent_data = None
        self.trial_len = 0


class RealWorldController(Controller):
    def __init__(self,
                 avatar_type="A_Img_Caps",
                 good_obj_name="bastone_floor_lamp",
                 bad_obj_name="arturoalvarez_v_floor_lamp",
                 num_good_obj=5,
                 num_bad_obj=5,
                 room_dim=5,
                 port=1071):

        self.good_obj_name = good_obj_name
        self.bad_obj_name = bad_obj_name
        self.num_good_objects = num_good_obj
        self.num_bad_objects = num_bad_obj
        self.room_dim = room_dim

        self.avatar_type = avatar_type

        self.comm_times = []

        # Start the controller.
        super().__init__(port, launch_build=False)

    def next(self):
        """
        Starts a new trial of an experiment. Populates a room with randomly placed lamps and a single avatar.
        """

        # Get a random avatar position.
        ret_dict = {}
        avatar_position = [random.uniform(-self.room_dim * 0.33, self.room_dim * 0.33), 0,
                           random.uniform(-self.room_dim * 0.33, self.room_dim * 0.33)]
        config_actions = []

        # Begin placing objects in the room.
        current_objects = []
        for good_obj in range(self.num_good_objects):
            current_objects.append(
                self.get_object_dict(self.find_open_position(current_objects, avatar_position), self.good_obj_name))

        for bad_obj in range(self.num_bad_objects):
            current_objects.append(
                self.get_object_dict(self.find_open_position(current_objects, avatar_position), self.bad_obj_name))

        # Add the TDW configurations to a list to be sent inside TDWGenerator.restart_trial()
        # Initialize the scene.
        # Set the render quality to as low as possible.
        # Tell the build to return transform, rigidbody, and image data.
        config_actions.append([{'$type': "load_scene", 'scene_name': "ProcGenScene"}])
        config_actions.append([{"$type": "send_transforms", "frequency": "always"},
                               {"$type": "send_collisions", "frequency": "always"},
                               {"$type": "send_rigidbodies", "frequency": "always"},
                               {"$type": "send_images", "frequency": "always"},
                               {"$type": "set_render_quality", "render_quality": 0},
                               {"$type": "set_screen_size", "width": 256, "height": 256},
                               {"$type": "set_img_pass_encoding", "value": False},
                               {"$type": "set_post_process", "value": False},
                               TDWUtils.create_empty_room(self.room_dim, self.room_dim)])

        for c_o in current_objects:
            config_actions.append(self.get_add_object(model_name=c_o["name"],
                                                      object_id=self.get_unique_id(),
                                                      position=c_o["position"],
                                                      rotation=c_o["orientation"]))

        config_actions.append([{"$type": "create_avatar", "type": self.avatar_type, "id": "a",
                                "position": avatar_position, "rotation": [0.0, 0.0, 0.0]},
                               {"$type": "teleport_avatar_to",
                                "position": {"x": avatar_position[0], "y": 1.0, "z": avatar_position[2]}}
                               ])

        config_actions.append([{"$type": "set_pass_masks", "pass_masks": ["_img"]}])
        config_actions.append([{"$type": "send_id_pass_segmentation_colors", "frequency": "always"}])
        config_actions.append([{"$type": "set_avatar_drag", "drag": 80, "angular_drag": 4}])

        # Set up the environment and start up the trial
        ret_dict['latents'] = self.restart_trial(config_actions)
        return ret_dict

    def get_object_dict(self, position, object_name):
        """
        Helper function to build an object dictionary to return to TDW.
        """

        return {"name": object_name,

                "position": {"x": float(position[0]),
                             "y": float(position[1]),
                             "z": float(position[2])},
                "orientation": {"x": 0.0, "y": 0.0, "z": 0.0},

                'id': np.random.randint(20, 2147483645)}

    def continue_trial(self, current_screen, current_sequence):
        """ Wrapper function for TDWGenerator.step() """

        current_screen.latent_data = self.step(current_sequence)
        return current_screen

    def find_open_position(self, current_objects, current_avatar_position):
        """
        Given the current objects inside the environment, returns an open position to place a new object.
        """

        return_position = None
        adaptive_thresh = 1
        i = 0
        while return_position is None:
            return_position = [random.uniform(-self.room_dim * 0.33, self.room_dim * 0.33), 0,
                               random.uniform(-self.room_dim * 0.33, self.room_dim * 0.33)]

            for obj in current_objects:
                if self.flat_distance(self.get_position(obj), return_position) <= adaptive_thresh:
                    return_position = None
                    break
            if (return_position is not None and current_avatar_position is not None and self.flat_distance(
                    return_position, current_avatar_position) <= 1):
                return_position = None
            i += 1
            if i > 0 and i % 200 == 0:
                adaptive_thresh /= 2

        return return_position

    def get_position(self, obj):
        """
        Helper function to return position from an object dictionary.
        """

        if 'center' in obj.keys():
            key = 'center'
        elif 'position' in obj.keys():
            key = 'position'
        return [obj[key]['x'], obj[key]['y'], obj[key]['z']]

    def flat_distance(self, point1, point2):
        if isinstance(point1, dict) and isinstance(point2, dict):
            x_sq = (float(point1['x']) - float(point2['x'])) ** 2
            z_sq = (float(point1['z']) - float(point2['z'])) ** 2
            return math.sqrt(x_sq + z_sq)

        elif isinstance(point1, (np.ndarray, list)) and isinstance(point2, (np.ndarray, list)):
            x_sq = (float(point1[0]) - float(point2[0])) ** 2
            z_sq = (float(point1[2]) - float(point2[2])) ** 2
            return math.sqrt(x_sq + z_sq)

    def restart_trial(self, config_actions):
        """
        Sends configuration commands to the build to begin a trial.
        Returns a dictionary containing build-level information about avatar, objects, images.
        """

        resps = []
        for c in config_actions:
            resps.append(self.communicate(c))
        return resps[-1]

    def step(self, action_batch):
        """
        Perform a step in the environment, taking an action and returning the response data from TDW.
        """

        # Send action batch.
        t0 = tm.time()
        resp = self.communicate(action_batch['tdw_action'])
        self.comm_times.append(tm.time() - t0)
        return resp


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--main', action='store_true')
    parser.add_argument('--machine', type=str, default='legion_lenovo', choices=['legion_lenovo', 'braintree', 'node11'])
    args = parser.parse_args()

    num_trials = 4
    trial_len = 1000
    generator = RealWorldController()

    # Actions available to the avatar
    nonmasked_actions = ['forward_velocity', 'angular_velocity']
    num_physics_steps = 5

    elapseds = []
    benchmarks = []
    for trial_itt in range(num_trials):
        print('trial: ', trial_itt)
        # This has information like images, avatar data, object data, collision data.
        trial_begin_dict = generator.next()
        encapsulated_data = screen()
        screen.latent_data = trial_begin_dict['latents']
        t0 = tm.time()
        for trial_frame in range(trial_len):
            # Generate a random action from between -1,1 for each action.
            random_action = np.random.uniform(-200, 200, len(nonmasked_actions))
            sendable_action = []
            # Actual TDW actions.
            for p_idx in range(num_physics_steps):
                sendable_action.append(
                    {"$type": "move_avatar_forward_by", "magnitude": random_action[0]})
                sendable_action.append(
                    {"$type": "rotate_avatar_by", "angle": random_action[1] * 8, "axis": "yaw"})
                sendable_action.append({"$type": "step_physics", "frames": 1})

            sendable_action = {'tdw_action': sendable_action}

            screen = generator.continue_trial(screen, sendable_action)

        t1 = tm.time()
        elapsed = t1 - t0
        elapseds.append(elapsed)
        if len(elapseds) > 1:
            total_elapsed = np.sum(elapseds[1:])
            mean_elapsed = np.mean(elapseds[1:])
            frame_rate_overall = trial_len / mean_elapsed
            comms_time = sum(generator.comm_times)
            frac_comms_time = comms_time / total_elapsed
            implied_build_rate = (len(elapseds) - 1) * trial_len / comms_time
            benchmarks.append(frame_rate_overall)
        else:
            del generator.comm_times[:]

    fps = str(round(sum(benchmarks) / len(benchmarks)))[:-2]
    if args.main:
        txt = PATH.read_text()
        machine_key = args.machine.upper()
        if machine_key == "LEGION_LENOVO":
            if system() == "Windows":
                machine_key += "_WINDOWS"
            else:
                machine_key += "_UBUNTU"
        txt = txt.replace("$REAL_WORLD_" + machine_key, fps)
        PATH.write_text(txt)
        generator.communicate({"$type": "terminate"})
    print(f"FPS: " + fps)
