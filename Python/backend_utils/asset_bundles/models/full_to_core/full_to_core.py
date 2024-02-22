from pathlib import Path
from requests import head
from tqdm import tqdm
import boto3
from tdw.dev.config import Config
from tdw.librarian import ModelLibrarian

"""
Copy models from models_full.json to models_core.json

This will check the records to make sure they're ok, and then copy the asset bundle from tdw-private to tdw-public
This will also update the library json files in both libraries to point to the public URL.
"""

config = Config()
private_models = Path("full_to_core.txt").read_text().strip().split("\n")
lib_full = ModelLibrarian("models_full.json")
lib_core = ModelLibrarian("models_core.json")

session = boto3.Session(profile_name="tdw")
s3 = session.resource("s3")

pbar = tqdm(total=len(private_models) * 3)
for private_model in private_models:
    pbar.set_description(private_model)
    record_full = lib_full.get_record(private_model)
    if record_full is None:
        print(f"WARNING: No record for {private_model}")
        pbar.update(3)
        continue
    if record_full.do_not_use:
        print(f"SKIPPING {private_model} because it's flagged as do_not_use: {record_full.do_not_use_reason}")
        pbar.update(3)
        continue
    record_core = lib_core.get_record(private_model)
    if record_core is not None:
        pbar.update(3)
        continue
    urls = dict()
    for platform in record_full.urls:
        # Download the model.
        key = record_full.urls[platform].split("https://tdw-private.s3.amazonaws.com/")[1]
        resp = s3.meta.client.get_object(Bucket='tdw-private', Key=key)
        status_code = resp["ResponseMetadata"]["HTTPStatusCode"]
        if status_code != 200:
            print(f"WARNING {private_model} for {platform} is missing!")
            pbar.update(1)
            continue
        # Upload the asset bundle.
        s3_object = s3.Object("tdw-public", key)
        s3_object.put(Body=resp["Body"].read())
        s3_object.Acl().put(ACL="public-read")
        # Update the URLs.
        url = f"https://tdw-public.s3.amazonaws.com/{key}"
        resp = head(url)
        if resp.status_code != 200:
            print(f"WARNING: Got code {resp.status_code} for {url}")
        urls[platform] = url
        pbar.update(1)
    record_full.urls = urls
    # Add the record.
    lib_core.add_or_update_record(record=record_full, overwrite=False, write=True)
    # Update the record.
    lib_full.add_or_update_record(record=record_full, overwrite=True, write=True)
