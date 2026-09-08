#!/usr/bin/env python3
"""Sequential named workload measurements; functional oracles remain explicit."""
import hashlib
import json
from pathlib import Path
import platform
import re
import statistics
import subprocess
import time
from mmay_acceptance import Application
ROOT = Path(__file__).resolve().parents[1]
APP = Application(ROOT, timeout=240)
WORK = ROOT / "build" / ("measure-" + str(time.time_ns()))
WORK.mkdir(parents=True)
NAME = ROOT.name.removeprefix("marimay-")
row = b"INFO\t"+b"x"*122+b"\n" if NAME == "logstats" else b"x"*127+b"\n"
small = ROOT / "fixtures/sample.txt"
large = WORK / "stream-2m-v1.txt"
extended = WORK / "stream-20m-v1.txt"
large.write_bytes(row*16384)
extended.write_bytes(row*163840)
flags = ["--allow-read", str(ROOT), "--max-heap-bytes", "33554432"]
binary = WORK / "app-release"
APP.successful([APP.compiler,"build",".",*flags,"--release","--output",str(binary)])
engines = {"native":[str(binary)], "vm":[APP.compiler,"run",".",*flags,"--"]}
records = []

def encode(value): return json.dumps(value,ensure_ascii=False,separators=(",", ":")).encode()+b"\n"
def expectation(file, multiplier):
    if NAME == "grep":
        return (["Привет" if multiplier == 0 else "absent",str(file)],
                0 if multiplier == 0 else 1,
                (str(file)+":2:Привет 🌿\n").encode() if multiplier == 0 else b"")
    if NAME == "frequency":
        rows = [("б",2),("а",1),("🌿",1)] if multiplier == 0 else [("x"*127,16384*multiplier)]
        return (["count",str(file)],0,b"".join(encode({"value":v,"count":n}) for v,n in rows))
    count = 3 if multiplier == 0 else 16384*multiplier
    levels = [0,1,1,1] if multiplier == 0 else [0,count,0,0]
    events = [("старт",2),("🌿",1)] if multiplier == 0 else [("x"*122,count)]
    return ([str(file)],0,encode({"lines":count,"levels":dict(zip(["debug","info","warn","error"],levels)),
                                "events":[{"event":v,"count":n} for v,n in events]}))

def measured(name, command, expected_status, expected_output, budget, metadata):
    timing = ["/usr/bin/time", "-l" if platform.system() == "Darwin" else "-v"] if platform.system() in ("Darwin","Linux") else []
    start = time.monotonic()
    result = APP.run([*timing,*command])
    elapsed = time.monotonic()-start
    assert result.returncode == expected_status and result.stdout == expected_output, (name,result)
    if platform.system() == "Darwin":
        rss = re.search(rb"^\s*(\d+)\s+maximum resident set size\s*$",result.stderr,re.M)
        rss_bytes = int(rss[1]) if rss else None
    elif platform.system() == "Linux":
        rss = re.search(rb"Maximum resident set size \(kbytes\):\s*(\d+)",result.stderr)
        rss_bytes = int(rss[1])*1024 if rss else None
    else: rss_bytes = None
    records.append({"name":name,"command":command,"seconds":elapsed,"rss_bytes":rss_bytes,"status":result.returncode,
                    "stdout_sha256":hashlib.sha256(result.stdout).hexdigest(),"timing_stderr":result.stderr.decode(),
                    "seconds_budget":budget,"within_time_budget":elapsed<=budget,**metadata})
    print(name,round(elapsed,4),rss_bytes,flush=True)

# First native execution follows build directly; no user code is run to warm it.
for engine,prefix in engines.items():
    for repetition in range(4):
        args,status,out=expectation(small,0)
        measured(engine+"-small",[*prefix,*args],status,out,0.1 if engine=="native" else 0.5,
                 {"first":repetition==0,"dataset_sha256":hashlib.sha256(small.read_bytes()).hexdigest()})
for multiplier,file in [(1,large),(10,extended)]:
    for engine,prefix in engines.items():
        for repetition in range(3 if multiplier==1 else 1):
            args,status,out=expectation(file,multiplier)
            measured(engine+("-2m" if multiplier==1 else "-20m"),[*prefix,*args],status,out,
                     (2 if engine=="native" else 20)*multiplier,
                     {"dataset":file.name,"bytes":file.stat().st_size,"dataset_sha256":hashlib.sha256(file.read_bytes()).hexdigest(),
                      "rss_budget":134217728 if engine=="native" else 268435456})
# Populate the test cache, then measure one ordinary repeated source-test cycle.
APP.successful([APP.compiler,"test",".","--engine","both"])
start=time.monotonic();output=APP.successful([APP.compiler,"test",".","--engine","both"])
test_seconds=time.monotonic()-start
sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
         for p in sorted(ROOT.glob("*.my"))}
report={"schema":ROOT.name+".measurements/1","host":platform.platform(),"harness":APP.metadata(engines),
        "sources":sources,"budgets_sha256":hashlib.sha256((ROOT/"BUDGETS.md").read_bytes()).hexdigest(),
        "conditions":"Sequential processes after compiler verification; normal desktop background, no forced OS cache eviction. First sample follows build; not a disk-cold or fully idle-host claim.",
        "records":records,"test_both":{"seconds":test_seconds,"seconds_budget":2,"within_budget":test_seconds<=2,"stdout":output.decode()}}
(WORK / "report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
(ROOT/"build/latest-measurement.txt").write_text(str(WORK/"report.json")+"\n")
print("report:",WORK/"report.json")
