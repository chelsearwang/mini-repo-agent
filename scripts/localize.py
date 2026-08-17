import json
import os
import re
import subprocess
from rank_bm25 import BM25Okapi

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "..", "data", "mini_swebench.json")

def run(cmd, repo_dir):
    result = subprocess.run(cmd, cwd=repo_dir, capture_output=True, text=True)
    return result.stdout

def tokenize(text):
    return re.findall(r"[a-zA-Z_]+", text.lower())

def list_source_files(repo_dir, commit):
    # All .py files at a given commit, excluding tests
    out = run(["git", "ls-tree", "-r", "--name-only", commit], repo_dir)
    return [f for f in out.splitlines() if f.endswith(".py") and "test" not in f.lower()]

def get_file_content(repo_dir, commit, path):
    # reads one file's full content at the commit
    return run(["git", "show", f"{commit}:{path}"], repo_dir)

def localize(instance):
    repo_dir = os.path.join(SCRIPT_DIR, "..", instance["repo"])
    base_commit = instance["fix_commit"] + "^1"

    files = list_source_files(repo_dir, base_commit)
    # build list by running once per itme
    corpus = [tokenize(get_file_content(repo_dir, base_commit, f)) for f in files]

    bm25 = BM25Okapi(corpus)
    query = tokenize(instance["problem_statement"])
    scores = bm25.get_scores(query)

    ranked = sorted(zip(files, scores), key=lambda x: -x[1])
    top5 = [f for f, s in ranked[:5]]

    gold = [f for f in instance["changed_files"] if f.endswith(".py") and "test" not in f.lower()]
    top1_hit = len(gold) > 0 and ranked[0][0] in gold
    top5_hit = any(g in top5 for g in gold)

    return {
        "issue": instance["issue_number"],
        "repo": instance["repo"],
        "gold_files": gold,
        "top5_predicted": top5,
        "top1_hit": top1_hit,
        "top5_hit": top5_hit,
    }

if __name__ == "__main__":
    with open(DATA_PATH) as f:
        dataset = json.load(f)

    # run localize once per instance
    results = [localize(inst) for inst in dataset]

    for r in results:
        mark1 = "✓" if r["top1_hit"] else "✗"
        mark5 = "✓" if r["top5_hit"] else "✗"
        print(f"#{r['issue']} ({r['repo']}): top1={mark1} top5={mark5} | gold={r['gold_files']} | top5_pred={r['top5_predicted']}")

    top1_acc = sum(r["top1_hit"] for r in results) / len(results)
    top5_acc = sum(r["top5_hit"] for r in results) / len(results)
    print(f"\nTop-1 accuracy: {top1_acc:.0%} ({sum(r['top1_hit'] for r in results)}/{len(results)})")
    print(f"Top-5 accuracy: {top5_acc:.0%} ({sum(r['top5_hit'] for r in results)}/{len(results)})")

    RESULTS_PATH = os.path.join(SCRIPT_DIR, "..", "data", "localization_results.json")
    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)