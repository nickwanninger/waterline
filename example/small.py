import waterline as wl
import waterline.suites

space = wl.Workspace("bench")
space.add_suite(wl.suites.NAS, enable_openmp=False, suite_class="W")
space.run()
