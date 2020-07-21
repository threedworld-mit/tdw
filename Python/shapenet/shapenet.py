from pathlib import Path
import json
from tdw.librarian import ModelLibrarian, ModelRecord
from tdw.asset_bundle_creator import AssetBundleCreator
from typing import Union, List, Optional
from argparse import ArgumentParser
import csv
from tqdm import tqdm


class _ShapeNet:
    def __init__(self, src: Union[str, Path], dest: Union[str, Path]):
        """
        :param src: The source path or directory.
        :param dest: The root destination directory for the library file and asset bundles.
        """

        self.src = src
        if not isinstance(self.src, Path):
            self.src = Path(self.src)
        self.dest = dest
        if not isinstance(self.dest, Path):
            self.dest = Path(self.dest)
        if not self.dest.exists():
            self.dest.mkdir(parents=True)

        print("Directory structure must match: ")
        print(self.src)
        print(self._get_directory_structure())
        directories_ok = self._assess_directory_structure()
        if not directories_ok:
            raise Exception("Invalid directory structure!")
        print("OK!")

        self.library_path = self.dest.joinpath("records.json")

    def run(self, batch_size: int = 1000, vhacd_resolution: int = 8000000, first_batch_only: bool = False) -> None:
        """
        Create a library file if one doesn't exist yet. Then generate asset bundles.

        :param batch_size: The number of models per batch.
        :param vhacd_resolution: Higher value=better-fitting colliders and slower build process.
        :param first_batch_only: If true, output only the first batch. Useful for testing purposes.
        """

        if not self.library_path.exists():
            self.create_library()
        self.create_asset_bundles(batch_size=batch_size, vhacd_resolution=vhacd_resolution,
                                  first_batch_only=first_batch_only)

    def create_library(self) -> ModelLibrarian:
        """
        Create the metadata library. Returns the librarian.
        """

        raise Exception()

    def _get_librarian(self, description: str) -> ModelLibrarian:
        """
        Returns a librarian object.

        :param description: The description of the library.
        """

        ModelLibrarian.create_library(description, self.library_path)
        print("Adding records to the library...")
        return ModelLibrarian(str(self.library_path.resolve()))

    def _get_url(self, wnid: str, name: str, platform: str) -> str:
        """
        Creates a valid destination local URL for an asset bundle.

        :param wnid: The model wnid.
        :param name: The model name.
        :param platform: The asset bundle platform.
        """

        dest = self.dest.joinpath(wnid + "/" + name + "/" + platform)
        return "file:///" + str(dest.resolve()).replace("\\", "/")

    def create_asset_bundles(self, batch_size: int = 1000, vhacd_resolution: int = 8000000,
                             first_batch_only: bool = False) -> None:
        """
        Convert all .obj files into asset bundles.

        :param batch_size: The number of models per batch.
        :param vhacd_resolution: Higher value=better-fitting colliders and slower build process.
        :param first_batch_only: If true, output only the first batch. Useful for testing purposes.
        """

        records = ModelLibrarian(library=str(self.library_path.resolve())).records
        a = AssetBundleCreator(quiet=True)

        pbar = tqdm(total=len(records))
        while len(records) > 0:
            # Get the next batch.
            batch: List[ModelRecord] = records[:batch_size]
            records = records[batch_size:]

            for record in batch:
                # If the asset bundles for this record already exist, skip it.
                urls_exist = False
                for platform in record.urls:
                    url = record.urls[platform][8:]
                    if Path(url).exists():
                        urls_exist = True
                if urls_exist:
                    continue

                # If the prefab for this record exists, skip it.
                dest_path = Path.home().joinpath(f"asset_bundle_creator/Assets/Resources/models/{record.name}.obj")
                if dest_path.exists():
                    continue
                # Process the .obj
                obj_path = self._get_obj(record)
                # Move the files and remove junk.
                a.move_files_to_unity_project(None, model_path=obj_path, sub_directory=f"models/{record.name}")
            # Creating the asset bundles.
            a.create_many_asset_bundles(str(self.library_path.resolve()), cleanup=True,
                                        vhacd_resolution=vhacd_resolution)
            pbar.update(len(batch))

            # Process only the first batch of models.
            if first_batch_only:
                break
        pbar.close()

    def _get_directory_structure(self) -> str:
        """
        Returns a string representation of the expected directory structure.
        """

        raise Exception()

    def _assess_directory_structure(self) -> bool:
        """
        Check that the directory structure is correct.
        """

        raise Exception()

    def _get_obj(self, record: ModelRecord) -> Path:
        """
        Returns the .obj file associated with the record.

        :param record: The record.
        """

        raise Exception()


class ShapeNetSEM(_ShapeNet):
    """
    Generate asset bundles from ShapeNet SEM.
    """

    def _get_directory_structure(self) -> str:
        return "\tmodels/\n\tmetadata.csv"

    def _assess_directory_structure(self) -> bool:
        for q in ["models", "metadata.csv"]:
            if not self.src.joinpath(q).exists():
                return False
        textures_in_models = False
        for f in self.src.joinpath("textures").rglob("*.jpg"):
            textures_in_models = True
            break
        if not textures_in_models:
            if not self.src.joinpath("textures").exists():
                print("Missing textures/")
                return False
        return True

    def _get_obj(self, record: ModelRecord) -> Path:
        return self.src.joinpath(f"models/{record.name}.obj")

    def create_library(self) -> ModelLibrarian:
        lib = self._get_librarian("ShapeNetSEM")
        first_time_only = True
        metadata_path = self.src.joinpath("metadata.csv")
        with open(str(metadata_path), newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if first_time_only:
                    first_time_only = False
                    continue
                if row[1] == "" or row[3] == "":
                    continue
                record = ModelRecord()
                record.name = row[0][4:]
                record.wcategory = row[3].split(",")[0]
                record.wnid = f"n{int(row[2][1:]):08d}"

                for platform in record.urls:
                    record.urls[platform] = self._get_url(record.wnid, record.name, platform)
                lib.add_or_update_record(record, overwrite=False, write=False)
        # Write to disk.
        lib.write(pretty=False)

        # Move the textures.
        any_textures = False
        for f in self.src.joinpath("textures").rglob("*.jpg"):
            f.replace(self.src.joinpath(f"models/{f.name}"))
            any_textures = True
        if any_textures:
            print("Moved all .jpg files in textures/ to models/")
        return lib


class ShapeNetCore(_ShapeNet):
    """
    Generate asset bundles from ShapeNet Core v2.
    """

    def _get_obj(self, record: ModelRecord) -> Path:
        d = self.src.joinpath(record.wnid[1:] + "/" + record.name)

        # Move the images.
        models = d.joinpath("models")
        mtl = models.joinpath("model_normalized.mtl")
        if mtl.exists():
            mtl_txt = mtl.read_text(encoding="utf-8")
            for mtl_line in mtl_txt.split("\n"):
                # Move the texture.
                if "../images" in mtl_line:
                    tex_src = models.joinpath(mtl_line.split(" ")[1])
                    if tex_src.exists():
                        tex_dest = models.joinpath(tex_src.name)
                        tex_src.replace(tex_dest)
            # Update the mtl file.
            mtl_txt = mtl_txt.replace("../images/", "")
            mtl.write_text(mtl_txt)
            mtl.replace(models.joinpath(record.name + ".mtl"))
        obj = models.joinpath("model_normalized.obj")
        dest = models.joinpath(record.name + ".obj")
        if obj.exists():
            obj.replace(dest)

        # Fixed the mtl line.
        txt = dest.read_text(encoding="utf-8")
        txt = txt.replace("mtllib model_normalized.mtl", f"mtllib {record.name}.mtl")
        dest.write_text(txt, encoding="utf-8")

        return dest

    def _get_taxonomy_path(self) -> Path:
        """
        Returns the path to the taxonomy file.
        """

        return self.src.joinpath("taxonomy.json")
    
    def _get_directory_structure(self) -> str:
        return "\ttaxonomy.json\n\twnid/\n\twnid/\n\t(etc.)"

    def _assess_directory_structure(self) -> bool:
        taxonomy = self._get_taxonomy_path()
        if not taxonomy.exists():
            return False
        return True

    def create_library(self) -> ModelLibrarian:
        # Load the taxonomy file.
        taxonomy_raw = json.loads(self._get_taxonomy_path().read_text(encoding="utf-8"))
        taxonomy = dict()
        for synset in taxonomy_raw:
            taxonomy.update({synset["synsetId"]: synset["name"].split(",")[0]})
        # Create a new library.
        lib = self._get_librarian("ShapeNetCore")

        # Process each .obj file.
        for f in self.src.rglob("*.obj"):
            wnid = f.parts[-4]
            record = ModelRecord()
            record.name = f.parts[-3]
            record.wnid = "n" + wnid
            record.wcategory = taxonomy[wnid]
            for platform in record.urls:
                record.urls[platform] = self._get_url(record.wnid, record.name, platform)

            lib.add_or_update_record(record, overwrite=False, write=False)

        # Write to disk. Don't pretty-print (saves about 60 MB).
        lib.write(pretty=False)
        return lib


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--src", type=str, default="D:/ShapeNetCore.v2",
                        help="The absolute path to the root source directory.")
    parser.add_argument("--dest", type=str, default="D:/tdw_shapenet_core",
                        help="The absolute path to the root destination directory.")
    parser.add_argument("--set", type=str, default="core", choices=["core", "sem"],
                        help="Which ShapeNet set this is.")
    parser.add_argument("--batch_size", type=int, default=1000,
                        help="The number of models per batch.")
    parser.add_argument("--vhacd_resolution", type=int, default=8000000,
                        help="Higher value=better-fitting colliders and slower build process.")
    parser.add_argument("--first_batch_only", action="store_true",
                        help="Output only the first batch. Useful for testing purposes.")
    args = parser.parse_args()
    if args.set == "core":
        shapenet = ShapeNetCore(Path(args.src), Path(args.dest))
    else:
        shapenet = ShapeNetSEM(Path(args.src), Path(args.dest))
    shapenet.run(batch_size=args.batch_size, vhacd_resolution=args.vhacd_resolution,
                 first_batch_only=args.first_batch_only)
