from enum import Enum
from platform import system
from typing import List, Union, Optional
from tdw.controller import Controller
from tdw.librarian import ModelLibrarian, ModelRecord
from tdw.add_ons.add_on import AddOn
from tdw.add_ons.model_verifier.model_tests.model_test import ModelTest
from tdw.add_ons.model_verifier.model_tests.model_report import ModelReport
from tdw.add_ons.model_verifier.model_tests.missing_materials import MissingMaterials
from tdw.add_ons.model_verifier.model_tests.physics_quality import PhysicsQuality


class _Test(Enum):
    """
    A type of test.
    """

    model_report = 1
    missing_materials = 2
    physics_quality = 4


class ModelVerifier(AddOn):
    """
    Run tests on an object model.
    """

    def __init__(self):
        super().__init__()
        self._tests: List[_Test] = list()
        self._record: Optional[ModelRecord] = None
        self._current_test: Optional[ModelTest] = None
        self._object_id: int = -1
        """:field
        A list of reports from the test.
        """
        self.reports: List[str] = list()
        """:field
        If True, the tests are done.
        """
        self.done: bool = False

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "create_empty_environment"},
                {"$type": "set_render_quality",
                 "render_quality": 0},
                {"$type": "set_post_process",
                 "value": False},
                {"$type": "simulate_physics",
                 "value": False},
                {"$type": "create_avatar",
                 "id": "a",
                 "type": "A_Img_Caps_Kinematic"},
                {"$type": "teleport_avatar_to",
                 "position": {"x": 1.75, "y": 0.5, "z": 0}},
                {"$type": "look_at_position",
                 "position": {"x": 0, "y": 0.5, "z": 0}}]

    def set_tests(self, name: str, model_report: bool, missing_materials: bool, physics_quality: bool,
                  source: Union[ModelLibrarian, ModelRecord, str] = None) -> None:
        """
        Start new tests for the model. Only call this if there isn't currently a test running.

        :param name: The name of the model.
        :param source: The source of the model. If None: Get the record corresponding to `name` in `models_core.json`. If `ModelLibrarian`: Get the record corresponding to `name` in this library. If `ModelRecord`: Use this record. If `str`: Create a dummy record with name `name` and URL `source`.
        :param model_report: If True, run a basic test on the model.
        :param missing_materials: If True, test the model for any missing materials.
        :param physics_quality: If True, test the extent to which the colliders geometry matches the rendered geometry.
        """

        if self._current_test is not None:
            raise Exception(f"Cannot set new tests because we're still testing {self._record.name}")
        self._tests = list()
        self.done = False
        self.reports.clear()
        if model_report:
            self._tests.append(_Test.model_report)
        if missing_materials:
            self._tests.append(_Test.missing_materials)
        if physics_quality:
            self._tests.append(_Test.physics_quality)
        # This is the name of a model in models_core.json
        if source is None:
            if "models_core.json" not in Controller.MODEL_LIBRARIANS:
                Controller.MODEL_LIBRARIANS["models_core.json"] = ModelLibrarian()
            self._record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(name)
        # This is the name of a record in a specified library.
        elif isinstance(source, ModelLibrarian):
            self._record = source.get_record(name)
        # This is a model record.
        elif isinstance(source, ModelRecord):
            self._record = source
        # This is a URL.
        elif isinstance(source, str):
            self._record = ModelRecord()
            self._record.name = name
            self._record.urls[system()] = source
        else:
            raise TypeError("Invalid type for source: " + source)
        self._next_test()

    def _next_test(self) -> None:
        """
        Start the next test, if any.
        """

        if len(self._tests) == 0:
            self._current_test = None
            self._record = None
            return
        t: _Test = self._tests.pop(0)
        if t == _Test.model_report:
            self._current_test = ModelReport(record=self._record)
        elif t == _Test.physics_quality:
            self._current_test = PhysicsQuality(record=self._record)
        elif t == _Test.missing_materials:
            self._current_test = MissingMaterials(record=self._record)
        else:
            raise Exception(f"Test not defined: {t}")
        self.commands.extend(self._current_test.start())

    def on_send(self, resp: List[bytes]) -> None:
        if self._current_test is None:
            self.done = True
            return
        # Get test commands.
        self.commands.extend(self._current_test.on_send(resp=resp))
        # If this test is done, append the reports and try to start a new test.
        if self._current_test.done:
            self.reports.extend(self._current_test.reports)
            self._next_test()
