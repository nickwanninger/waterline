import waterline as wl
import waterline.suites
import waterline.utils
import waterline.pipeline
from pathlib import Path

import time


space = wl.Workspace("ws")

space.add_suite(wl.suites.NAS, enable_openmp=True, suite_class="B")
space.add_suite(wl.suites.GAP)
space.add_suite(wl.suites.PolyBench)
space.add_suite(wl.suites.MiBench)
# space.add_suite(wl.suites.SPEC2017, tar="/home/nick/SPEC2017.tar.gz")

# run a baseline pipeline on the suites. This will produce a
# binary in each of their directories called 'baseline'
space.run_pipeline(waterline.pipeline.Pipeline("baseline"))

# space.prepare()

# space.run()


# exit()
exit()


def opt(*passes):
    def _internal(bitcode):
        space.shell("opt", bitcode, "-o", bitcode, *passes)

    return _internal


def disassemble(bitcode):
    space.shell("llvm-dis", bitcode)
    pass


def my_stage(bitcode):
    print(bitcode)

pl = waterline.pipeline.Pipeline("optimized")


pl.add_stage(opt("-O3"), name="Apply O3")
pl.add_stage(opt("-mem2reg"), name="Apply mem2reg")
pl.add_stage(opt("-lcssa"), name="Apply LCSSA")
pl.add_stage(my_stage)
pl.add_stage(disassemble)

space.run_pipeline(pl)
