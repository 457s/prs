from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import cleandf


def clean_oncols(
    database_d: dict,
    database_k: str,
    table_schema: str,
    table_name: str,
    df: pd.DataFrame,
) -> pd.DataFrame:
    """return ddf.df"""
    ddf = cleandf.Cleandf(df)
    ddf.clean_columns
    maincols = database_d[database_k][table_schema][table_name]["maincols"]
    numcols = database_d[database_k][table_schema][table_name]["numcols"]
    pecols = database_d[database_k][table_schema][table_name]["pecols"]
    datecols = database_d[database_k][table_schema][table_name]["datecols"]
    strcols = database_d[database_k][table_schema][table_name]["strcols"]
    for c in maincols:
        if c not in ddf.df.columns:
            ddf.df[c] = None
    othercols = [c for c in ddf.df.columns if c not in maincols]
    ddf.df["extra_data"] = ddf.df[othercols].apply(
        lambda row: row.to_json(force_ascii=False), axis=1
    )
    ddf.clean_number_cols(numcols).clean_percentage_cols(pecols).clean_date_cols(
        datecols
    ).clean_str_cols(strcols)
    return ddf.df
