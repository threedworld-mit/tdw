##### Objects and Scenes

# Object positions

So far, we've seen examples of how to set the position of an object when it is first created:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
c.start()
object_id = c.get_unique_id()
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="iron_box",
                                position={"x": 1, "y": 0, "z": -0.5},
                                object_id=object_id)])
c.communicate({"$type": "terminate"})
```

