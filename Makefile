venv: venv/touchfile


venv/touchfile: requirements.txt
	test -d venv || virtualenv venv
	. venv/bin/activate; pip install -Ur requirements.txt
	touch venv/touchfile


build: venv
	. venv/bin/activate && python3 setup.py bdist_wheel


install: build
	pip3 install --force-reinstall dist/waterline-*


publish: build
	. venv/bin/activate && python3 -m twine upload --repository pypi dist/*

example: venv FORCE
	. venv/bin/activate && python3 -m example.all


post_install: venv FORCE
	. venv/bin/activate && python3 -m example.post_install

FORCE:
