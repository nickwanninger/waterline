import waterline as wl
import waterline.suites
import waterline.utils
import waterline.pipeline
from pathlib import Path
import time
from typing import List


space = wl.Workspace("ws")

# space.add_suite(wl.suites.NAS, enable_openmp=True, suite_class="A")
# space.add_suite(wl.suites.GAP)
# space.add_suite(wl.suites.PolyBench, size="SMALL")
space.add_suite(wl.suites.MiBench)
# space.add_suite(wl.suites.SPEC2017, tar="/home/nick/SPEC2017.tar.gz")


pl = waterline.pipeline.Pipeline("optimized")
pl.add_stage(waterline.pipeline.OptStage(["-O3"]), name="Apply O3")
space.add_pipeline(pl)


class SizeRunner(waterline.Runner):
    def run(
        self,
        workspace: waterline.Workspace,
        config: waterline.RunConfiguration,
        binary: Path,
    ):
        return binary.stat().st_size


# space.run(runs=1, runner=SizeRunner())
space.run(runs=1)
