# Locales to support
LOCALES := en ar es_419 fr zh_CN

.PHONY: help extract_translations compile_translations test test-coverage quality install-test-requirements

help: ## Display this help message
	@echo "Please use \`make <target>' where <target> is one of:"
	@grep '^[a-zA-Z]' $(MAKEFILE_LIST) | sort | awk -F ':.*?## ' 'NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

extract_translations: ## Extract strings to be translated from Python files
	@echo "Extracting translatable strings from Python files..."
	i18n_tool extract -v --config games/locale/config.yaml
	@echo "Extraction complete. Check games/locale/en/LC_MESSAGES/django-partial.po"

compile_translations: ## Compile .po files to .mo files
	@echo "Compiling translation files..."
	@for locale in $(LOCALES); do \
		echo "Generating $$locale..."; \
		i18n_tool generate -l $$locale --config games/locale/config.yaml; \
	done
	@find games/locale -type f \( -name "*-partial.po" -o -name "*-partial.mo" \) -delete
	@echo "Compilation complete. Check games/locale/*/LC_MESSAGES/*.mo files"

install-test-requirements: ## Install test requirements
	@echo "Installing test requirements..."
	pip install -r test-requirements.txt

test: ## Run unit tests
	@echo "Running unit tests..."
	pytest games/tests/ -v

test-coverage: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	pytest games/tests/ -v --cov=games --cov-report=term-missing --cov-report=html --cov-report=xml

quality: ## Run code quality checks
	@echo "Running pylint..."
	DJANGO_SETTINGS_MODULE=games.tests.settings pylint games --load-plugins=pylint_django --exit-zero
	@echo "Running pycodestyle..."
	pycodestyle games --exclude=migrations,tests --max-line-length=120 || true