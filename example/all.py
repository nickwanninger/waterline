import waterline as wl
import waterline.suites
import waterline.utils
import waterline.pipeline
from pathlib import Path
import time
from typing import List



class MyLinker(wl.Linker):
    libs = []
    command = 'clang++'


space = wl.Workspace("ws")


# space.add_suite(wl.suites.NAS, enable_openmp=True, suite_class="S")
# space.add_suite(wl.suites.GAP)
# space.add_suite(wl.suites.PolyBench, size="LARGE")
# space.add_suite(wl.suites.MiBench)
# space.add_suite(wl.suites.SPEC2017, tar="/home/nick/SPEC2017.tar.gz")
space.add_suite(wl.suites.Embench)

space.prepare()

pl = waterline.pipeline.Pipeline("optimized")
pl.set_linker(MyLinker())
pl.add_stage(waterline.pipeline.OptStage(["-O3"]), name="Apply O3")
space.add_pipeline(pl)


space.run(runs=1)
