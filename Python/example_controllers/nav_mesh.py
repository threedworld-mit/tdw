from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import ArrivedAtNavMeshDestination, OutputData
from proc_gen_room import create_office


"""
- Create a NavMeshAvatar and a simple procedurally-generated room. 
- Tell the avatar to navigate to different destinations.
"""


class NavMesh(Controller):
    DESTINATIONS = [{"x": 5, "y": 0, "z": 3}, {"x": 1, "y": 0, "z": 8}, {"x": 1, "y": 0, "z": 3}]

    def run(self):
        self.start()
        # Create an office.
        self.communicate(create_office(12, 24, 4, 4, 6))

        # Get a random position on the NavMesh.
        x, y, z = TDWUtils.get_random_position_on_nav_mesh(self, 12, 24)

        # Index of the next destination.
        d = 0

        # Create the avatar.
        self.communicate(TDWUtils.create_avatar(avatar_type="A_Nav_Mesh",
                                                position={"x": x, "y": 0.5, "z": 0}))
        # Teleport the avatar.
        # Set the speed of the avatar.
        # Set the destination of the avatar.
        self.communicate([{"$type": "set_nav_mesh_avatar",
                           "avatar_id": "a",
                           "speed": 2},
                          {"$type": "set_nav_mesh_avatar_destination",
                           "avatar_id": "a",
                           "destination": NavMesh.DESTINATIONS[d]}
                          ])

        # Go to 3 destinations.
        i = 0
        while i < 3:
            resp = self.communicate({"$type": "do_nothing"})

            # If there is only 1 element in the response, it is an empty frame.
            if len(resp) == 1:
                continue
            # The avatar arrived at the destination!
            else:
                assert OutputData.get_data_type_id(resp[0]) == "anmd"

                # Parse the output data.
                data = ArrivedAtNavMeshDestination(resp[0])
                print(data.get_avatar_id())
                print("")

                i += 1
                d += 1
                if d >= len(NavMesh.DESTINATIONS):
                    d = 0
                # Set a new destination.
                self.communicate({"$type": "set_nav_mesh_avatar_destination",
                                  "avatar_id": "a",
                                  "destination": NavMesh.DESTINATIONS[d]})


if __name__ == "__main__":
    NavMesh().run()
