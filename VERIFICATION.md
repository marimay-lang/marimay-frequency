# Historical local D101 verification — 2026-09-08

This translates the original local record; it does not report a new run.

3 source tests passed with `mmay test . --engine both`. Acceptance covered
26 exact status/stdout/stderr scenarios in VM, Native Debug and Native
Release (denied builds used VM and Native Release), plus 3 closed pipes.
Cases include Unicode, CRLF, final lines, limits, errors, symlinks, capability
denial and 2097152-byte input. Frequency/logstats additionally cover 4096
distinct keys. Input files remained unchanged.

| Scenario | Native Release | VM |
|---|---:|---:|
| 2 MiB, median of 3 runs | 31.23 ms | 270.29 ms |
| 20 MiB, one run | 269.86 ms | 934.07 ms |
| Peak RSS at 20 MiB | 37.14 MiB | 50.19 MiB |

Repeated test-both cycle: 339.33 ms. The first native execution immediately
after build was **385.38 ms**, above the fixed 100 ms budget; subsequent
executions met it. Control C17 programs without Marimay spent 370–512 ms before
main, but the exact startup subsystem responsible was not established.
First-execution performance acceptance remained blocked. Budgets, data and
macOS security settings were unchanged.

The host was macOS arm64, Release compiler with D101, managed heap 32 MiB,
with sequential measurements after compiler verification and ordinary desktop
background applications. This was not a disk-cold/fully idle-host study or
Tier 1-complete evidence. The 2 MiB medians do not characterize every format
or key distribution.

Reports: `build/acceptance/report.json` and `build/measure-1788863919106864000/report.json`.
Snapshots/hashes were also recorded in the language repository under
`docs/implementation/evidence/cp42-file-lines-2026-09-08.json`.
Compiler SHA-256: `076f9fce9bec61bb1fc7e4cf54934311a893246dcdd230c830c9b62111bcaf9c`.
Native SHA-256: `85bb5b75c4afbb131f1ef6e3726b167b99bcf177c6f66869b391195e3910ebe4`.
Other open gates are listed in `ERGONOMICS.md` and the CP42 portfolio.
