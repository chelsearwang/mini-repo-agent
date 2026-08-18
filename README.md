# Mini Issue-to-Patch Agent

This is a small project I built to learn more about how AI agents fix real
bugs in codebases — specifically two steps: **finding which file a bug is
in** (localization), and **writing an actual fix** (patch generation). I
tested it on real bugs from three open-source Python projects: `click`,
`flask`, and `requests`.

## The data

10 real bugs, straight from each project's git history — the commit
right before the fix, the commit with the fix, and which files actually
changed. Because I couldn't use the standard SWE-bench dataset due to Hugging Face connectivity issues, I constructed a small custom dataset by identifying real bug fixes from project histories and tracing each to the corresponding pre-fix and fix commits. The "bug report" text for each one is based on the
changelog description.

## Localization

I used BM25 (a keyword-based search algorithm, kind of like a simpler
version of a search engine) to rank every source file in the codebase
against the bug report text, and checked whether the file that actually got
changed showed up near the top.

**Results (10 bugs): got it right 40% of the time as my #1 guess, 90% of
the time somewhere in my top 5 guesses.**

Failure worth noting: issue #3449's real bug was in `_termui_impl.py`, but
my search's top guess was `_compat.py` instead. My best explanation: the bug
report mentions an "I/O operation on closed file" error, and `_compat.py`
happens to contain an unrelated class (`_AtomicFile`) with its own `.closed`
attribute and `close()` method — so the search likely matched on the shared
word "closed," even though that code has nothing to do with the actual bug.

## Patch Generation

For 5 of bugs, I fed the localized file + bug report to an
LLM (Gemini 3.6 Flash) and asked for a patch as a diff, then compared
against the real historical fix by hand.

| Issue | Right file? | Was the patch actually correct? |
|---|---|---|
| #3487 | Yes | Yes — basically the same fix |
| #2995 | Yes | **No** — found the right file, but the fix didn't actually solve the bug |
| #1841 | No | No — confidently edited the wrong code |
| #3449 | No | No — same thing |
| #7309 | No | Unclear — see below |

### Observation: Correct patches from incorrect context

Issue #7309 produced an unexpected result. I provided the model with an incorrectly localized file, but its generated patch targeted a different file that I had never included in the prompt — and that file happened to match the actual historical fix.

One possible explanation is that the model had prior exposure to information about this bug or its historical fix during pretraining, rather than deriving the fix solely from the repository context I provided.

However, this experiment cannot establish that explanation. I did not test whether the bug or fix appeared in the model's training data, so training-data exposure remains a hypothesis.

## Limitations

- Only 10 bugs for localization and 5 for patch generation — small sample,
  not meant to prove anything definitively
- I only searched whole files, not individual functions — a more
  fine-grained search would probably do better

## What I'd try next

- Search at the function level instead of the whole file
- Add more bugs, maybe from smaller/less-famous repos, just in case the model already knows the answer from bigger/common ones
- Actually run the tests to check if a patch works, instead of just reading
  it myself
