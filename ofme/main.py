from pathlib import Path
import sys, importlib

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def main():
    module_paths = [
        p for p in Path(ROOT / "scripts").glob("*.py") if not p.stem.startswith("_")
    ]
    m = {}
    i = 0
    for module_path in module_paths:
        i += 1
        m[i] = module_path.stem
        print(f"{m[i]} -> id_{i}")
    idd = int(input("input main id："))

    print(f"\n> {m[idd]} <")
    module_name = f"scripts.{m[idd]}"
    module = importlib.import_module(module_name)
    module.main()


if __name__ == "__main__":
    while True:
        try:
            print("==============================")
            main()
            print("!!!done!!!")
        except Exception as e:
            print(f"!!!{e}!!!")
        qc = input("continue -> .* | quit -> q：")
        if qc == "q":
            break
