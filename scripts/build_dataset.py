import json
import os
from explore_commit import run

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "..", "data", "mini_swebench.json")

instances = [
    {
        "issue_number": 3487,
        "repo": "click",
        "fix_commit": "a5f5aa6",
        "problem_statement": "Echoing an empty bytes or bytearray object with click.echo() raises a TypeError instead of writing nothing.",
    },
    {
        "issue_number": 3449,
        "repo": "click",
        "fix_commit": "5ee8e31",
        "problem_statement": "Using echo_via_pager together with CliRunner's output capture raises an I/O operation on closed file error.",
    },
    {
        "issue_number": 2995,
        "repo": "click",
        "fix_commit": "701b313",
        "problem_statement": "Fish shell autocompletion breaks when a command-line argument contains quoted or escaped characters.",
    },
    {
        "issue_number": 6096,
        "repo": "flask",
        "fix_commit": "05e9c6bd",
        "problem_statement": "Parsing a host header containing an IPv6 address fails because the code incorrectly uses partition(':') to split out the port, which breaks on the colons inside the IPv6 address itself.",
    },
    {
        "issue_number": 2374,
        "repo": "flask",
        "fix_commit": "d625d411",
        "problem_statement": "jsonify() incorrectly encodes datetime objects that are timezone-aware but not in UTC, producing the wrong timestamp in the JSON output.",
    },
    {
        "issue_number": 1841,
        "repo": "flask",
        "fix_commit": "6e46d0cd",
        "problem_statement": "Flask fails to import or run correctly under PyPy3 due to a compatibility issue in how string/bytes types are handled.",
    },
    {
        "issue_number": 2731,
        "repo": "flask",
        "fix_commit": "27d56c1d",
        "problem_statement": "When a blueprint's url_prefix and a route's rule both have slashes at the boundary, Flask doesn't correctly merge them, resulting in incorrect or duplicate slashes in the final URL.",
    },
    {
        "issue_number": 7309,
        "repo": "requests",
        "fix_commit": "f0198e6d",
        "problem_statement": "When parsing a Content-Type header that contains a malformed parameter (one with no '=' sign), the parser stores a boolean True as that parameter's value instead of a string, which can cause type errors in code that expects all header parameter values to be strings.",
    },
    {
        "issue_number": 6628,
        "repo": "requests",
        "fix_commit": "3ff3ff21",
        "problem_statement": "When a JSONDecodeError exception is raised inside a multiprocessing worker, attempting to pass it back to the main process via pickling fails, crashing the entire process pool instead of just reporting the JSON parsing error.",
    },
    {
        "issue_number": 5274,
        "repo": "requests",
        "fix_commit": "6fbfca90",
        "problem_statement": "When a request manually specifies a Host header, the underlying HTTP connection still adds its own automatic Host header on top of it, resulting in two Host headers being sent in the same request, which some servers reject or handle incorrectly.",
    },
]

dataset = []

for inst in instances:
    repo_dir = os.path.join(SCRIPT_DIR, "..", inst["repo"])
    fix_commit = inst["fix_commit"]
    base_commit = fix_commit + "^1"

    changed_files = run(["git", "diff", "--name-only", base_commit, fix_commit], repo_dir).strip().splitlines()

    dataset.append({
        "issue_number": inst["issue_number"],
        "repo": inst["repo"],
        "problem_statement": inst["problem_statement"],
        "fix_commit": fix_commit,
        "changed_files": changed_files,
    })

    print(f"Issue #{inst['issue_number']} ({inst['repo']}): {changed_files}")

with open(OUTPUT_PATH, "w") as f:
    json.dump(dataset, f, indent=2)

print(f"\nSaved {len(dataset)} instances to {OUTPUT_PATH}")