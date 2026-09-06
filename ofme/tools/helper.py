from pathlib import Path
import time
from typing import Callable
from functools import wraps


def input_folderpath() -> Path:
    """return folderpath"""
    while True:
        folderstring = input("input dir path：").strip('"').strip("'").strip()
        folderpath = Path(folderstring)
        if not folderpath.is_dir():
            print("is not dir")
            qc = input("continue -> .* | quit -> q：")
            if qc == "q":
                raise
            continue
        else:
            break
    return folderpath


def input_sheetname() -> int | str:
    """return sheet_name"""
    sheetnamestring = input("input sheet ：").strip('"').strip("'").strip()
    try:
        sheet_name = int(sheetnamestring)
    except:
        sheet_name = sheetnamestring
    return sheet_name


def input_folderpath_sheetname() -> tuple[Path, int | str]:
    """return folderpath,sheet_name"""
    folderpath = input_folderpath()
    sheet_name = input_sheetname()
    return folderpath, sheet_name


def input_clean(description: str) -> str:
    """return result"""
    result = input(f"{description}").strip('"').strip("'").strip()
    return result


class Timer:
    """def __init__(self,description:str) -> None:
    self.description=description"""

    def __init__(self, description: str) -> None:
        self.description = description

    def __enter__(self) -> "Timer":
        print(f"begin {self.description}...", end="", flush=True)
        self.start = time.time()
        return self

    def __exit__(self, *args) -> None:
        self.elapsed = time.time() - self.start
        print(f" {self.elapsed:.2f}s")


def timer(func: Callable) -> Callable:
    """return wrapper"""

    @wraps(func)
    def wrapper():
        print(f"begin {func.__name__}...", end="", flush=True)
        start = time.time()
        func()
        end = time.time()
        elapsed = end - start
        print(f" {elapsed:.2f}s")

    return wrapper
