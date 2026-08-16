import json
import os
from explore_commit import run

REPO_DIR = "click"

instances = [
    {
        "issue_number": 3487,
        "fix_commit": "a5f5aa6",
        "problem_statement": "Echoing an empty bytes or bytearray object with click.echo() raises a TypeError instead of writing nothing.",
    },
    {
        "issue_number": 3449,
        "fix_commit": "5ee8e31",
        "problem_statement": "Using echo_via_pager together with CliRunner's output capture raises an I/O operation on closed file error.",
    },
    {
        "issue_number": 2995,
        "fix_commit": "701b313",
        "problem_statement": "Fish shell autocompletion breaks when a command-line argument contains quoted or escaped characters.",
    },
]

dataset = []

for inst in instances:
    fix_commit = inst["fix_commit"]
    base_commit = fix_commit + "^1"

    changed_files = run(["git", "diff", "--name-only", base_commit, fix_commit]).strip().splitlines()

    dataset.append({
        "issue_number": inst["issue_number"],
        "problem_statement": inst["problem_statement"],
        "fix_commit": fix_commit,
        "changed_files": changed_files,
    })

    print(f"Issue #{inst['issue_number']}: {changed_files}")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "..", "data", "mini_swebench.json")

with open(OUTPUT_PATH, "w") as f:
    json.dump(dataset, f, indent=2)

print(f"\nSaved {len(dataset)} instances to {OUTPUT_PATH}")