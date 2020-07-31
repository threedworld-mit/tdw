from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
import docker
import time
import os
import subprocess
from tdw.version import __version__

"""
Using NVIDIA Flex in a docker container, drape a cloth over an object.
"""


class DockerController(Controller):
    def __init__(self):
        client = docker.from_env()

        client.images.build(path=".", tag=f"tdw:v{__version__}",
                            build_args={"TDW_VERSION": __version__})

        # This method is preferred to subprocess, but the gpu flag is currently
        # not supported by docker-py (see PR: #2419 in the docker-py repo)
        # client.containers.run("tdw:v1.6.0",
        #                       network="host",
        #                       environment=["DISPLAY=$DISPLAY"],
        #                       gpus="all")

        subprocess.Popen(["docker", "run",
                          "--rm",
                          "--gpus", "all",
                          "-v", "/tmp/.X11-unix:/tmp/.X11-unix",
                          "-e", "DISPLAY={}".format(os.environ["DISPLAY"]),
                          "--network", "host",
                          "-t", f"tdw:{__version__}",
                          "./TDW/TDW.x86_64"],
                         shell=False)

        super().__init__()

    def run(self):
        # Load procedurally generated room
        self.start()
        self.communicate(TDWUtils.create_empty_room(12, 12))

        # Create the Flex container.
        self.communicate({"$type": "create_flex_container",
                          "collision_distance": 0.001,
                          "static_friction": 1.0,
                          "dynamic_friction": 1.0,
                          "iteration_count": 3,
                          "substep_count": 8,
                          "radius": 0.1875,
                          "damping": 0,
                          "drag": 0})

        # Create the avatar.
        # Teleport the avatar.
        # Look at the target position.
        self.communicate(TDWUtils.create_avatar(position={"x": 2.0, "y": 1, "z": 1},
                                                look_at={"x": -1.2, "y": 0.5, "z": 0}))

        # Create the solid object.
        solid_id = self.add_object("rh10",
                                   position={"x": -1.2, "y": 0, "z": 0},
                                   rotation={"x": 0.0, "y": -90.0, "z": 0.0})
        # Make the object kinematic.
        self.communicate({"$type": "set_kinematic_state",
                          "id": solid_id})
        # Assign the object a FlexActor.
        # Assign the object a Flex container.
        self.communicate([{"$type": "set_flex_solid_actor",
                           "id": solid_id,
                           "mass_scale": 100.0,
                           "particle_spacing": 0.035},
                          {"$type": "assign_flex_container",
                           "id": solid_id,
                           "container_id": 0}])
        # Set the Flex scale.
        self.communicate({"$type": "set_flex_object_scale",
                          "id": solid_id,
                          "scale": {"x": 1, "y": 1, "z": 1}})

        # Create the cloth.
        cloth_id = self.add_object("cloth_square",
                                   position={"x": -1.2, "y": 1.0, "z": 0},
                                   library="models_special.json")
        # Make the cloth kinematic.
        self.communicate({"$type": "set_kinematic_state",
                          "id": cloth_id})
        # Assign the cloth a FlexActor.
        # Assign the cloth a Flex container.
        self.communicate([{"$type": "set_flex_cloth_actor",
                           "id": cloth_id,
                           "mass_scale": 1,
                           "mesh_tesselation": 1,
                           "tether_stiffness": 0.5,
                           "bend_stiffness": 1.0,
                           "self_collide": False,
                           "stretch_stiffness": 1.0},
                          {"$type": "assign_flex_container",
                           "id": cloth_id,
                           "container_id": 0}
                          ])
        # Set the Flex scale.
        self.communicate({"$type": "set_flex_object_scale",
                          "id": cloth_id,
                          "scale": {"x": 1, "y": 1, "z": 1}})

        # Iterate for 500 frames.
        for i in range(500):
            self.communicate({"$type": "step_physics", "frames": 0})


if __name__ == "__main__":
    DockerController().run()
