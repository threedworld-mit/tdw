from typing import List
from time import sleep
from tdw.webgl.webgl_controller import WebGLController, run


class HelloWorld(WebGLController):
    """
    A minimal example of a WebGL controller.
    """

    def on_communicate(self, resp: List[bytes]) -> List[dict]:
        print("Hello world!")

        # You don't need to include this in your controller.
        # It is only here to slow down the rate at which "Hello world!" gets printed.
        sleep(1)

        return []


if __name__ == "__main__":
    # These are the default values of `port` and `check_version`.
    # This statement is equivalent to: `c = HelloWorld()`.
    c = HelloWorld(port=1071, check_version=True)

    # Run the controller until the process is killed.
    run(c)
