IMAGE_NAME=scottyhind/nfl-data-pipeline
IMAGE_TAG:=$(shell git rev-parse HEAD)

.PHONY: build
build:
	@echo building $(IMAGE_NAME) image...
	@docker build \
		--cache-from $(IMAGE_NAME):build-cache \
		--cache-from $(IMAGE_NAME):latest \
		-t $(IMAGE_NAME):latest \
		-t $(IMAGE_NAME):$(IMAGE_TAG) .

.PHONY: run
run:
	@docker run $(IMAGE_NAME)

.PHONY: shell
shell:
	@docker run \
		-it \
		-v $(shell PWD)/data:/opt/nfl/data \
		-v $(shell PWD)/app:/opt/nfl/app \
		$(IMAGE_NAME) bash

.PHONY: pipeline
pipeline:
	@docker run -v $(shell PWD)/data:/opt/nfl/data $(IMAGE_NAME) python3 -m app

.PHONY: notebook
notebook:
	docker run \
		-p 8888:8888 \
		-v $(PWD)/data:/$(WORKDIR)/data \
		-v $(PWD)/notebooks:/$(WORKDIR)/notebooks \
		-v $(PWD)/app:/$(WORKDIR)/app \
		$(IMAGE_NAME) jupyter notebook --ip=0.0.0.0 --allow-root .