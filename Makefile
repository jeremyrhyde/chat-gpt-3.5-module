BUILD_CHANNEL?=local
OS=$(shell uname)
VERSION=v1.12.0
GIT_REVISION = $(shell git rev-parse HEAD | tr -d '\n')
TAG_VERSION?=$(shell git tag --points-at | sort -Vr | head -n1)

.PHONY: setup
setup:
	brew install mavsdk && pip3 install viam-sdk pyyaml openai poetry flake8

.PHONY: clean
clean:
	find . -type d -name '__pycache__' | xargs rm -rf

_lint:
	flake8 --max-line-length=100 --exclude=**/gen/**,*_grpc.py,*_pb2.py,*_pb2.pyi,.tox

.PHONY: lint
lint:
	poetry run $(MAKE) _lint 

.PHONY: install
install:
	pip install -r requirements.txt