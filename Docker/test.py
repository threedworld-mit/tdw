from tdw.controller import Controller

c = Controller(launch_build=False, port=1071)
print("Hello world!")
c.communicate({"$type": "terminate"})
