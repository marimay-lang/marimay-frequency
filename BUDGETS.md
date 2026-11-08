# Budgets defined before measurement

Local CLI0, macOS arm64; Release compiler and Native Release application.
The small input is `fixtures/sample.txt`. `stream-2m-v1` has 16384 lines of
128 bytes, exactly 2097152 bytes. Grep searches for an absent substring;
frequency counts a repeated line; logstats counts INFO and one event.
`tools/acceptance.py` generates synthetic inputs without reading user values.

- Small first and repeated native execution: ≤100 ms; `mmay run`: ≤500 ms.
- Repeated `mmay test . --engine both`: ≤2 s with a ready native cache.
- Large input: native ≤2 s, VM ≤20 s, including process startup.
- `stream-20m-v1`: 163840 of the same lines (20 MiB), native ≤20 s, VM ≤200 s,
  with the same unique-key count. This additional growth check retains the
  original 2 MiB budget.
- Peak RSS: native ≤128 MiB, VM ≤256 MiB.
- Streaming acceptance also runs with a 32 MiB managed heap, separately from
  RSS. For growth checks, repeat the same input ten times with unchanged
  unique-key count and the same memory limits.

Initial measurements are stored separately from functional acceptance. These
budgets do not close CP42/Tier 1. The first execution after build is not warmed
in advance. A miss blocks the affected acceptance rather than changing its
budget.
