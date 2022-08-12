from tdw.add_ons.logger import Logger
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
logger = Logger(record=True, path="log.json")
c.add_ons.append(logger)
c.communicate([])
c.communicate(TDWUtils.create_empty_room(12, 12))
logger.save()
with open("log.json", "rt") as f:
    print(f.read())
c.communicate({"$type": "terminate"})