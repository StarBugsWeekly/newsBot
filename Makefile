SHELL += -eu

BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m

export VERSION := ${VERSION:-0.0.1}

.DEFAULT_GOAL := help

## install dependency python package
init:
	@echo "${BLUE}❤ install python dependency - processing${NC}"
	pipenv lock --requirements > requirements.txt
	@echo "${GREEN}✓ install python dependency - success${NC}"

## build the docker image
image-build: init
	@docker build -t smalltown/newsbot:${VERSION} .
	@docker tag smalltown/newsbot:${VERSION} smalltown/newsbot:latest

image-push: image-build
	@docker push smalltown/newsbot:${VERSION}
	@docker push smalltown/newsbot:latest

## display this help text
help:
	$(info Available targets)
	@awk '/^[a-zA-Z\-\_0-9]+:/ {                    \
		nb = sub( /^## /, "", helpMsg );              \
		if(nb == 0) {                                 \
			helpMsg = $$0;                              \
			nb = sub( /^[^:]*:.* ## /, "", helpMsg );   \
		}                                             \
		if (nb)                                       \
			print  $$1 "\t" helpMsg;                    \
	}                                               \
	{ helpMsg = $$0 }'                              \
	$(MAKEFILE_LIST) | column -ts $$'\t' |          \
	grep --color '^[^ ]*'

.PHONY: help init deploy test
