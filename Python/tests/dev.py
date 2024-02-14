

def config():
    """
    Test the Config class.
    """

    from tdw.dev.config import Config
    c = Config()
    for path in [c.ini_path, c.tdw_path, c.tdwunity_path, c.tdw_docs_path]:
        assert path.exists(), path


def versions():
    """
    Test the version strings.
    """

    from tdw.dev.versions import PROJECT_SETTINGS_PATH, VERSION_UNITY_EDITOR, versions_are_equal
    assert PROJECT_SETTINGS_PATH.exists(), PROJECT_SETTINGS_PATH
    assert VERSION_UNITY_EDITOR == "2020.3.24f1", VERSION_UNITY_EDITOR
    vs = versions_are_equal()
    assert vs[0], vs[1]


if __name__ == "__main__":
    config()
    versions()
