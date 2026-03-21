import os

root = r"c:\Users\Lenovo\Antigravity_Home\Proyecto_Antigravity"
patterns = ["06/03", "06-03", "03/06", "Glifosato"]

def search():
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirpath or "node_modules" in dirpath or ".expo" in dirpath:
            continue
        for filename in filenames:
            if filename.endswith((".py", ".ts", ".tsx", ".json", ".csv", ".md", ".txt")):
                path = os.path.join(dirpath, filename)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        for p in patterns:
                            if p in content:
                                print(f"Found '{p}' in {path}")
                except Exception:
                    pass

if __name__ == "__main__":
    search()
