import waterline as wl
import waterline.suites

target = wl.Target.riscv64gc("/opt/riscv", dynamic_linker="/lib/ld-linux-riscv64-lp64d.so.1")

space = wl.Workspace("bench-riscv", target=target)
space.add_suite(wl.suites.NAS, enable_openmp=False, suite_class="W")
space.add_suite(wl.suites.GAP, enable_openmp=False)
space.add_suite(wl.suites.Embench, iters=10)
space.add_suite(wl.suites.MiBench, iters=10)
space.archive("riscv-archive")
