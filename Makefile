# =============================================================================
# Multi-Language CI/CD Development Toolchain - Main Makefile
# Supports: Go, TypeScript, Java (Maven), Python
# =============================================================================

# Include all modular Makefiles
include makefiles/common.mk
include makefiles/go.mk
include makefiles/typescript.mk
include makefiles/java.mk
include makefiles/python.mk
include makefiles/git.mk

# Optional: Include PR management for advanced users
# Uncomment the line below if you need Pull Request management features
# Warning: PR operations require repository write permissions
# include makefiles/git-pr.mk

# =============================================================================
# Main Targets and Help
# =============================================================================

# Declare all PHONY targets
.PHONY: help install-tools check-tools fmt fmt-all fmt-go fmt-ts fmt-java fmt-python fmt-check check check-all check-go check-ts check-java check-python project-status hooks-check-all hooks-fmt hooks-commit-msg hooks-uninstall hooks-install hooks-install-basic create-branch-helpers branch-setup new-branch new-feature new-bugfix new-hotfix new-design clean-branches list-remote-branches branch-help check-branch safe-push dev-setup

# Default target
help: ## Show help information
	@echo "$(BLUE)Multi-Language CI/CD Development Toolchain$(RESET)"
	@echo ""
	@make --no-print-directory project-status
	@echo ""
	@echo "$(BLUE)Available targets:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sed 's/^[^:]*://' | sed 's/:.*## / ## /' | sort | awk 'BEGIN {FS = " ## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'