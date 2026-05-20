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
    l=len(file.read_text().splitlines())
    lines += l
print("total lines:",lines)