.PHONY: help install lint test validate format terraform-init terraform-plan terraform-apply create-job

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install Python dependencies
	pip install -r requirements.txt
	pre-commit install

lint: ## Run linting checks
	ruff check .
	black --check .
	isort --check-only .

format: ## Format code
	black .
	isort .
	terraform fmt -recursive terraform/

test: ## Run tests
	pytest tests/ --cov=scripts --cov-report=term-missing

validate: ## Validate job definitions and Terraform
	python scripts/validate_job_definitions.py
	cd terraform && terraform init && terraform validate

terraform-init: ## Initialize Terraform
	cd terraform && terraform init

terraform-plan: ## Run Terraform plan
	cd terraform && terraform plan

terraform-apply: ## Apply Terraform changes
	cd terraform && terraform apply

create-job: ## Create a new job (usage: make create-job JOB_NAME=ford)
	@if [ -z "$(JOB_NAME)" ]; then \
		echo "Error: JOB_NAME is required. Usage: make create-job JOB_NAME=ford"; \
		exit 1; \
	fi
	python scripts/create_new_job.py $(JOB_NAME) $(ARGS)

