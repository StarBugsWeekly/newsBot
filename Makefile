SHELL += -eu

BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m

VERSION ?= latest
PROFILES ?= database

.DEFAULT_GOAL := help

## install dependency python package
init:
	@echo "${BLUE}❤ install python dependency - processing${NC}"
	pipenv lock --requirements > requirements.txt
	@echo "${GREEN}✓ install python dependency - success${NC}"

## start devloper mode
dev-on:
##@pipenv install
	@COMPOSE_PROFILES=${PROFILES} docker-compose down
	@COMPOSE_PROFILES=${PROFILES} docker-compose up -d

## stop developr mode
dev-off:
	@COMPOSE_PROFILES=${PROFILES} docker-compose down

prod-on:
##@pipenv install
	@COMPOSE_PROFILES=production docker-compose down
	@COMPOSE_PROFILES=production docker-compose up -d

## stop developr mode
prod-off:
	@COMPOSE_PROFILES=production docker-compose down

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

.PHONY: help init dev-on dev-off prod-on prod-off image-build image-push
