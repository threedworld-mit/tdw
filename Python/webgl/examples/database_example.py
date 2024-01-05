from threading import Thread
from tdw.tdw_utils import TDWUtils
from tdw.webgl import TrialController, TrialMessage, END_MESSAGE, Database, TrialPlayback, run
from tdw.webgl.trials.hello_world import HelloWorld
from tdw.webgl.trial_adders import AtEnd

"""
This is a minimal example of how to connect a TrialController to a Database.
For the sake of simplicity, this script runs a Database in a thread.
In an actual TDW simulation, you should always run the Database as a separate process.
"""


class MyTrialController(TrialController):
    def get_initial_message(self) -> TrialMessage:
        return TrialMessage(trials=[HelloWorld()], adder=AtEnd())

    def get_next_message(self, playback: TrialPlayback) -> TrialMessage:
        return END_MESSAGE


class MyDatabase(Database):
    """
    A subclass of the minimal Database parent class that prints some messages about trial data and then closes the connection.
    """

    def __init__(self, port: int):
        super().__init__(port=port)
        self.done = False

    def on_receive_data(self, session_id: int, data: bytes) -> None:
        print("Session ID:", session_id)
        print(f"Trial data size: {TDWUtils.bytes_to_megabytes(len(data))} MB")
        self.done = True

    def is_done(self) -> bool:
        return self.done


def run_database(port: int) -> None:
    database = MyDatabase(port=port)
    database.run()


if __name__ == "__main__":
    # Start the Database on a thread. In an actual simulation, you should always run it as a separate process.
    database_port = 1338
    t = Thread(target=run_database, args=[database_port])
    t.start()

    controller = MyTrialController()

    # Connect to the Database.
    # Alternatively, you could run the controller in a separate script, e.g. my_trial_controller.py
    # You can then pass the database address as a command line argument:
    # `python3 my_trial_controller.py --database_address 127.0.0.1:1338`
    controller.connect_database_socket(f'127.0.0.1:{database_port}')

    # Run the controller.
    run(controller)
