from pathlib import Path
from argparse import ArgumentParser
from benchmark_utils import PATH

parser = ArgumentParser()
parser.add_argument("version", type=str, nargs="?", help="Version number")
args = parser.parse_args()


txt = Path("../../Documentation/benchmark/template.md").read_text()

txt = txt.replace("$TDW_VERSION", f"TDW v{args.version}")

PATH.write_text(txt)
