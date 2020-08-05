from tdw.controller import Controller


"""
A minimal example of how to connect to the build and receive data.
"""

if __name__ == "__main__":
    c = Controller()
    print("Everything is OK!")
    c.communicate({"$type": "terminate"})
