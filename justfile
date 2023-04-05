build:
  python3 setup.py bdist_wheel

install: build
  pip3 install --force-reinstall dist/waterline-*


test:
  @python3 -m tests