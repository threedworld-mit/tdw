from tdw.add_ons.container_manager import ContainerManager
from tdw.add_ons.empty_object_manager import EmptyObjectManager
from tdw.add_ons.object_manager import ObjectManager


# A container manager shared between multiple replicants.
CONTAINER_MANAGER: ContainerManager = ContainerManager()
# An empty object manager shared between multiple replicants.
EMPTY_OBJECT_MANAGER: EmptyObjectManager = EmptyObjectManager()
# An object manager shared between multiple replicants.
OBJECT_MANAGER: ObjectManager = ObjectManager(transforms=True, rigidbodies=False, bounds=True)
