# Waterline

## Basic usage
Install waterline:
```
pip3 install --user waterline
```

Using waterline to build and run NAS benchmarks:
```python
import waterline as wl

# create a waterline "workspace" where binaries will be compiled.
space = wl.Workspace("ws")
space.add_suite(wl.suites.NAS, enable_openmp=False, suite_class="W") # build the "W" class of NAS.
space.run() # build and run all the benchmarks, emitting results to ws/results
```
