from sqlalchemy import text, Engine
from pathlib import Path
import pandas as pd


def select_allcols(engine: Engine, table_schema: str, table_name: str) -> list[str]:
    """return allcols"""
    with engine.begin() as con:
        result = con.execute(text(f"""--sql
                         SELECT column_name FROM information_schema.columns
                         WHERE table_schema='{table_schema}' AND table_name='{table_name}'
                         ORDER BY ordinal_position ASC; """))
        rows = result.fetchall()
    allcols = [v[0] for v in rows]
    return allcols


def select_pkeycols(engine: Engine, table_schema: str, table_name: str) -> list[str]:
    """return pkeycols"""
    with engine.begin() as con:
        result = con.execute(text(f"""--sql
                                SELECT column_name FROM information_schema.key_column_usage
                                WHERE table_schema='{table_schema}' AND table_name='{table_name}'
                                ORDER BY  ordinal_position ASC """))
        rows = result.fetchall()
    pkeycols = [v[0] for v in rows]
    return pkeycols


def execute_sql(engine: Engine, sqlpath: str | Path, encoding: str) -> None:
    with open(Path(sqlpath), "r", encoding=encoding) as f:
        sql = f.read()
    with engine.begin() as con:
        execute_count = 0
        for s in sql.split(";"):
            if s.replace(" ", "").strip():
                execute_count += 1
                res = con.execute(text(s))
                if res.returns_rows:
                    header = list(res.keys())
                    data = [list(row) for row in res]
                    df = pd.DataFrame(data=data, columns=header)
                    print(f"execute {execute_count}：")
                    print(df)
                else:
                    print(f"execute {execute_count}：")
                    print(f"sql {res.rowcount} rows")
        if execute_count == 0:
            raise Exception("none sql")
