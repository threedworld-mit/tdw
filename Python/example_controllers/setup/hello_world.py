from tdw.controller import Controller


"""
A minimal example of how to connect to the build and receive data.
"""

if __name__ == "__main__":
    # If you're running the TDW build on a remote server, replace this with c = Controller(launch_build=False)
    c = Controller()
    print("Hello world!")
    c.communicate({"$type": "terminate"})
