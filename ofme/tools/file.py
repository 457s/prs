import zipfile, os, xlwings
from pathlib import Path
import pandas as pd
import chardet


def generate_ppath(
    path: str | Path | list[str] | list[Path], suffix: list[str]
) -> list[Path]:
    """return ppath"""
    if type(path) is list:
        ppath = [Path(p) for p in path if Path(p).suffix in suffix]
    else:
        ppath = [p for p in Path(str(path)).rglob("*") if p.suffix in suffix]
    if len(ppath) == 0:
        raise Exception("generate_ppath error not find")
    return ppath


def rzips(path: str | Path | list[str] | list[Path]) -> int:
    """return count"""
    ppath = generate_ppath(path, [".zip"])
    count = 0
    for zpath in ppath:
        with zipfile.ZipFile(zpath, "r") as z:
            z.extractall(zpath.parent / zpath.stem)
        os.remove(zpath)
        count += 1
    return count


def read_excels(
    path: str | Path | list[str] | list[Path],
    sheet_name: str | int,
    header: int = 0,
    skiprows: int = 0,
    skipfooter: int = 0,
    na_values: list[str] = ["", " "],
    dtype: type | dict[str, type] | None = str,
) -> tuple[pd.DataFrame, int, list[Path]]:
    """return df,count,ppath"""
    ppath = generate_ppath(path, [".xlsx", ".xls"])
    dfs = []
    count = 0
    for p in ppath:
        df = pd.read_excel(
            p,
            sheet_name=sheet_name,
            header=header,
            skiprows=skiprows,
            skipfooter=skipfooter,
            na_values=na_values,
            dtype=dtype,
        )
        df["from_path"] = str(p.resolve())
        df["from_file"] = p.stem
        df["from_sheet"] = str(sheet_name)
        dfs.append(df)
        count += 1
    df = pd.concat(dfs, ignore_index=True)
    return df, count, ppath


def read_excel(
    path: str | Path,
    sheet_name: str | int,
    header: int = 0,
    skiprows: int = 0,
    skipfooter: int = 0,
    na_values: list[str] = ["", " "],
    dtype: type | dict[str, type] | None = str,
) -> tuple[pd.DataFrame, str | Path]:
    """return df,path"""
    df = pd.read_excel(
        path,
        sheet_name=sheet_name,
        header=header,
        skiprows=skiprows,
        skipfooter=skipfooter,
        na_values=na_values,
        dtype=dtype,
    )
    df["from_path"] = str(Path(path).resolve())
    df["from_file"] = Path(path).stem
    df["from_sheet"] = str(sheet_name)
    return df, path


def read_csvs(
    path: str | Path | list[str] | list[Path],
    encoding: str,
    header: int = 0,
    skiprows: int = 0,
    skipfooter: int = 0,
    na_values: list[str] = ["", " "],
    dtype: type | None = str,
) -> tuple[pd.DataFrame, int, list[Path]]:
    """return df,count,ppath"""
    ppath = generate_ppath(path, [".csv"])
    dfs = []
    count = 0
    for p in ppath:
        df = pd.read_csv(
            p,
            encoding=encoding,
            header=header,
            skiprows=skiprows,
            skipfooter=skipfooter,
            na_values=na_values,
            dtype=dtype,
        )
        df["from_path"] = str(p.resolve())
        df["from_file"] = p.stem
        dfs.append(df)
        count += 1
    df = pd.concat(dfs, ignore_index=True)
    return df, count, ppath


def read_csv(
    path: str | Path,
    encoding: str,
    header: int = 0,
    skiprows: int = 0,
    skipfooter: int = 0,
    na_values: list[str] = ["", " "],
    dtype: type | None = str,
) -> tuple[pd.DataFrame, str | Path]:
    """return df,path"""
    df = pd.read_csv(
        Path(path),
        encoding=encoding,
        header=header,
        skiprows=skiprows,
        skipfooter=skipfooter,
        na_values=na_values,
        dtype=dtype,
    )
    df["from_path"] = str(Path(path).resolve())
    df["from_file"] = Path(path).stem
    return df, path


def read_powertable(
    path: str | Path,
    powertable_name: str,
    header: bool = True,
    index: bool = False,
    na_values: list[str] = ["", " "],
    dtype: type | dict[str, type] | None = str,
) -> pd.DataFrame:
    """return df"""
    with xlwings.App(visible=False, add_book=False) as app:
        with app.books.open(Path(path), read_only=True) as wb:
            for sheet in wb.sheets:
                for table in sheet.tables:
                    if table.name == powertable_name:
                        df = table.range.options(
                            pd.DataFrame,
                            header=header,
                            index=index,
                            na_values=na_values,
                            dtype=dtype,
                        ).value
                        df["from_path"] = str(Path(path).resolve())
                        df["from_file"] = Path(path).stem
                        df["from_sheet"] = sheet.name
                        df["from_powertable"] = table.name
                        return df
    raise Exception("not find powertable or xw error")


def read_powertables(
    path: str | Path | list[str] | list[Path],
    powertable_name: str,
    header: bool = True,
    index: bool = False,
    na_values: list[str] = ["", " "],
    dtype: type | dict[str, type] | None = str,
) -> tuple[pd.DataFrame, int, list[Path]]:
    """return df,count,ppath"""
    ppath = generate_ppath(path, [".xlsx", ".xls"])
    dfs = []
    readed_files_path = []
    readed_tables_path = []
    with xlwings.App(visible=False, add_book=False) as app:
        for p in ppath:
            readed_files_path.append(p.resolve())
            with app.books.open(p, read_only=True) as wb:
                for sheet in wb.sheets:
                    for table in sheet.tables:
                        if table.name == powertable_name:
                            df = table.range.options(
                                pd.DataFrame,
                                header=header,
                                index=index,
                                na_values=na_values,
                                dtype=dtype,
                            ).value
                            df["from_path"] = str(p.resolve())
                            df["from_file"] = p.stem
                            df["from_sheet"] = sheet.name
                            df["from_powertable"] = table.name
                            dfs.append(df)
                            readed_tables_path.append(p.resolve())
    if len(readed_files_path + readed_tables_path) == 0:
        raise Exception("xw.App error")
    else:
        not_find_tale = [p for p in readed_files_path if p not in readed_tables_path]
        if len(not_find_tale) != 0:
            for result in not_find_tale:
                print(f"<{str(result)}>")
            raise Exception("these excels not find powertable or open error")
        else:
            df = pd.concat(dfs, ignore_index=True)
            count = len(readed_tables_path)
            return df, count, ppath


def check_file_encoding(file_path: str | Path) -> None:
    with open(Path(file_path), "rb") as f:
        result = chardet.detect(f.read())
    print(result)
