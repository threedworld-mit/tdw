from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.output_data_writer import OutputDataWriter
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Write raw output data per frame from the build.
"""

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("output_data_writer")
print(f"Output will be saved to: {output_directory}")
c = Controller()
writer = OutputDataWriter(output_directory=output_directory)
c.add_ons.append(writer)
c.communicate([TDWUtils.create_empty_room(12, 12),
               Controller.get_add_object(model_name="vase_02",
                                         object_id=0),
               {"$type": "send_transforms",
                "frequency": "once"}])
c.communicate({"$type": "terminate"})
# Corresponds to: 00000000.txt
data = writer.read(0)
print(data)
