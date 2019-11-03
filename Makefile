-include .env

IMAGE = $(if $(CUSTOM_IMAGE),$(CUSTOM_IMAGE),obtka:latest)
CONTAINER = $(if $(CUSTOM_CONTAINER),$(CUSTOM_CONTAINER),obtka)
HOST_PORT = $(if $(CUSTOM_HOST_PORT),$(CUSTOM_HOST_PORT),8000)
MANAGECMD = docker exec -it $(CONTAINER)
APP_LOCATION = "$(PWD)"
DOCKERFILE = "$(PWD)/docker/dev/Dockerfile"


all:
	@echo "Hello $(LOGNAME), nothing to do by default"
	@echo "Try 'make help'"

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: delete-container ## Build the container
	@docker build --tag $(IMAGE) -f $(DOCKERFILE) $(APP_LOCATION)
	@docker run -dit --name $(CONTAINER) -v $(APP_LOCATION):/deploy -p $(HOST_PORT):8000 -w /deploy $(IMAGE) /bin/bash

restart: ## Restart the container
	@docker restart $(CONTAINER)

cmd: start ## Access bash
	@$(MANAGECMD) /bin/bash

up: start ## Start api dev server
	@$(MANAGECMD) /bin/bash -c "cd app && uvicorn api:app --reload --host 0.0.0.0"

start: clean
	@docker start $(CONTAINER)

down: ## Stop container
	@docker stop $(CONTAINER) || true

delete-container: down
	@docker rm $(CONTAINER) || true

remove: delete-container ## Delete containers and images
	@docker rmi $(IMAGE)

clean: ## Deletes old *.py[co] files
	@find . -name "*.py[co]" -delete

test: start ## Run tests
	@$(MANAGECMD) /bin/bash -c "cd app && python -m pytest ../test/"

code-style: start ## Run pyblack and flake8
	@$(MANAGECMD) /bin/bash -c "black . && flake8 ."


.DEFAULT_GOAL := help
