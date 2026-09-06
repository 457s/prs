from pathlib import Path
import sys
from datetime import datetime
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import file


def extract_noreaded_excels(
    readed_d: dict,
    database_k: str,
    table_schema: str,
    table_name: str,
    folderpath: str | Path,
    sheet_name: str | int,
) -> tuple[pd.DataFrame, int, dict]:
    """return df,count,readed_d"""
    readedpaths = [
        Path(p)
        for v in readed_d[database_k][table_schema][table_name].values()
        for p in v
    ]
    readpaths = [
        p
        for p in Path(folderpath).rglob("*")
        if p.suffix in (".xls", ".xlsx") and p not in readedpaths
    ]
    df, count, readednewpaths = file.read_excels(readpaths, sheet_name=sheet_name)
    readed_d[database_k][table_schema][table_name][f"{datetime.now()}"] = [
        str(p.resolve()) for p in readednewpaths
    ]
    return df, count, readed_d


def extract_noreaded_csvs(
    readed_d: dict,
    database_k: str,
    table_schema: str,
    table_name: str,
    folderpath: str | Path,
    encoding: str,
) -> tuple[pd.DataFrame, int, dict]:
    """return df,count,readed_d"""
    readedpaths = [
        Path(p)
        for v in readed_d[database_k][table_schema][table_name].values()
        for p in v
    ]
    readpaths = [p for p in Path(folderpath).rglob("*.csv") if p not in readedpaths]
    df, count, readednewpaths = file.read_csvs(readpaths, encoding)
    readed_d[database_k][table_schema][table_name][f"{datetime.now()}"] = [
        str(p) for p in readednewpaths
    ]
    return df, count, readed_d


def extract_noreaded_powertables(
    readed_d: dict,
    database_k: str,
    table_schema: str,
    table_name: str,
    folderpath: str | Path,
    powertable_name: str,
) -> tuple[pd.DataFrame, int, dict]:
    """return df,count,readed_d"""
    readedpaths = [
        Path(p)
        for v in readed_d[database_k][table_schema][table_name].values()
        for p in v
    ]
    readpaths = [
        p
        for p in Path(folderpath).rglob("*")
        if p.suffix in (".xls", ".xlsx") and p not in readedpaths
    ]
    df, count, readednewpaths = file.read_powertables(readpaths, powertable_name)
    readed_d[database_k][table_schema][table_name][f"{datetime.now()}"] = [
        str(p.resolve()) for p in readednewpaths
    ]
    return df, count, readed_d
