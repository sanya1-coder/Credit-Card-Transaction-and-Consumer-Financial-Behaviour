# Milestone Feedback

Project: P19 - Credit-card transaction and consumer financial behaviour
Repo: `sanya1-coder/Credit-Card-Transaction-and-Consumer-Financial-Behaviour`
Official milestone score after post-lock recovery: 5.5/20
Post-lock sanity-check score: 11/20
Band: `not_milestone_ready`
Reviewed at: 2026-05-10T09:29:31

This is the official milestone feedback after applying the post-lock recovery policy. The locked May 6 snapshot remains the baseline, but real, reproducible fixes made after lock can recover 50% of the lost milestone points.

## Score Recovery Applied

- Locked milestone score: 0/20
- Post-lock sanity-check score: 11/20
- Official milestone score: 5.5/20
- Formula: locked score + 50% of the post-lock improvement

## Rubric Breakdown

- Charter lock: 1/4. the charter is not recorded as approved; charter file exists and is not obviously template; the milestone manifest does not confirm charter lock
- Source access proof: 2/4. some data/probe evidence was found, but the manifest source list is incomplete
- Baseline before sophistication: 4/4. `outputs/baseline_metric.json` is readable and contains a real metric/value
- Reproducible dry run: 0/4. `uv run main.py` fails from a fresh copy of the repo
- Metric schema readiness: 4/4. `outputs/primary_metric.json` is readable and machine-checkable

## Policy Notes

- post-lock recovery policy applied: locked score 0/20; post-lock sanity check 11/20; official score = 0 + 50% of (11 - 0) = 5.5/20

## What To Fix Next

- Make the charter unambiguous: final question, dataset, primary metric, baseline, scope limits, and team roles should all be visible in `CHARTER.md`.
- Make source access easy to verify: include a probe file or script, list the source in `outputs/milestone_manifest.json`, and commit a small permitted fallback if the full source is too large/private.
- Make `uv run main.py` work from a fresh clone. If the full data is large, the script should still run on a committed sample or a clearly reproducible download path.

## Reproducibility Error Observed

The reviewer ran `uv run main.py` from a fresh copy of the repo. The relevant tail of the error was:

```text
    ...<6 lines>...
        storage_options=self.options.get("storage_options", None),
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/private/var/folders/t6/gytrx5s95txg4g8vkt7rnb980000gn/T/eco6810-milestone-P19-_tz21w0i/repo/.venv/lib/python3.14/site-packages/pandas/io/common.py", line 926, in get_handle
    handle = open(
        handle,
    ...<3 lines>...
        newline="",
    )
FileNotFoundError: [Errno 2] No such file or directory: 'archive/sd254_users.csv'
```

## Final Phase Guidance

- First priority: make the project reproducible from a fresh clone with `uv run main.py`. Do this before adding more modeling complexity.
- Make the data path boring and reliable: source proof, fallback/sample data, and README instructions should agree.
- This needs urgent repair. A simple, reproducible, well-explained project will score better than an ambitious project that cannot be run or verified.
- For the final submission, keep the repo as the source of truth: `README.md`, `CHARTER.md`, `main.py`, `outputs/`, `report.md`, and `AI_USAGE_LOG.md` should tell one consistent story.

Please treat this feedback as a way to make the final week calmer, not as a ceiling on the final project. A clear, reproducible, honestly interpreted final submission can still be strong.
