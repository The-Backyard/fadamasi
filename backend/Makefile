.DEFAULT_GOAL=help

.PHONY: help venv install_dev install_prod check test migrate admin run clean

VENV_DIR = venv
PYTHON = python3
PIP = $(VENV_DIR)/bin/pip
PRE_COMMIT = $(VENV_DIR)/bin/pre-commit
TOX = $(VENV_DIR)/bin/tox

# Check if virtual environment is activated
define check_venv
	@ if [ "$$($(PYTHON) -c 'import sys; print(sys.prefix)')" != "$(CURDIR)/$(VENV_DIR)" ]; then \
		echo "Error: Virtual environment not activated. Please activate or create one."; \
		exit 1; \
	fi
endef

help: ## Display this help message with available make commands.
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

venv: ## Create a virtual environment.
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created."
	@echo "Activate with the command 'source $(VENV_DIR)/bin/activate'"

install_dev: ## Install project development dependencies.
	$(call check_venv)
	$(PIP) install -r requirements/development.txt
	$(PIP) install -r requirements/testing.txt
	$(PRE_COMMIT) install
	@echo "Project development dependencies installed."

install_prod: ## Install project production dependencies.
	$(call check_venv)
	$(PIP) install -r requirements/production.txt
	@echo "Project production dependencies installed."

check: ## Run code quality checks
	$(call check_venv)
	@python manage.py check
	$(TOX)
	$(PRE_COMMIT) run --all-files
	@echo "All checks passed"

test: ## Run tests
	$(call check_venv)
	@pytest --cov

migrate: ## Run database migrations
	$(call check_venv)
	@python manage.py makemigrations
	@python manage.py migrate

admin: ## Create admin superuser
	$(call check_venv)
	@python manage.py createsuperuser

run: ## Run development server
	$(call check_venv)
	@python manage.py runserver

flush: ## Reset the database
	$(call check_venv)
	@python manage.py flush

clean: ## Clean up the project of unneeded files
	@echo "Cleaning up the project of unneeded files..."
	@rm -rf .tox .mypy_cache .ruff_cache .pytest_cache *.egg-info dist .cache htmlcov coverage.xml .coverage $(VENV_DIR)
	@find . -name '*.pyc' -delete
	@find . -name 'db.sqlite3' -delete
	@find . -type d -name '__pycache__' -exec rm -r {} \+
	@echo "Clean up successfully completed."
