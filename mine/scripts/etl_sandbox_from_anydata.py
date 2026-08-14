from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from services import sandbox
from tools import helper


def main():
    while True:
        filetype = input("excel -> e | powertable -> p | csv -> c：")
        mod = input("many -> 1 | one -> 0：")
        result = filetype + mod
        if result not in ["e1", "e0", "p1", "p0", "c1", "c0"]:
            print("error input")
            qc = input("continue -> .* | quit -> q：")
            if qc == "q":
                raise
            continue
        else:
            break

    if result == "e1":
        folderpath, sheet_name = helper.input_folderpath_sheetname()
        with helper.Timer("excels_to_sandbox"):
            count = sandbox.excels_to_sandbox(folderpath, sheet_name)
            print(f"done <{count} files>", end="")
    elif result == "e0":
        path = helper.input_clean("input file path：")
        sheet_name = helper.input_sheetname()
        with helper.Timer("excel_to_sandbox"):
            sandbox.excel_to_sandbox(path, sheet_name)
            print("done", end="")
    elif result == "c1":
        folderpath = helper.input_folderpath()
        encoding = helper.input_clean("input encoding：")
        with helper.Timer("csvs_to_sandbox"):
            count = sandbox.csvs_to_sandbox(folderpath, encoding)
            print(f"done <{count} files>", end="")
    elif result == "c0":
        path = helper.input_clean("input file path：")
        encoding = helper.input_clean("input encoding：")
        with helper.Timer("csv_to_sandbox"):
            sandbox.csv_to_sandbox(path, encoding)
            print("done")
    elif result == "p1":
        folderpath = helper.input_folderpath()
        powertablename = helper.input_clean("input powertable name：")
        with helper.Timer(""):
            count = sandbox.powertables_to_sandbox(folderpath, powertablename)
            print(f"done <{count} files>", end="")
    elif result == "p0":
        path = helper.input_clean("input file path：")
        powertablename = helper.input_clean("input powertable name：")
        with helper.Timer(""):
            sandbox.powertable_to_sandbox(path, powertablename)
            print("done", end="")
