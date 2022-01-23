#
# Makefile to build and upload to local pypi servers.
#

repo=localhost
user=pypiadmin
password=pypiadmin

install:
	python -m pip install -U pip
	pip install -U --pre -r requirements-dev.txt

.PHONY: build
build:
	rm -rf dist/*
	rm -rf *.egg-info
	rm -rf build
	python setup.py bdist_wheel

upload:
	make build
	twine upload --repository-url http://$(repo):8036 --user $(user) --password $(password) dist/*

test:
	pytest --cache-clear --flake8 --isort --cov=testcenter --tgn-api=rest --tgn-server=windows_511

release:
	# Github workflow python-publish will upload the release to pypi.
	git tag -a $(tag) -m "$(message)"
	gh release create $(tag) -F .changelog
