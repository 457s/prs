from pathlib import Path
import sys
from sqlalchemy import create_engine

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from services import config, extract, transform, load
from tools import helper


def main():
    table_name = input("input table_name：")
    folderpath, sheet_name = helper.input_folderpath_sheetname()
    database_d = config.read_config("database", "utf-8")
    shell_config = config.shell_config()
    ks = {}
    cou = 0
    for k in database_d.keys():
        cou += 1
        ks[cou] = k
        print(f"{ks[cou]}->id_{cou}")
    database_k = ks[int(helper.input_clean("input database id：")[0])]
    database_url = shell_config[database_k]
    readed_d = config.read_config("readed", "utf-8")
    engine = create_engine(database_url)

    with helper.Timer("extract_noreaded_excels"):
        df, count, readed_d = extract.extract_noreaded_excels(
            readed_d, database_k, "dwd", table_name, folderpath, sheet_name
        )
        print(f"done <{count} files {len(df)} rows>", end="")

    with helper.Timer("clean_oncols"):
        df = transform.clean_oncols(database_d, database_k, "ods", table_name, df)
        print("done", end="")

    with helper.Timer("load_ods_oncols"):
        load.load_ods_oncols(database_d, database_k, table_name, engine, df)
        print("done", end="")

    with helper.Timer("upsert_dwd_where_update_from_ods"):
        load.upsert_dwd_where_update_from_ods(table_name, engine)
        print("done", end="")

    with helper.Timer("write_config on readed_paths"):
        config.write_config("readed", readed_d, "utf-8")
        print("done", end="")
