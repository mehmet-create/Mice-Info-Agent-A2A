import os

# Folders or files to ignore
IGNORE = {"__pycache__", ".git", ".venv", "env", "venv", "migrations", ".idea", ".vscode"}

def print_tree(start_path=".", prefix=""):
    entries = [e for e in os.listdir(start_path) if e not in IGNORE]
    entries.sort()

    for i, entry in enumerate(entries):
        path = os.path.join(start_path, entry)
        connector = "└── " if i == len(entries) - 1 else "├── "
        print(prefix + connector + entry)

        if os.path.isdir(path):
            extension = "    " if i == len(entries) - 1 else "│   "
            print_tree(path, prefix + extension)

if __name__ == "__main__":
    print_tree(".")
