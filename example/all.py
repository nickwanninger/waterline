import waterline as wl
import waterline.suites
import waterline.utils
import waterline.pipeline
from pathlib import Path

space = wl.Workspace('./test_workspace')

# space.add_suite(wl.suites.NAS(enable_openmp=True, suite_class='A'))
# space.add_suite(wl.suites.GAP())
space.add_suite(wl.suites.PolyBench())

space.acquire()
space.compile()
space.get_bitcode()


# run a baseline pipeline on the suites. This will produce a
# binary in each of their directories called 'baseline'
space.run_pipeline(waterline.pipeline.Pipeline('baseline'))

pl = waterline.pipeline.Pipeline('O3')


def opt(*passes):
  def _internal(bitcode):
    waterline.utils.run_command(['opt', bitcode, '-o', bitcode, *passes])
  return _internal


def disassemble(bitcode):
  waterline.utils.run_command(['llvm-dis', bitcode])
  pass


pl.add_stage(opt('-O3'))
pl.add_stage(disassemble)

space.run_pipeline(pl)
