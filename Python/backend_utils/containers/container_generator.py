from typing import Dict, List
import json
from pathlib import Path
from tdw.controller import Controller
from tdw.container_data.container_shape import ContainerShape
from tdw.dev.containers.container_cacher import ContainerCacher


class ContainerGenerator(ContainerCacher):
    """
    Generate containers from a manifest json file.
    """

    MANIFEST_DATA: dict = json.loads(Path("manifest.json").read_text())
    COLLIDER_DATA: Dict[str, List[str]] = MANIFEST_DATA["colliders"]

    def box_cavities(self) -> None:
        if "box_cavity" not in ContainerGenerator.COLLIDER_DATA:
            return
        for model_name in ContainerGenerator.COLLIDER_DATA["box_cavity"]:
            self._add(model_name=model_name, container_shape=self.box_cavity(model_name=model_name))

    def interior_box_cavities(self) -> None:
        if "interior_box_cavity" not in ContainerGenerator.COLLIDER_DATA:
            return
        for model_name in ContainerGenerator.COLLIDER_DATA["interior_box_cavity"]:
            self._add(model_name=model_name, container_shape=self.interior_box_cavity(model_name=model_name))

    def cylinder_cavities(self) -> None:
        if "cylinder_cavity" not in ContainerGenerator.COLLIDER_DATA:
            return
        for model_name in ContainerGenerator.COLLIDER_DATA["cylinder_cavity"]:
            self._add(model_name=model_name, container_shape=self.cylinder_cavity(model_name=model_name))

    def interior_cylinder_cavities(self) -> None:
        if "interior_cylinder_cavity" not in ContainerGenerator.COLLIDER_DATA:
            return
        for model_name in ContainerGenerator.COLLIDER_DATA["interior_cylinder_cavity"]:
            self._add(model_name=model_name, container_shape=self.interior_cylinder_cavity(model_name=model_name))

    def enclosed_cylinder_cavities(self) -> None:
        if "enclosed_cylinder_cavity" not in ContainerGenerator.COLLIDER_DATA:
            return
        for model_name in ContainerGenerator.COLLIDER_DATA["enclosed_cylinder_cavity"]:
            self._add(model_name=model_name, container_shape=self.enclosed_cylinder_cavity(model_name=model_name))

    def interior_sphere_cavities(self) -> None:
        if "interior_sphere_cavity" not in ContainerGenerator.COLLIDER_DATA:
            return
        for model_name in ContainerGenerator.COLLIDER_DATA["interior_sphere_cavity"]:
            y = ContainerGenerator.MANIFEST_DATA["interior_sphere_cavity_y_factors"][model_name]
            self._add(model_name=model_name, container_shape=self.interior_sphere_cavity(model_name=model_name, y_factor=y))

    def rectangular_surfaces(self) -> None:
        if "rectangular_surface" not in ContainerGenerator.COLLIDER_DATA:
            return
        for model_name in ContainerGenerator.COLLIDER_DATA["rectangular_surface"]:
            self._add(model_name=model_name, container_shape=self.rectangular_surface(model_name=model_name))

    def circular_surfaces(self) -> None:
        if "circular_surface" not in ContainerGenerator.COLLIDER_DATA:
            return
        for model_name in ContainerGenerator.COLLIDER_DATA["circular_surface"]:
            self._add(model_name=model_name, container_shape=self.circular_surface(model_name=model_name))

    def shelf_surfaces(self) -> None:
        if "shelf" not in ContainerGenerator.COLLIDER_DATA:
            return
        for model_name in ContainerGenerator.COLLIDER_DATA["shelf"]:
            for container_shape in self.shelves(model_name=model_name,
                                                ys=ContainerGenerator.MANIFEST_DATA["shelf_ys"][model_name]):
                self._add(model_name=model_name, container_shape=container_shape)

    def sinks(self) -> None:
        if "sink" not in ContainerGenerator.COLLIDER_DATA:
            return
        for model_name in ContainerGenerator.COLLIDER_DATA["sink"]:
            for container_shape in self.sink(model_name=model_name):
                self._add(model_name=model_name, container_shape=container_shape)

    def interior_cavities_with_divider(self) -> None:
        if "interior_cavity_with_divider" not in ContainerGenerator.MANIFEST_DATA:
            return
        for model_name in ContainerGenerator.MANIFEST_DATA["interior_cavity_with_divider"]:
            for container_shape in self.interior_cavity_with_divider(model_name=model_name,
                                                                     cavity_positions=ContainerGenerator.MANIFEST_DATA["interior_cavity_with_divider"][model_name]):
                self._add(model_name=model_name, container_shape=container_shape)

    def write(self) -> None:
        for lib in Controller.MODEL_LIBRARIANS.values():
            lib.write()
        Path("log.txt").write_text("\n".join(self.log))

    def run(self) -> None:
        self.shelf_surfaces()
        self.rectangular_surfaces()
        self.circular_surfaces()
        self.box_cavities()
        self.interior_box_cavities()
        self.cylinder_cavities()
        self.interior_cylinder_cavities()
        self.enclosed_cylinder_cavities()
        self.interior_sphere_cavities()
        self.sinks()
        self.interior_cavities_with_divider()
        self.write()
        self.communicate({"$type": "terminate"})

    def _add(self, model_name: str, container_shape: ContainerShape) -> None:
        if container_shape is None:
            return
        self.update_record(model_name=model_name, containers=[container_shape], write=True)


if __name__ == "__main__":
    c = ContainerGenerator()
    c.run()
