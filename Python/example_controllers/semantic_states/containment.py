from PIL import Image, ImageDraw, ImageFont
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.container_manager import ContainerManager
from tdw.add_ons.object_manager import ObjectManager
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.container_data.container_tag import ContainerTag
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class Containment(Controller):
    """
    Add objects to the scene and listen for containment events.
    Save the image of each frame.
    At the end of a trial, create a timeline diagram of the containment states.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.container_manager: ContainerManager = ContainerManager()
        self.object_manager: ObjectManager = ObjectManager(transforms=False, rigidbodies=True, bounds=False)
        self.camera = ThirdPersonCamera(position={"x": 3, "y": 2.5, "z": -1},
                                        look_at={"x": 0, "y": 0, "z": 0},
                                        avatar_id="a")
        self.path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("containment")
        print(f"Images will be saved to: {str(self.path.resolve())}")
        self.capture = ImageCapture(path=self.path, avatar_ids=["a"], pass_masks=["_img"])
        self.add_ons.extend([self.object_manager, self.container_manager, self.camera, self.capture])

    def trial(self, container_name: str):
        self.container_manager.reset()
        self.object_manager.reset()
        self.camera.initialized = False
        self.capture.initialized = False
        # Create the room.
        commands = [{'$type': "load_scene",
                     'scene_name': "ProcGenScene"},
                    TDWUtils.create_empty_room(12, 12)]
        # Add the container.
        container_id = Controller.get_unique_id()
        commands.extend(Controller.get_add_physics_object(model_name=container_name,
                                                          object_id=container_id,
                                                          kinematic=True))
        falling_object_id = Controller.get_unique_id()
        # Add the falling object.
        commands.extend(Controller.get_add_physics_object(model_name="jug02",
                                                          object_id=falling_object_id,
                                                          position={"x": 0, "y": 3, "z": 0}))
        self.communicate(commands)
        # Wait for the object to stop moving.
        sleeping = False
        # Record the containment states.
        frames = []
        while not sleeping:
            sleeping = self.object_manager.rigidbodies[falling_object_id].sleeping
            containment = False
            tag = ContainerTag.inside
            for container_shape_id in self.container_manager.events:
                object_id = self.container_manager.container_shapes[container_shape_id]
                if object_id == container_id:
                    event = self.container_manager.events[container_shape_id]
                    if falling_object_id in event.object_ids:
                        containment = True
                        tag = event.tag
                        break
            frames.append((containment, tag))
            self.communicate([])
        # Create a timeline diagram of the containment states.
        image = Image.new(mode="RGB", size=(1024, 256))
        x_0 = 36
        y_0 = 256 // 3
        frame_width = 2
        for frame in frames:
            if not frame[0]:
                color = (255, 255, 255)
            else:
                if frame[1] == ContainerTag.on:
                    color = (255, 0, 0)
                else:
                    color = (0, 0, 255)
            for x in range(x_0, x_0 + frame_width):
                for y in range(y_0, y_0 + 64):
                    image.putpixel((x, y), color)
            x_0 += frame_width
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("Roboto-Regular.ttf", size=36)
        draw.text((800, y_0), "On", (255, 0, 0), font=font)
        draw.text((800, y_0 + 50), "Inside", (0, 0, 255), font=font)
        # Save the image.
        image.save(str(self.path.joinpath(container_name + ".png").resolve()))

    def run(self):
        for container_name in ["quatre_dining_table", "basket_18inx18inx12iin_plastic_lattice"]:
            self.trial(container_name=container_name)
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = Containment()
    c.run()
