from argparse import ArgumentParser
import os.path
from json import dumps
from typing import Dict, List
import re
from pathlib import Path
from requests import get
from tqdm import tqdm
import boto3


class Location:
    """
    Location data from an IP address lookup.
    """

    def __init__(self, json_data: dict):
        self.address: str = json_data["ip"]
        self.network: str = json_data["network"]
        self.city: str = json_data["city"]
        self.region: str = json_data["region"]
        self.country: str = json_data["country"]
        self.latitude: float = json_data["latitude"]
        self.longitude: float = json_data["longitude"]
        self.num_requests: int = 1
        self.num_bytes: int = 0


class LoggedData:
    """
    Logged data from an S3 log.
    """

    def __init__(self, text: str):
        regex = re.search(r'\w+ (tdw-(public|private)) \[(.*?)] ((?:[0-9]{1,3}\.){3}[0-9]{1,3}) - \w+ REST.\w+.\w+ (.*?) ("(.*?)") (\d+)', text)
        self.bucket: str = ""
        self.time: str = ""
        self.ip_address: str = ""
        self.request: str = ""
        self.status_code: int = 0
        self.num_bytes: int = 0
        self.file_name: str = ""
        self.library: str = ""
        self.asset_bundle_type: str = ""
        self.valid: bool = True
        self.upload: bool = False
        if regex is None:
            self.valid = False
            return
        self.bucket = regex.group(1)
        self.time = regex.group(3)[:-6]
        self.ip_address = regex.group(4)
        self.request = regex.group(5)
        self.status_code = int(regex.group(8))
        # Read the successful log.
        if self.status_code == 200:
            regex = re.search(r'(.*?) 200 - (\d+) \d+ ', text)
            # This is an upload.
            if regex is None:
                self.upload = True
                return
            self.num_bytes = int(regex.group(2))
            file_path = [fp for fp in self.request.split("/") if len(fp.strip()) > 0]
            self.library = file_path[0]
            self.file_name = file_path[-1]
            if "materials" in self.library:
                self.asset_bundle_type = "material"
            elif "models" in self.library:
                self.asset_bundle_type = "model"
            elif "scenes" in self.library:
                self.asset_bundle_type = "scene"
            elif "skyboxes" in self.library:
                self.asset_bundle_type = "skybox"
            elif "robots" in self.library:
                self.asset_bundle_type = "robot"
            elif "animations" in self.library:
                self.asset_bundle_type = "humanoid animation"
            elif "humanoids" in self.library:
                self.asset_bundle_type = "non-physics humanoid"
            elif "replicants" in self.library:
                self.asset_bundle_type = "replicant"
            elif "drones" in self.library or "flying_objects" in self.library:
                self.asset_bundle_type = "drone"
            elif "effects" in self.library:
                self.asset_bundle_type = "visual effect"
            elif "vehicles" in self.library:
                self.asset_bundle_type = "vehicle"
            else:
                raise Exception(f"Undefined asset bundle type: {self.library}")


class Downloads:
    """
    The number of unique downloads for a given asset bundle.
    """

    def __init__(self, library: str, num_bytes: int):
        self.library: str = library
        self.num_downloads: int = 1
        self.num_bytes: int = num_bytes


class S3LogAnalyzer:
    """
    Analyze S3 logs.
    """

    def __init__(self, directory: Path):
        """
        :param directory: The logs directory.
        """

        if not directory.exists():
            directory.mkdir(parents=True)
        self.directory: Path = directory.resolve()

    def download(self, prefix: str = None) -> None:
        """
        Download logs to `self.directory`.

        :param prefix: An optional prefix that will be used as a filter, e.g. `"tdw-log-2023-06-02"`.
        """

        session = boto3.Session(profile_name="tdw")
        bucket = 'tdw-cc-access-logs'
        s3 = session.resource("s3")
        bucket = s3.Bucket(bucket)
        for obj_summary in (bucket.objects.all() if prefix is None else bucket.objects.filter(Prefix=prefix)):
            key = obj_summary.key
            obj = obj_summary.get()
            self.directory.joinpath(f"{key}.txt").write_bytes(obj["Body"].read())

    def to_json(self) -> None:
        """
        Iterate through all downloaded logs and write the following .json files to `<output directory>/analysis/`:

        1. `locations.json` The number of downloads per location.
           To generate this file, this script does an HTTP request to `https://ipapi.co` for every new IP address.
           In most cases, this should therefore be only a few requests.
        2. `logs.json` A .json file containing useful data from every log.
        3. `downloads.json` The number of downloads per asset bundle per location.
        """

        locations: Dict[str, Location] = dict()
        logs: Dict[str, List[LoggedData]] = dict()
        downloads: Dict[str, Dict[str, Downloads]] = dict()
        # Get a progress bar. Get the total number of children in the directory.
        pbar = tqdm(total=len(os.listdir(str(self.directory.resolve()))))
        for path in self.directory.iterdir():
            # Make sure this path is a file.
            if path.is_file():
                log_text = path.read_text()
                for log in log_text.split("\n"):
                    if len(log) == 0:
                        continue
                    # Get the logged data.
                    logged_data = LoggedData(text=log)
                    address: str = logged_data.ip_address[:]
                    # Look up the IP address.
                    if address not in locations:
                        ip_data = get(f'https://ipapi.co/{address}/json/').json()
                        # Possibly, there was a time out.
                        if "ip" not in ip_data or ("error" in ip_data and ip_data["error"]):
                            continue
                        locations[address] = Location(ip_data)
                    # Increment the number of requests.
                    else:
                        locations[address].num_requests += 1
                    # Increment the number of bytes.
                    if logged_data.valid and not logged_data.upload:
                        locations[address].num_bytes += logged_data.num_bytes
                    # Store the logged data.
                    if address not in logs:
                        logs[address] = list()
                    logs[address].append(logged_data)
                    # Store the number of downloads.
                    if logged_data.valid:
                        if address not in downloads:
                            downloads[address] = dict()
                        if logged_data.file_name not in downloads[address]:
                            downloads[address][logged_data.file_name] = Downloads(library=logged_data.library,
                                                                                  num_bytes=logged_data.num_bytes)
                        else:
                            downloads[address][logged_data.file_name].num_downloads += 1
                pbar.update(1)
        # Write the logged data to disk.
        output_directory = self.directory.joinpath("analysis")
        if not output_directory.exists():
            output_directory.mkdir(parents=True)
        d = {k: v.__dict__ for (k, v) in locations.items()}
        output_directory.joinpath("locations.json").write_text(dumps(d, indent=2, sort_keys=True))
        d = {k: [vv.__dict__ for vv in v] for (k, v) in logs.items()}
        output_directory.joinpath("logs.json").write_text(dumps(d, indent=2, sort_keys=True))
        q = dict()
        for k in downloads:
            q[k] = dict()
            for v in downloads[k]:
                q[k][v] = downloads[k][v].__dict__
        output_directory.joinpath("downloads.json").write_text(dumps(q, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("directory", type=str,
                        help="Either the directory you want to download to, or the directory of the downloaded logs.",)
    parser.add_argument("--download", action="store_true",
                        help="Download logs to `directory`. Requires S3 credentials")
    parser.add_argument("--prefix", type=str, required=False,
                        help="If included after --download, this is a prefix that this script will use to filter downloads."
                             " For example: tdw-log-2023-06-02")
    args = parser.parse_args()
    analyzer = S3LogAnalyzer(directory=Path(args.directory).resolve())
    if args.download:
        analyzer.download(prefix=args.prefix)
    else:
        analyzer.to_json()
