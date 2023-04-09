import waterline as wl
import waterline.suites
import waterline.utils
import waterline.pipeline
from pathlib import Path
import time


space = wl.Workspace("ws")

space.add_suite(wl.suites.NAS, enable_openmp=True, suite_class="W")
space.add_suite(wl.suites.GAP)
space.add_suite(wl.suites.PolyBench)
space.add_suite(wl.suites.MiBench)
space.add_suite(wl.suites.SPEC2017, tar="/home/nick/SPEC2017.tar.gz")


def opt(*passes):
    def _internal(bitcode):
        space.shell("opt", bitcode, "-o", bitcode, *passes)

    return _internal


pl = waterline.pipeline.Pipeline("optimized")

pl.add_stage(opt("-O3"), name="Apply O3")
# pl.add_stage(opt("-mem2reg"), name="Apply mem2reg")
# pl.add_stage(opt("-lcssa"), name="Apply LCSSA")

space.add_pipeline(pl)


class SizeRunner(waterline.Runner):
    def run(
        self,
        workspace: waterline.Workspace,
        config: waterline.RunConfiguration,
        binary: Path,
    ):
        return binary.stat().st_size


space.run(runs=1, runner=SizeRunner())
