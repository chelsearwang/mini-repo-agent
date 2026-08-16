import subprocess
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.join(SCRIPT_DIR, "..", "click")

def run(cmd):
    """Run a shell command inside the click repo, and return its text output."""
    result = subprocess.run(cmd, cwd=REPO_DIR, capture_output=True, text=True)
    return result.stdout

def get_changed_files(base_commit, fix_commit):
    """Return the list of files that changed between two commits."""
    output = run(["git", "diff", "--name-only", base_commit, fix_commit])
    files = output.strip().splitlines()
    return files

if __name__ == "__main__":
    commit = "a5f5aa6"
    parent = commit + "^1"

    changed = get_changed_files(parent, commit)
    print("Files changed in this commit:")
    for f in changed:
        print(" -", f)