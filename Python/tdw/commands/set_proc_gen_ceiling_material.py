# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.proc_gen_material_command import ProcGenMaterialCommand


class SetProcGenCeilingMaterial(ProcGenMaterialCommand):
    """
    Set the material of a procedurally-generated ceiling.
    """

    def __init__(self, name: str):
        """
        :param name: The name of the material. The material must already be loaded in memory.
        """

        super().__init__(name=name)

