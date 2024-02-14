from pathlib import Path


class Config:
    """
    Read an .ini file for development and testing of TDW.
    Create the .ini file if it doesn't already exist.
    """

    def __init__(self):
        """
        (no arguments)
        """

        """:field
        The path to the config.ini file.
        """
        self.ini_path: Path = Path.home().joinpath("tdw_config/config.ini")
        # Create the .ini file if it doesn't exist.
        if not self.ini_path.exists():
            # Create the parent directory.
            if not self.ini_path.parent.exists():
                self.ini_path.parent.mkdir(parents=True)
            print("config.ini doesn't exist yet.")
            # User input.
            tdwunity_path = Config._get_path("TDWUnity")
            tdw_path = Config._get_path("tdw")
            tdw_docs_path = Config._get_path("tdw_docs")
            # Write the file.
            self.ini_path.write_text(f"TDWUnity={tdwunity_path}\ntdw={tdw_path}\ntdw_docs={tdw_docs_path}",
                                     encoding="utf-8")
            print(f"Created: {self.ini_path.resolve()}")
        # Read the .ini file.
        txt = self.ini_path.read_text(encoding="utf-8")
        """:field
        The path to the TDWUnity repo.
        """
        self.tdwunity_path: Path = Path(self._get_value("TDWUnity", txt))
        """:field
        The path to the tdw repo.
        """
        self.tdw_path: Path = Path(self._get_value("tdw", txt))
        """:field
        The path to the tdw_docs repo.
        """
        self.tdw_docs_path: Path = Path(self._get_value("tdw_docs", txt))

    @staticmethod
    def _get_path(repo: str) -> str:
        """
        Prompt for user input until the input is a valid path.

        :param repo: The name of the repo.

        :return: The path.
        """

        got_path = False
        path = ""
        while not got_path:
            # User input.
            path = input(f"Absolute path to your local {repo} directory: ").replace('"', '')
            # Check if the path exists.
            got_path = Path(path).exists()
        return path

    @staticmethod
    def _get_value(key: str, txt: str) -> str:
        """
        :param key: The key for the value in the config.ini file.
        :param txt: The text of the config.ini file.

        :return: A value in config.ini
        """

        for line in txt.split("\n"):
            if line.startswith(key):
                return line.split("=")[1].strip()
        raise Exception(f"Key not found: {key}")
