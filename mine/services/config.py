from pathlib import Path
import sys, shutil, json
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def read_config(jsonname: str, encoding: str) -> dict:
    """return jsond"""
    with open(ROOT / "config" / f"{jsonname}.json", "r", encoding=encoding) as j:
        jsond = json.load(j)
    return jsond


def write_config(jsonname: str, jsond: dict, encoding: str) -> None:
    shutil.copy2(
        ROOT / "config" / f"{jsonname}.json",
        ROOT
        / "backup"
        / f'{jsonname}_{datetime.now().strftime("%Y年%m月%d日%H时%M分%S秒")}.json',
    )
    with open(ROOT / "config" / f"{jsonname}.json", "w", encoding=encoding) as j:
        json.dump(jsond, j, ensure_ascii=False)


def shell_config() -> dict:
    """return jsond"""
    with open(ROOT.parent / "env" / "config.json") as f:
        jsond = json.load(f)
    return jsond
