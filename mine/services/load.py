from pathlib import Path
import sys
from sqlalchemy import text, Engine
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import database


def load_ods_oncols(
    database_d: dict,
    database_k: str,
    table_name: str,
    engine: Engine,
    df: pd.DataFrame,
) -> None:
    with engine.begin() as con:
        con.execute(text(f"""--sql
                        TRUNCATE TABLE ods.{table_name};"""))
        df[
            database_d[database_k]["ods"][table_name]["maincols"] + ["extra_data"]
        ].to_sql(
            con=con,
            name=table_name,
            schema="ods",
            index=False,
            if_exists="append",
            method="multi",
            chunksize=int(
                10000 / len(database_d[database_k]["ods"][table_name]["maincols"]) + 1
            ),
        )


def upsert_dwd_where_update_from_ods(table_name: str, engine: Engine):
    """all cols from ods into dwd"""
    allcols = database.select_allcols(engine, "ods", table_name)
    pkeycols = database.select_pkeycols(engine, "dwd", table_name)
    selectcols = ",".join([f'"{col}"' for col in allcols])
    pkeycols = ",".join([f'"{col}"' for col in pkeycols])
    setcols = ",".join(
        [f'"{col}"=EXCLUDED."{col}"' for col in allcols if col not in pkeycols]
    )
    with engine.begin() as con:
        con.execute(text(f"""--sql
                        INSERT INTO dwd.{table_name} ({selectcols})
                        SELECT {selectcols} FROM ods.{table_name}
                        ON CONFLICT({pkeycols}) DO UPDATE SET {setcols}
                        WHERE dwd.{table_name}."更新日期"<EXCLUDED."更新日期";
                          """))
