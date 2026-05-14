import waterline as wl
import waterline.suites

target = wl.Target.riscv64gc("/opt/riscv")

space = wl.Workspace("bench-riscv", target=target)
space.add_suite(wl.suites.NAS, enable_openmp=False, suite_class="W")
space.add_suite(wl.suites.GAP, enable_openmp=False)
space.archive("riscv-archive")
