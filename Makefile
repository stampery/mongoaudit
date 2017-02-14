.PHONY: dist, test

default:
	pip install -I -r requirements.txt
	pyinstaller main.spec

init:
	python mongoaudit

test:
	pytest

install:
	pip install -I -r requirements.txt
	/usr/bin/env python2 setup.py bdist_wheel
	pip install dist/mongoaudit-*.whl

clean:
	find . -name \*.pyc -delete
	rm -rf ./dist ./build ./mongoaudit.egg-info
