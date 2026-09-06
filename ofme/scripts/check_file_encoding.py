from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import file, helper


def main():
    path = Path(helper.input_clean("input file path："))
    print()
    file.check_file_encoding(path)
