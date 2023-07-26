# Waterline

## Basic usage
Install waterline:
```
pip3 install --user waterline
```
You will also need LLVM and gclang installed. You can find gclang here: 


Using waterline to build and run NAS benchmarks:
```python
import waterline as wl
import waterline.suites

# create a waterline "workspace" where binaries will be compiled.
space = wl.Workspace("ws")
space.add_suite(suites.NAS, enable_openmp=False, suite_class="W") # build the "W" class of NAS.
space.run() # build and run all the benchmarks, emitting results to ws/results
```
