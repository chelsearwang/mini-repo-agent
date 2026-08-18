import json
import os
import subprocess
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "..", "data", "mini_swebench.json")
LOC_PATH = os.path.join(SCRIPT_DIR, "..", "data", "localization_results.json")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "..", "data", "patch_results.json")

SELECTED_ISSUES = [3487, 2995, 1841, 7309, 3449]

def run(cmd, repo_dir):
    return subprocess.run(cmd, cwd=repo_dir, capture_output=True, text=True).stdout

def get_file_content(repo_dir, commit, path):
    return run(["git", "show", f"{commit}:{path}"], repo_dir)

def get_gold_diff(repo_dir, base_commit, fix_commit, files):
    return run(["git", "diff", base_commit, fix_commit, "--"] + files, repo_dir)

with open(DATA_PATH) as f:
    dataset = {d["issue_number"]: d for d in json.load(f)}

with open(LOC_PATH) as f:
    loc_results = {r["issue"]: r for r in json.load(f)}

results = []

for issue in SELECTED_ISSUES:
    inst = dataset[issue]
    loc = loc_results[issue]
    repo_dir = os.path.join(SCRIPT_DIR, "..", inst["repo"])
    base_commit = inst["fix_commit"] + "^1"
    top1_file = loc["top5_predicted"][0]

    file_content = get_file_content(repo_dir, base_commit, top1_file)
    gold_diff = get_gold_diff(repo_dir, base_commit, inst["fix_commit"], inst["changed_files"])

    prompt = f"""You are fixing a bug in a Python codebase.

Bug report:
{inst['problem_statement']}

Current content of {top1_file}:
```python
{file_content}
```

Write a patch that fixes this bug, as a unified diff. Only output the diff, nothing else."""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )
    generated_patch = response.text

    print(f"\n{'='*60}")
    print(f"Issue #{issue} ({inst['repo']}) — localized file: {top1_file} (top1_hit={loc['top1_hit']})")
    print(f"{'='*60}")
    print("--- GENERATED PATCH ---")
    print(generated_patch)
    print("--- GOLD (REAL) PATCH ---")
    print(gold_diff)

    results.append({
        "issue": issue,
        "repo": inst["repo"],
        "localized_file": top1_file,
        "top1_hit": loc["top1_hit"],
        "generated_patch": generated_patch,
        "gold_diff": gold_diff,
    })

with open(OUTPUT_PATH, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nSaved {len(results)} patch results to {OUTPUT_PATH}")