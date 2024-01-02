from tdw.webgl import END_MESSAGE, TrialController, TrialMessage, TrialPlayback
from tdw.webgl.trials.hello_world import HelloWorld as HelloWorldTrial
from tdw.webgl.trial_adders import AtEnd


class HelloWorld(TrialController):
    """
    A minimal hello world TrialController.

    1. Send a `HelloWorld` trial. This will show "Hello world!" in the WebGL window and then end.
    2. End the simulation.
    """

    def get_initial_message(self) -> TrialMessage:
        return TrialMessage(trials=[HelloWorldTrial()], adder=AtEnd())

    def get_next_message(self, playback: TrialPlayback) -> TrialMessage:
        return END_MESSAGE


if __name__ == "__main__":
    from tdw.webgl import run
    run(HelloWorld())
