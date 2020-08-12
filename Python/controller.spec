# -*- mode: python -*-
import sys
from pathlib import Path
from PyInstaller.utils.hooks import copy_metadata
import os

# Read the config file.
config_file = Path.home().joinpath("tdw_build/tdw_controller/freeze.ini")
assert config_file.exists()
config = config_file.read_text(encoding="utf-8")
controller = Path(config.split("controller=")[1])
root_dir = str(controller.parent.resolve())
controller = str(controller.resolve())

block_cipher = None

datas = copy_metadata("tdw")
# Add TDW data files.
for root, dirs, files in os.walk("tdw"):
    if "tdw.egg-info" in root or "__pycache__" in root:
        continue
    for file in files:
        if ".py" in file:
            continue
        datas.append((root, file))

hiddenimports = []

a = Analysis([controller],
             pathex=[str(Path(controller).parent.resolve())],
             binaries=[],
             datas=datas,
             hiddenimports=hiddenimports,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='tdw_controller',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True)
if sys.platform == "darwin":
    app = BUNDLE(exe,
         name='tdw_controller.app',
         icon=None,
         bundle_identifier=None)
