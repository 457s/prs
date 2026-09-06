from pathlib import Path
import sys, importlib

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import helper
from services import config


def main():
    tasks_d = config.read_config(jsonname="tasks", encoding="utf-8")
    task_ks = {}
    k_id = 0
    for k in tasks_d.keys():
        k_id += 1
        print(f"{k}->id_{k_id}")
        task_ks[k_id] = k
    iid = int(helper.input_clean("input task id："))
    task = tasks_d[task_ks[iid]]
    numb = 0
    for mod in task:
        numb += 1
        print(f"\nmain{numb}>{mod}<")
        module = importlib.import_module(mod)
        module.main()
