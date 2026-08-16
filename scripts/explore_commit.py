import subprocess
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.join(SCRIPT_DIR, "..", "click")

def run(cmd, repo_dir):
    result = subprocess.run(cmd, cwd=repo_dir, capture_output=True, text=True)
    return result.stdout

def get_changed_files(base_commit, fix_commit, repo_dir):
    output = run(["git", "diff", "--name-only", base_commit, fix_commit], repo_dir)
    return output.strip().splitlines()

if __name__ == "__main__":
    commit = "a5f5aa6"
    parent = commit + "^1"

    changed = get_changed_files(parent, commit)
    print("Files changed in this commit:")
    for f in changed:
        print(" -", f)