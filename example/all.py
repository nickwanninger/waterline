import waterline as wl
import waterline.suites as suites
import waterline.utils
import waterline.pipeline
from waterline.run import Runner

from pathlib import Path
import pandas as pd
import subprocess
import os

perf_stats = [
    "instructions",
    "cycles",
    "duration_time",
    "cache-misses",
    "cache-references",

    "L1-dcache-prefetches",
    "L1-dcache-loads",
    "L1-dcache-load-misses",

    # "L1-dcache-load-misses",
    # "L1-dcache-loads",
    # "L1-dcache-stores",
    # "L1-icache-load-misses",
    # "LLC-load-misses",
    # "LLC-loads",
    # "LLC-store-misses",
    # "LLC-stores",
    "branch-instructions",
    "branch-misses",
]

class PerfRunner(Runner):
    def run(self, workspace, config, binary):
        cwd = os.getcwd() if config.cwd is None else config.cwd
        print("running cd", cwd, "&&", binary, *config.args)
        with waterline.utils.cd(cwd):
            proc = subprocess.Popen(
                ['perf', 'stat', '-e', ','.join(perf_stats), '-x', ',', '-o', f'{binary}.perf.csv', binary, *config.args],
                stdout=subprocess.DEVNULL,
                # stderr=subprocess.DEVNULL,
                env=config.env,
                cwd=cwd,
            )
            proc.wait()


        df = pd.read_csv(f'{binary}.perf.csv', comment='#', header=None)
        out = {}
        for val, name in zip(df[0], df[2]):
            out[name] = val
        # print(out)
        return out


space = wl.Workspace("ws")

space.add_suite(suites.NAS, enable_openmp=False, suite_class="W")
# space.add_suite(suites.GAP, enable_exceptions=False, enable_openmp=False)
# space.add_suite(suites.PolyBench, size="SMALL")
# space.add_suite(suites.MiBench)
# space.add_suite(suites.SPEC2017, tar="/home/nick/SPEC2017.tar.gz", config="test",
#                 disabled=[600, 602, 620, 623, 625, 631, 641, 657, 619, 638, 644])
# space.add_suite(suites.Embench, iters=100)
# space.add_suite(suites.Stockfish)
# space.add_suite(suites.SqliteTPCH)

space.prepare()

pl = waterline.pipeline.Pipeline("optimized")
pl.add_stage(waterline.pipeline.OptStage(["-O3"]), name="Apply O3")
space.add_pipeline(pl)


results = space.run(run_name="myrun", runner=PerfRunner(), runs=3)
# results.reset_index(drop=True, inplace=True)
# print(results)
# results.to_csv("out.csv", index=False)
