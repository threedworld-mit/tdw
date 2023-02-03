from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union
from json import loads
from argparse import ArgumentParser
from csv import DictReader
from tdw.tdw_utils import TDWUtils
from tdw.asset_bundle_creator.model_creator import ModelCreator


class _ShapeNet(ABC):
    """
    Abstract base class for generating ShapeNet asset bundles.
    """

    def __init__(self, source_directory: Union[str, Path], output_directory: Union[str, Path]):
        """
        :param source_directory: The source path or directory.
        :param output_directory: The root destination directory for the library file and asset bundles.
        """

        self.source_directory: Path = TDWUtils.get_path(source_directory)
        self.output_directory: Path = TDWUtils.get_path(output_directory)
        if not self.output_directory.exists():
            self.output_directory.mkdir(parents=True)
        self.metadata_path: Path = self.output_directory.joinpath("metadata.csv")

    def run(self, vhacd_resolution: int = 800000) -> None:
        """
        Create asset bundles from a ShapeNet set.

        :param vhacd_resolution: The VHACD voxel resolution.
        """

        # Create a metadata file.
        if not self.metadata_path.exists():
            self.metadata_path.write_text("name,wnid,wcategory,scale_factor,path\n" + self.get_csv().strip())
            print("Generated metadata.csv")
        ModelCreator().metadata_file_to_asset_bundles(metadata_path=self.metadata_path,
                                                      output_directory=self.output_directory,
                                                      vhacd_resolution=vhacd_resolution,
                                                      library_description=self.get_library_description())

    @abstractmethod
    def get_csv(self) -> str:
        """
        :return: A string of .csv metadata.
        """
        raise Exception()

    @abstractmethod
    def get_library_description(self) -> str:
        """
        :return: A description that will be included in `library.json`.
        """

        raise Exception()


class ShapeNetCore(_ShapeNet):
    """
    Generate asset bundles from ShapeNetCore.
    """

    def get_csv(self) -> str:
        # Get the taxonomy file.
        taxonomy = loads(self.source_directory.joinpath("taxonomy.json").read_text())
        # Get wnid and category data.
        wnids = {w["synsetId"]: w["name"].split(",")[0] for w in taxonomy}
        # Get cached ImageNet data.
        csv = ""
        print("Generating metadata.csv (this may take a few minutes)...")
        for d in self.source_directory.iterdir():
            # This is a directory.
            if d.is_dir():
                # Get the WordNet ID and category from the overall taxonomy.
                wnid = d.name
                wcategory = wnids[wnid]
                for model_directory in d.iterdir():
                    if model_directory.is_dir():
                        name = model_directory.name
                        f = model_directory.joinpath("models").joinpath("model_normalized.obj")
                        # Sometimes there is an irregular path.
                        if f.exists():
                            path = str(f.resolve()).replace("\\", "/")
                            csv += f"{name},{wnid},{wcategory},1,{path}\n"
        return csv

    def get_library_description(self) -> str:
        return "ShapeNetCore"


class ShapeNetSEM(_ShapeNet):
    """
    Generate asset bundles from ShapeNetSEM.
    """

    def get_csv(self) -> str:
        csv = ""
        source_metadata_path = self.source_directory.joinpath("metadata.csv")
        assert source_metadata_path.exists(), f"File not found: {source_metadata_path.resolve()}\n" \
                                              f"Download metadata.csv from the ShapeNet website."
        with open(str(source_metadata_path.resolve()), newline='') as csvfile:
            reader = DictReader(csvfile)
            for row in reader:
                # The name always starts with "wss."
                name = row["fullId"][4:]
                wnid = row["wnsynset"]
                # The category is a list split by commas.
                wcategory = row["wnlemmas"]
                if "," in wcategory:
                    wcategory = wcategory.split(",")[0]
                path = str(self.source_directory.joinpath("models").joinpath(name + ".obj").resolve()).replace("\\", "/")
                csv += f"{name},{wnid},{wcategory},1,{path}\n"
        return csv

    def get_library_description(self) -> str:
        return "ShapeNetSEM"


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--source_directory", type=str, default="D:/ShapeNetCore.v2",
                        help="The absolute path to the root source directory.")
    parser.add_argument("--output_directory", type=str, default="D:/tdw_shapenet_core",
                        help="The absolute path to the root destination directory.")
    parser.add_argument("--set", type=str, default="core", choices=["core", "sem"],
                        help="Which ShapeNet set this is.")
    parser.add_argument("--vhacd_resolution", type=int, default=800000,
                        help="Higher value=better-fitting colliders and slower build process.")
    args = parser.parse_args()
    if args.set == "core":
        shapenet = ShapeNetCore(args.source_directory, args.output_directory)
    else:
        shapenet = ShapeNetSEM(args.source_directory, args.output_directory)
    shapenet.run(vhacd_resolution=args.vhacd_resolution)
