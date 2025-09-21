# =============================================================================
# Python Language Support - Makefile Module
# =============================================================================

# Python tool definitions (using virtual environment)
PYTHON := /Users/scguo/.virtualenvs/mydemos/bin/python
BLACK := black
ISORT := isort
FLAKE8 := flake8
MYPY := mypy
PYLINT := pylint

# Python project variables
PYTHON_DIR := backend-python
PYTHON_FILES := $(shell find backend-python -name "*.py" 2>/dev/null || true)

# =============================================================================
# Python Tool Installation
# =============================================================================

install-tools-python: ## Install Python development tools
	@if [ "$(HAS_PYTHON)" = "true" ]; then \
		echo "$(YELLOW)Installing Python tools...$(RESET)"; \
		$(PYTHON) -m pip install \
			black==24.4.2 \
			isort==5.13.2 \
			flake8==7.0.0 \
			mypy==1.9.0 \
			pylint==3.1.0; \
		echo "$(GREEN)Python tools installed$(RESET)"; \
	else \
		echo "$(BLUE)Skipping Python tools (no Python project detected)$(RESET)"; \
	fi

check-tools-python: ## Check Python development tools
	@if [ "$(HAS_PYTHON)" = "true" ]; then \
		echo "$(YELLOW)Checking Python tools...$(RESET)"; \
		test -f $(PYTHON) || (echo "$(RED)Python virtual environment not found at $(PYTHON)$(RESET)" && exit 1); \
		$(PYTHON) -c "import black" 2>/dev/null || (echo "$(RED)black is not installed. Run 'make install-tools-python'$(RESET)" && exit 1); \
		$(PYTHON) -c "import isort" 2>/dev/null || (echo "$(RED)isort is not installed. Run 'make install-tools-python'$(RESET)" && exit 1); \
		$(PYTHON) -c "import flake8" 2>/dev/null || (echo "$(RED)flake8 is not installed. Run 'make install-tools-python'$(RESET)" && exit 1); \
		$(PYTHON) -c "import mypy" 2>/dev/null || (echo "$(RED)mypy is not installed. Run 'make install-tools-python'$(RESET)" && exit 1); \
		$(PYTHON) -c "import pylint" 2>/dev/null || (echo "$(RED)pylint is not installed. Run 'make install-tools-python'$(RESET)" && exit 1); \
		echo "$(GREEN)Python tools available$(RESET)"; \
	fi

# =============================================================================
# Python Code Formatting
# =============================================================================

fmt-python: ## Format Python code
	@if [ "$(HAS_PYTHON)" = "true" ]; then \
		echo "$(YELLOW)Formatting Python code...$(RESET)"; \
		cd $(PYTHON_DIR) && \
		$(PYTHON) -m $(ISORT) . && \
		$(PYTHON) -m $(BLACK) .; \
		echo "$(GREEN)Python code formatted$(RESET)"; \
	else \
		echo "$(BLUE)Skipping Python formatting (no Python project)$(RESET)"; \
	fi

# =============================================================================
# Python Code Quality Checks
# =============================================================================

check-python: ## Check Python code quality
	@if [ "$(HAS_PYTHON)" = "true" ]; then \
		echo "$(YELLOW)Checking Python code quality...$(RESET)"; \
		cd $(PYTHON_DIR) && \
		echo "$(YELLOW)Running flake8...$(RESET)" && \
		$(PYTHON) -m $(FLAKE8) . && \
		echo "$(YELLOW)Running mypy...$(RESET)" && \
		$(PYTHON) -m $(MYPY) . && \
		echo "$(YELLOW)Running pylint...$(RESET)" && \
		$(PYTHON) -m $(PYLINT) --fail-under=8.0 *.py; \
		echo "$(GREEN)Python code quality checks completed$(RESET)"; \
	else \
		echo "$(BLUE)Skipping Python checks (no Python project)$(RESET)"; \
	fi

# Show Python project information
info-python: ## Show Python project information
	@echo "$(BLUE)Python Project Information:$(RESET)"
	@echo "  Python files: $(words $(PYTHON_FILES))"
	@if [ "$(HAS_PYTHON)" = "true" ]; then \
		echo "  Python version: $$($(PYTHON) --version)"; \
		echo "  Pip version: $$($(PYTHON) -m pip --version)"; \
	fi

# Format check (without modifying files)
fmt-check-python: ## Check if Python code format meets standards (without modifying files)
	@echo "$(YELLOW)Checking Python code formatting...$(RESET)"
	@if [ "$(HAS_PYTHON)" = "true" ]; then \
		cd $(PYTHON_DIR) && \
		$(PYTHON) -m $(ISORT) --check-only . && \
		$(PYTHON) -m $(BLACK) --check . || \
		(echo "$(RED)Python code is not formatted. Run 'make fmt-python' to fix.$(RESET)" && exit 1); \
	fi
	@echo "$(GREEN)Python code formatting checks passed$(RESET)"

# =============================================================================
# Individual Python Quality Check Tools
# =============================================================================

check-flake8-python: ## Run flake8 syntax and style checks
	@echo "$(YELLOW)Running flake8 checks...$(RESET)"
	@if [ "$(HAS_PYTHON)" = "true" ]; then \
		cd $(PYTHON_DIR) && $(PYTHON) -m $(FLAKE8) .; \
		echo "$(GREEN)Flake8 checks passed$(RESET)"; \
	fi

check-mypy-python: ## Run mypy type checking
	@echo "$(YELLOW)Running mypy type checking...$(RESET)"
	@if [ "$(HAS_PYTHON)" = "true" ]; then \
		cd $(PYTHON_DIR) && $(PYTHON) -m $(MYPY) .; \
		echo "$(GREEN)MyPy type checking passed$(RESET)"; \
	fi

check-pylint-python: ## Run pylint static analysis
	@echo "$(YELLOW)Running pylint static analysis...$(RESET)"
	@if [ "$(HAS_PYTHON)" = "true" ]; then \
		cd $(PYTHON_DIR) && $(PYTHON) -m $(PYLINT) --fail-under=8.0 *.py; \
		echo "$(GREEN)Pylint analysis passed$(RESET)"; \
	fi