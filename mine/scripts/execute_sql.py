from pathlib import Path
import sys
from sqlalchemy import create_engine

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import database, helper
from services import config


def main():
    i = 0
    m = {}
    for p in Path(ROOT / "sql").rglob("*.sql"):
        i += 1
        m[i] = p
        print(f"{m[i]} -> id.{i}")
    iid = int(input("input execute id："))
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
    engine = create_engine(database_url)
    print(f"\n{m[iid]} <")
    database.execute_sql(engine=engine, encoding="utf-8", sqlpath=m[iid])
