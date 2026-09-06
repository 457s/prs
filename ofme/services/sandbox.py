from pathlib import Path
import sys
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import file


def excels_to_sandbox(folder_path: Path | str, sheet_name: str | int) -> int:
    """return count"""
    df, count, *_ = file.read_excels(Path(folder_path), sheet_name=sheet_name)
    out_file_stem = (
        str(Path(folder_path).resolve())
        .replace(":", "_")
        .replace("\\", "_")
        .replace("/", "_")
        + "_"
        + "ctime"
        + f"{datetime.now().strftime('%Y年%m月%d日%H时%M分%S秒')}"
    )
    df.to_excel(
        ROOT / "sandbox" / f"{out_file_stem}.xlsx",
        index=False,
        engine="xlsxwriter",
    )
    return count


def excel_to_sandbox(path: str | Path, sheet_name: str | int) -> Path | str:
    """return path"""
    df, path = file.read_excel(Path(path), sheet_name=sheet_name)
    out_file_stem = (
        str(Path(path).resolve()).replace(":", "_").replace("\\", "_").replace("/", "_")
        + "_"
        + "ctime"
        + f"{datetime.now().strftime('%Y年%m月%d日%H时%M分%S秒')}"
    )
    df.to_excel(
        ROOT / "sandbox" / f"{out_file_stem}.xlsx",
        index=False,
        engine="xlsxwriter",
    )
    return path


def csvs_to_sandbox(folder_path: Path | str, encoding: str) -> int:
    """return count"""
    df, count, *_ = file.read_csvs(Path(folder_path), encoding=encoding)
    out_file_stem = (
        str(Path(folder_path).resolve())
        .replace(":", "_")
        .replace("\\", "_")
        .replace("/", "_")
        + "_"
        + "ctime"
        + f"{datetime.now().strftime('%Y年%m月%d日%H时%M分%S秒')}"
    )
    df.to_excel(
        ROOT / "sandbox" / f"{out_file_stem}.xlsx",
        index=False,
        engine="xlsxwriter",
    )
    return count


def csv_to_sandbox(path: Path | str, encoding: str) -> Path | str:
    """return path"""
    df, path = file.read_csv(Path(path), encoding=encoding)
    out_file_stem = (
        str(Path(path).resolve()).replace(":", "_").replace("\\", "_").replace("/", "_")
        + "_"
        + "ctime"
        + f"{datetime.now().strftime('%Y年%m月%d日%H时%M分%S秒')}"
    )
    df.to_excel(
        ROOT / "sandbox" / f"{out_file_stem}.xlsx",
        index=False,
        engine="xlsxwriter",
    )
    return path


def powertables_to_sandbox(folder_path: str | Path, powertable_name: str) -> int:
    """return count"""
    df, count, *_ = file.read_powertables(folder_path, powertable_name)
    out_file_stem = (
        str(Path(folder_path).resolve())
        .replace(":", "_")
        .replace("\\", "_")
        .replace("/", "_")
        + "_"
        + "ctime"
        + f"{datetime.now().strftime('%Y年%m月%d日%H时%M分%S秒')}"
    )
    df.to_excel(
        ROOT / "sandbox" / f"{out_file_stem}.xlsx",
        index=False,
        engine="xlsxwriter",
    )
    return count


def powertable_to_sandbox(path: str | Path, powertable_name: str) -> Path | str:
    """return path"""
    df = file.read_powertable(path, powertable_name)
    out_file_stem = (
        str(Path(path).resolve()).replace(":", "_").replace("\\", "_").replace("/", "_")
        + "_"
        + "ctime"
        + f"{datetime.now().strftime('%Y年%m月%d日%H时%M分%S秒')}"
    )
    df.to_excel(
        ROOT / "sandbox" / f"{out_file_stem}.xlsx",
        index=False,
        engine="xlsxwriter",
    )
    return path
