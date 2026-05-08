# Milestone Feedback

Project: P19 - Credit-card transaction and consumer financial behaviour
Repo: `sanya1-coder/Credit-Card-Transaction-and-Consumer-Financial-Behaviour`
Milestone score locked: 0/20
Raw score before policy caps: 0/20
Band: `not_milestone_ready`
Reviewed at: 2026-05-09T01:59:19

This is the locked milestone evaluation for the May 6 milestone. The score is based on the latest repository snapshot available to the instructor review workflow when this feedback was generated.

## Rubric Breakdown

- Charter lock: 0/4. the charter is not recorded as approved; no `CHARTER.md` file was found; the milestone manifest does not confirm charter lock
- Source access proof: 0/4. no usable source/probe evidence was found
- Baseline before sophistication: 0/4. `outputs/baseline_metric.json` is missing
- Reproducible dry run: 0/4. `uv run main.py` fails from a fresh copy of the repo
- Metric schema readiness: 0/4. `outputs/primary_metric.json` is missing

## What To Fix Next

- Make the charter unambiguous: final question, dataset, primary metric, baseline, scope limits, and team roles should all be visible in `CHARTER.md`.
- Make source access easy to verify: include a probe file or script, list the source in `outputs/milestone_manifest.json`, and commit a small permitted fallback if the full source is too large/private.
- Keep a simple baseline first. `outputs/baseline_metric.json` should contain a real metric name and value, not template text.
- Make `uv run main.py` work from a fresh clone. If the full data is large, the script should still run on a committed sample or a clearly reproducible download path.
- `outputs/primary_metric.json` should be machine-checkable: include `metric_name`, `value`, `threshold`, and `passed`.

## Reproducibility Error Observed

The reviewer ran `uv run main.py` from a fresh copy of the repo. The relevant tail of the error was:

```text
error: Failed to spawn: `main.py`
  Caused by: No such file or directory (os error 2)
```

## Final Phase Guidance

- First priority: make the project reproducible from a fresh clone with `uv run main.py`. Do this before adding more modeling complexity.
- Second priority: make the final metric parseable in `outputs/primary_metric.json` with a value, threshold, and pass/fail status.
- Make the data path boring and reliable: source proof, fallback/sample data, and README instructions should agree.
- This needs urgent repair. A simple, reproducible, well-explained project will score better than an ambitious project that cannot be run or verified.
- For the final submission, keep the repo as the source of truth: `README.md`, `CHARTER.md`, `main.py`, `outputs/`, `report.md`, and `AI_USAGE_LOG.md` should tell one consistent story.

Please treat this feedback as a way to make the final week calmer, not as a ceiling on the final project. A clear, reproducible, honestly interpreted final submission can still be strong.
