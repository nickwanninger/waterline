import shutil
import subprocess
from pathlib import Path

import waterline as wl
import waterline.suites
import waterline.pipeline

from waterline.pipeline import Stage, _should_run

# Alaska requires these canonicalization passes. The baseline also runs them.
CANONICALIZE = "mergereturn,break-crit-edges,loop-simplify,lcssa,indvars,mem2reg,instnamer"

# These undefined symbols require the Alaska runtime.
RUNTIME_SYMBOLS = ("alaska.HF", "halloc", "hcalloc", "hrealloc", "hfree", "alaska_barrier_poll")


class Alaska:
    """
    Find artifacts from Alaska tools/cross_compile.sh.
    """

    def __init__(self, root, build=None, plugin=None, translate=None):
        self.root = Path(root)
        self.build = Path(build) if build else self.root / "build-cross"

        self.plugin = Path(plugin or self.build / "local" / "lib" / "Alaska.so")
        self.translate = Path(translate or self.build / "translate.bc")

        self.validate()

    def validate(self):
        for name in ("plugin", "translate"):
            path = getattr(self, name)
            if not path.exists():
                raise FileNotFoundError(
                    f"alaska {name} not found at {path}. "
                    f"Run tools/cross_compile.sh from {self.root}."
                )

    def stage(self, **kwargs):
        return AlaskaStage(self, **kwargs)

    def baseline_stage(self):
        return AlaskaBaselineStage()


class AlaskaBaselineStage(Stage):
    """Run canonicalization for the Alaska baseline."""

    def run(self, input, output, benchmark):
        if not _should_run(input, output):
            return
        ws = benchmark.suite.workspace
        ws.shell("opt", str(input), "-o", str(output), f"-passes={CANONICALIZE}")
        ws.shell("llvm-dis", str(output))


class AlaskaStage(Stage):
    """Apply Alaska translation. Also apply any later -O3 to the baseline."""

    def __init__(self, alaska: Alaska, hoisting=True, escape=True, check=True):
        self.alaska = alaska
        self.hoisting = hoisting
        # alaska-escape translates pointers handed to external functions
        # (printf, memcpy, ...). Dropping it restricts translation to loads and
        # stores.
        self.escape = escape
        self.check = check

    def run(self, input, output, benchmark):
        if not _should_run(input, output):
            return

        ws = benchmark.suite.workspace
        plugin = self.alaska.plugin

        # Copy the input before the passes change the output in place.
        if input != output:
            shutil.copy(input, output)

        def run_passes(passes):
            ws.shell(
                "opt",
                f"--load-pass-plugin={plugin}",
                f"--passes={passes}",
                str(output),
                "-o",
                str(output),
            )

        ws.shell("opt", str(output), "-o", str(output), f"-passes={CANONICALIZE}")

        # Run opt once per pass, as the Alaska script does.
        run_passes("alaska-prepare")
        run_passes("alaska-translate" if self.hoisting else "alaska-translate-nohoist")
        if self.escape:
            run_passes("alaska-escape")
        # Make calls to @alaska_translate before llvm-link so
        # --only-needed includes the translation code.
        run_passes("alaska-lower")

        ws.shell(
            "llvm-link",
            str(output),
            "--only-needed",
            "--internalize",
            str(self.alaska.translate),
            "-o",
            str(output),
        )

        # alaska-inline inlines the translate calls; globaldce drops the now
        # dead internal definitions it was inlined from.
        run_passes("alaska-inline,globaldce")

        if self.check:
            self.check_no_runtime(ws, output, benchmark)

        ws.shell("llvm-dis", str(output))

    def check_no_runtime(self, ws, bitcode, benchmark):
        """Verify that undefined symbols do not require the Alaska runtime."""
        out = subprocess.run(
            ["llvm-nm", "--undefined-only", str(bitcode)],
            capture_output=True,
            text=True,
        )
        undefined = {line.split()[-1] for line in out.stdout.splitlines() if line.strip()}
        leaked = sorted(undefined.intersection(RUNTIME_SYMBOLS))
        if leaked:
            raise RuntimeError(
                f"alaska: {benchmark.suite.name}/{benchmark.name} references the alaska "
                f"runtime ({', '.join(leaked)}), which is not built for this target"
            )


target = wl.Target.riscv64gc("/opt/riscv", dynamic_linker="/lib/ld-linux-riscv64-lp64d.so.1")

space = wl.Workspace("bench-riscv", target=target)
# space.add_suite(wl.suites.NAS, enable_openmp=False, suite_class="W")
space.add_suite(wl.suites.GAP, enable_openmp=False)
# space.add_suite(wl.suites.Embench, iters=1000)
#
# space.add_suite(wl.suites.SPEC2017, tar="/home/nick/SPEC2017.tar.gz", config="train",
#                  # disabled=[600, 602, 620, 623, 625, 631, 641, 657, 619, 638, 644]
#                  # disabled=[620, 623],
#      )

# space.add_suite(wl.suites.MiBench)

optimized = wl.pipeline.Pipeline("optimized")
optimized.add_stage(wl.pipeline.OptStage(["-O3"]), name="Apply O3")
space.add_pipeline(optimized)

# Alaska. Requires `tools/cross_compile.sh` to have been run in the alaska
# tree, which builds the host pass plugin and the RISC-V translate.bc.
#
# This is a translation-only configuration: allocations stay plain libc, so no
# handles ever exist and every inlined check takes the "not a handle" branch.
# What it measures is the cost of the check plus its effect on code layout.
alaska = Alaska("/tank/nick/alaska")

# The alaska passes require canonicalized IR and no -O3 runs after them, so a
# plain -O3 pipeline is not a like-for-like baseline. `alaska-baseline` is the
# same bitcode canonicalized and then left alone -- it differs from `alaska`
# by nothing but the transform.
# alaska_baseline = wl.pipeline.Pipeline("alaska-baseline")
# alaska_baseline.add_stage(wl.pipeline.OptStage(["-O3"]), name="Apply O3")
# alaska_baseline.add_stage(alaska.baseline_stage(), name="Canonicalize")
# space.add_pipeline(alaska_baseline)

alaska_pl = wl.pipeline.Pipeline("alaska")
alaska_pl.add_stage(wl.pipeline.OptStage(["-O3"]), name="Apply O3")
alaska_pl.add_stage(alaska.stage(escape=False), name="Alaska")
space.add_pipeline(alaska_pl)

space.archive("riscv-archive")
