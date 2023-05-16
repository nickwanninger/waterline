from waterline import Suite, Benchmark, Linker, RunConfiguration
from pathlib import Path
import shutil
import os


class SpecBenchmark(Benchmark):
    def __init__(self, suite, name, bin, runs=[]):
        super().__init__(suite, name)
        self.runs = runs
        self.bin = bin

    def compile(self, output: Path):
        # print(f"compile spec {self.name}")
        self.suite.run_support_script("compile", self.name, self.suite.config)

        shutil.copy(
            self.suite.src
            / f"SPEC2017/benchspec/CPU/{self.name}/build/build_peak_gclang.0000/"
            / self.bin,
            output,
        )

    def run_configs(self):
        # print('run config for', self.name)
        config = self.suite.config
        if config == "ref":
            config = "refspeed"

        rundir = (
            self.suite.src
            / f"SPEC2017/benchspec/CPU/{self.name}/run/run_peak_{config}_gclang.0000/"
        )
        with open(rundir / "speccmds.cmd") as f:
            for line in f:
                pass
            last_line = line
        # hack: get the arguments :I
        args = last_line.split("peak.gclang ")[1].strip().split(" ")
        print(self.name, args)
        yield RunConfiguration(self.name, args=args, cwd=rundir)

    def link(self, object, output, linker):
        linker.link(
            self.suite.workspace,
            [object],
            output,
            args=["-lm", "-lstdc++", "-lpthread"],
        )


class SPEC2017(Suite):
    name = "SPEC2017"

    def configure(self, tar=None, config="ref"):
        if tar is None:
            raise RuntimeError("No tarball supplied for SPEC2017.")
        self.tarball = Path(tar)
        self.config = config
        # Integer
        self.add_benchmark(SpecBenchmark, "600.perlbench_s", "perlbench_s")
        self.add_benchmark(SpecBenchmark, "602.gcc_s", "sgcc")
        self.add_benchmark(SpecBenchmark, "605.mcf_s", "mcf_s")
        self.add_benchmark(SpecBenchmark, "620.omnetpp_s", "omnetpp_s")
        self.add_benchmark(SpecBenchmark, "623.xalancbmk_s", "xalancbmk_s")
        self.add_benchmark(SpecBenchmark, "625.x264_s", "x264_s")
        self.add_benchmark(SpecBenchmark, "631.deepsjeng_s", "deepsjeng_s")
        self.add_benchmark(SpecBenchmark, "641.leela_s", "leela_s")
        self.add_benchmark(SpecBenchmark, "657.xz_s", "xz_s")
        # # Floating Point
        # self.add_benchmark(SpecBenchmark, "619.lbm_s", "lbm_s"),
        # self.add_benchmark(SpecBenchmark, "638.imagick_s", "imagick_s"),
        # self.add_benchmark(SpecBenchmark, "644.nab_s", "nab_s"),

    def acquire(self):
        # the path to the SPEC2017 support folder
        support = Path(__file__).parent / "SPEC2017"
        shutil.copytree(support, self.src)
        shutil.unpack_archive(self.tarball, self.src, format="gztar")

        self.run_support_command(
            "chmod +x -R SPEC2017/bin SPEC2017/tools SPEC2017/*.sh"
        )
        self.run_support_script("install")

    def run_support_command(self, command):
        self.workspace.shell("sh", "-c", f"cd {self.src}; {command}")

    def run_support_script(self, name, *args):
        self.run_support_command(f'scripts/{name}.sh {" ".join(args)}')
