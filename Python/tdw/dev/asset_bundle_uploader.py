from pathlib import Path
import boto3
from tdw.asset_bundle_creator.asset_bundle_creator import AssetBundleCreator
from tdw.librarian import _Librarian, _Record
from tdw.backend.platforms import SYSTEM_TO_S3


def upload_asset_bundles(name: str, asset_bundles_directory: str, librarian: _Librarian, record: _Record = None,
                         url_infix: str = "models", bucket: str = "tdw-public", write: bool = True,
                         quiet: bool = False) -> _Librarian:
    """
    Upload asset bundles to the S3 repository.

    This function requires admin AWS credentials.

    The `asset_bundle_directory` *must* be structured like this:

    ```
    asset_bundle_directory/
    ....Darwin/
    ........name
    ....Linux/
    ........name
    ....Windows/
    ........name
    ....WebGL/
    ........name
    ```

    ...where `........name` is the asset bundle for each platform.

    You do not have to include asset bundles for every platform. You can optionally do something like this:

    ```
    asset_bundle_directory/
    ....Darwin/
    ........name
    ....Windows/
    ........name
    ```

    :param name: The name of the asset bundle.
    :param asset_bundles_directory: The absolute path to the asset bundles directory.
    :param librarian: The metadata librarian. The record will be added to the librarian if it doesn't exist (and if `record is not None`), or updated if it already exists.
    :param record: The metadata record. If None, this parameter is ignored. Otherwise, this record will be added to the librarian, or will overwrite an existing record of the same name.
    :param url_infix: The infix of the URL describing the type of asset bundle, for example `"models"` or `"robots"`.
    :param bucket: The S3 bucket.
    :param write: If True, immediately write changes to the librarian to disk.
    :param quiet: If True, don't print messages to the console.

    :return: The updated librarian.
    """

    src_directory: Path = Path(asset_bundles_directory).resolve()
    # Verify that the asset bundles source directory exists.
    assert src_directory.exists(), f"Directory not found: {src_directory}"
    # Verify that the asset bundles exist.
    assert AssetBundleCreator.asset_bundles_exist(name=name, directory=src_directory), \
        f"Asset bundles not found for: {name}"
    # Get the metadata record from the librarian.
    if record is None:
        record = librarian.get_record(name)
        assert record is not None, f"Record not found for: {name}"
    # Load S3.
    s3 = boto3.resource('s3')
    for platform in SYSTEM_TO_S3:
        # Get the asset bundle path.
        asset_bundle_path = src_directory.joinpath(platform).joinpath(name).resolve()
        if not asset_bundle_path.exists():
            print("Asset bundle not found:", asset_bundle_path)
        # Get the S3 path (everything in the URL after the ".com").
        s3_path = f"{url_infix}/{SYSTEM_TO_S3[platform]}/{AssetBundleCreator.UNITY_VERSION}/{name}"
        # Create an S3 object.
        s3_object = s3.Object(bucket, s3_path)
        # Put the object in the bucket.
        s3_object.put(Body=asset_bundle_path.read_bytes())
        # Set permissions.
        if "public" in bucket:
            s3_object.Acl().put(ACL="public-read")
        # Set the URL.
        record.urls[platform] = f"https://{bucket}.s3.amazonaws.com/{s3_path}"
        if not quiet:
            print(f"Uploaded: {record.urls[platform]}")
    # Update the library.
    librarian.add_or_update_record(record=record, overwrite=True, write=write, quiet=quiet)
    return librarian
