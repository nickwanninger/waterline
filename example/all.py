import waterline as wl
import waterline.suites
from pathlib import Path

space = wl.Workspace('./test_workspace')

space.add_suite(wl.suites.NAS(enable_openmp=True, suite_class='B'))
space.add_suite(wl.suites.GAP())

space.acquire()
# space.dump_benchmarks()
space.compile()
space.get_bitcode()
