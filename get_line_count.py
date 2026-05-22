from pathlib import Path
parent=Path(__file__).parent

def get_files() -> list[Path]:
    l=[]
    for f in parent.rglob("*.py"):
        if f == Path(__file__):
            continue
        l.append(f)
    return l


lines = 0
for file in get_files():
    _ = []
    embedded_quote = False
    for i in file.read_text().splitlines():
        if i.replace(" ", "").strip("\t").strip("\n") == "":
            continue
        if i.startswith("#"):
            continue

        _.append(i)
    l=len(_)
    lines += l
print("total lines:",lines)