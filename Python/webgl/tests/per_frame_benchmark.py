from typing import List, Union
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.commands.command import Command
from tdw.commands import ApplyForceToObject, SendRigidbodies
from tdw.output_data import OutputData, Rigidbodies
from tdw.webgl import run
from output_data_benchmark import OutputDataBenchmark


class PerFrameBenchmark(OutputDataBenchmark):
    """
    Output data benchmark with commands being sent per-frame.
    """

    def __init__(self, path: str):
        self.sent_rigidbodies: bool = False
        super().__init__(path=path)

    @classmethod
    def _send_per_frame(cls) -> bool:
        return True

    def on_receive_frame(self, resp: List[bytes]) -> List[Union[Command, dict]]:
        if not self.sent_rigidbodies:
            self.sent_rigidbodies = True
            return [SendRigidbodies(ids=[], frequency="always")]
        else:
            commands = []
            # Get Rigidbody data.
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "rigi":
                    rigidbodies = Rigidbodies(resp[i])
                    for j in range(rigidbodies.get_num()):
                        # If the object is sleeping, apply a force.
                        if rigidbodies.get_sleeping(j):
                            force = TDWUtils.array_to_vector3(np.random.uniform(-0.8, 0.8, 3))
                            commands.append(ApplyForceToObject(id=rigidbodies.get_id(j), force=force))
                    break
            return commands


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(allow_abbrev=False)
    parser.add_argument("--path", type=str, default="D:/tdw_docs/docs/webgl/tests/per_frame.csv")
    args, unknown = parser.parse_known_args()
    run(PerFrameBenchmark(path=args.path))
