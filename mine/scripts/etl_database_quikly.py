from pathlib import Path
import sys
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import file, helper
from services import config


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
    table_schema = helper.input_clean("input table_schema：")
    table_name = helper.input_clean("input table_name：")
    database_d = config.read_config("database", "utf-8")
    shell_config = config.shell_config()
    ks = {}
    cou = 0
    for k in database_d.keys():
        cou += 1
        ks[cou] = k
        print(f"{ks[cou]}->id_{cou}")
    database_k = ks[int(helper.input_clean("input database id："))]
    database_url = shell_config[database_k]
    engine = create_engine(database_url)

    if result == "p0":
        filepath = helper.input_clean("input file path：")
        powertable_name = helper.input_clean("input powertable_name：")
        with helper.Timer("read_powertable_to_sql_replace "):
            df = file.read_powertable(
                path=filepath, powertable_name=powertable_name, dtype=None
            )
            with engine.begin() as con:
                df.to_sql(
                    con=con,
                    schema=table_schema,
                    name=table_name,
                    index=False,
                    if_exists="replace",
                    method="multi",
                    chunksize=int(10000 / len(df.columns)),
                )
            print(f"done <{len(df)} rows>", end="")

    if result == "p1":
        folderpath = helper.input_folderpath()
        powertable_name = helper.input_clean("input powertable_name：")
        with helper.Timer("read_powertables "):
            df, count, *_ = file.read_powertables(
                path=folderpath, powertable_name=powertable_name, dtype=None
            )
            print(f"done <{count} files {len(df)} rows>", end="")
        with helper.Timer("to_sql_replace"):
            with engine.begin() as con:
                df.to_sql(
                    con=con,
                    schema=table_schema,
                    name=table_name,
                    index=False,
                    if_exists="replace",
                    method="multi",
                    chunksize=int(10000 / len(df.columns)),
                )
            print(f"done", end="")

    if result == "e1":
        folderpath, sheet_name = helper.input_folderpath_sheetname()
        with helper.Timer("read_excels"):
            df, count, *_ = file.read_excels(
                path=folderpath, sheet_name=sheet_name, dtype=None
            )
            print(f"done <{count} files {len(df)} rows>", end="")
        with helper.Timer("to_sql_replace"):
            with engine.begin() as con:
                df.to_sql(
                    con=con,
                    schema=table_schema,
                    name=table_name,
                    index=False,
                    if_exists="replace",
                    method="multi",
                    chunksize=int(10000 / len(df.columns)),
                )
            print("done", end="")

    if result == "e0":
        filepath = helper.input_clean("input file path：")
        sheet_name = helper.input_sheetname()
        with helper.Timer("read_excel"):
            df, *_ = file.read_excel(path=filepath, sheet_name=sheet_name, dtype=None)
            print(f"done <{len(df)} rows>", end="")
        with helper.Timer("to_sql_replace"):
            with engine.begin() as con:
                df.to_sql(
                    con=con,
                    schema=table_schema,
                    name=table_name,
                    index=False,
                    if_exists="replace",
                    method="multi",
                    chunksize=int(10000 / len(df.columns)),
                )
            print("done", end="")

    if result == "c1":
        folderpath = helper.input_folderpath()
        encoding = helper.input_clean("input encoding：")
        with helper.Timer("read_csvs"):
            df, count, *_ = file.read_csvs(
                path=folderpath, encoding=encoding, dtype=None
            )
            print(f"done <{count} files {len(df)} rows>", end="")
        with helper.Timer("to_sql_replace"):
            with engine.begin() as con:
                df.to_sql(
                    con=con,
                    schema=table_schema,
                    name=table_name,
                    index=False,
                    if_exists="replace",
                    method="multi",
                    chunksize=int(10000 / len(df.columns)),
                )
            print("done", end="")

    if result == "c0":
        filepath = helper.input_clean("input file path：")
        encoding = helper.input_clean("input encoding：")
        with helper.Timer("read_csv"):
            df, *_ = file.read_csv(path=filepath, encoding=encoding, dtype=None)
            print(f"done <{len(df)} rows>", end="")
        with helper.Timer("to_sql_replace"):
            with engine.begin() as con:
                df.to_sql(
                    con=con,
                    schema=table_schema,
                    name=table_name,
                    index=False,
                    if_exists="replace",
                    method="multi",
                    chunksize=int(10000 / len(df.columns)),
                )
            print("done", end="")
