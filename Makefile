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
	@docker run -it $(IMAGE_NAME) bash