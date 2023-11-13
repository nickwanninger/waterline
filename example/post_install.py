import waterline as wl
import waterline.suites as suites
import waterline.utils
import waterline.pipeline

space = wl.Workspace("ws")

class MyNas(suites.NAS):
  def post_acquire(self):
    print('NAS installed at', self.src)

space.add_suite(MyNas, enable_openmp=False, suite_class="W")

space.prepare()

pl = waterline.pipeline.Pipeline("optimized")
pl.add_stage(waterline.pipeline.OptStage(["-O3"]), name="Apply O3")
space.add_pipeline(pl)

results = space.run(runs=1)
