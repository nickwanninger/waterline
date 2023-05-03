import waterline as wl
import waterline.suites
import waterline.utils
import waterline.pipeline
from pathlib import Path
import pandas as pd


space = wl.Workspace("ws")


# space.add_suite(wl.suites.NAS, enable_openmp=False, suite_class="A")
# space.add_suite(wl.suites.GAP, enable_exceptions=False, enable_openmp=False)
# space.add_suite(wl.suites.PolyBench, size="SMALL")
# space.add_suite(wl.suites.MiBench)
# space.add_suite(wl.suites.SPEC2017, tar="/home/nick/SPEC2017.tar.gz", config="test")
space.add_suite(wl.suites.Embench, iters=10000)
# space.add_suite(wl.suites.Stockfish)

space.prepare()

pl = waterline.pipeline.Pipeline("optimized")
pl.add_stage(waterline.pipeline.OptStage(["-O3"]), name="Apply O3")
space.add_pipeline(pl)


results = space.run(runs=1)
results.reset_index(drop=True, inplace=True)
print(results)
results.to_csv("out.csv", index=False)
