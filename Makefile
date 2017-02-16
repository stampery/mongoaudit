.PHONY: dist, test

default:
	pip install -I -r requirements.txt
	pyinstaller main.spec

init:
	python mongoaudit

test:
	pytest

install:
	/usr/bin/env python2 setup.py install

clean:
	find . -name \*.pyc -delete
	rm -rf ./dist ./build ./mongoaudit.egg-info
