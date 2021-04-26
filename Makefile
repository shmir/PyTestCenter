#
# Makefile to build and upload to local pypi servers.
# To upload to pypi.org use plain twine upload.
#

repo=localhost
user=pypiadmin
password=pypiadmin

install:
	python -m pip install -U pip
	pip install -i http://$(repo):8036 --trusted-host $(repo) -U --pre -r requirements-dev.txt

.PHONY: build
build:
	rm -rf dist/*
	python setup.py bdist_wheel

upload:
	make build
	twine upload --repository-url http://$(repo):8036 --user $(user) --password $(password) dist/*

test:
	pytest --cache-clear --flake8 --isort --cov=testcenter --tgn-api=rest --tgn-server=windows_511
