import waterline as wl
import waterline.suites as suites
import waterline.utils
import waterline.pipeline
from pathlib import Path
import pandas as pd


space = wl.Workspace("ws")

# space.add_suite(suites.NAS, enable_openmp=False, suite_class="W")
# space.add_suite(suites.GAP, enable_exceptions=False, enable_openmp=False)
# space.add_suite(suites.PolyBench, size="SMALL")
# space.add_suite(suites.MiBench)
space.add_suite(suites.SPEC2017, tar="/home/nick/SPEC2017.tar.gz", config="ref")
# space.add_suite(suites.Embench, iters=100)
# space.add_suite(suites.Stockfish)
# space.add_suite(suites.SqliteTPCH)

space.prepare()

# pl = waterline.pipeline.Pipeline("optimized")
# pl.add_stage(waterline.pipeline.OptStage(["-O3"]), name="Apply O3")
# space.add_pipeline(pl)


results = space.run(runs=1)
results.reset_index(drop=True, inplace=True)
print(results)
results.to_csv("out.csv", index=False)
