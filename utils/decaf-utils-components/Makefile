##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

.PHONY: all clean install doc sdist

all: install doc

clean:
	rm -rf build dist decaf_utils_components.egg-info requirements.txt
	rm -rf docs/sphinx/source/code/*
	make -C docs/sphinx clean

install: clean
	pip-compile requirements.in
	pip install -r requirements.txt
	python setup.py install

doc:
	sphinx-apidoc -o docs/sphinx/source/code ./decaf_utils_components
	make -C docs/sphinx html latex

sdist: clean
	python setup.py sdist

