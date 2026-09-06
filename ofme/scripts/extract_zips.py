from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import file, helper


def main():
    folderpath = helper.input_folderpath()

    with helper.Timer("rzips"):
        count = file.rzips(folderpath)
        print(f"done <{count} files>", end="")
