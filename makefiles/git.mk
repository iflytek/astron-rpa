# =============================================================================
# Git Hooks and Branch Management - Makefile Module
# =============================================================================

# =============================================================================
# Git Hooks Installation
# =============================================================================

hooks-check-all: ## Install pre-commit hook (formatting + code quality checks)
	@echo "$(YELLOW)Installing Git pre-commit hook (fmt + checks)...$(RESET)"
	@mkdir -p .git/hooks
	@echo '#!/bin/sh' > .git/hooks/pre-commit
	@echo '# Auto-format code and run quality checks before commit' >> .git/hooks/pre-commit
	@echo 'echo "$(YELLOW)Running code formatting...$(RESET)"' >> .git/hooks/pre-commit
	@echo '' >> .git/hooks/pre-commit
	@echo '# Run formatting' >> .git/hooks/pre-commit
	@echo 'make fmt' >> .git/hooks/pre-commit
	@echo '' >> .git/hooks/pre-commit
	@echo '# Check if any files were modified by formatting' >> .git/hooks/pre-commit
	@echo 'if [ -n "$$(git diff --name-only)" ]; then' >> .git/hooks/pre-commit
	@echo '    echo "$(GREEN)Code formatting completed. Adding formatted files to commit...$(RESET)"' >> .git/hooks/pre-commit
	@echo '    git add -u' >> .git/hooks/pre-commit
	@echo '    echo "$(GREEN)Formatted files added to commit.$(RESET)"' >> .git/hooks/pre-commit
	@echo 'else' >> .git/hooks/pre-commit
	@echo '    echo "$(GREEN)No formatting changes needed.$(RESET)"' >> .git/hooks/pre-commit
	@echo 'fi' >> .git/hooks/pre-commit
	@echo '' >> .git/hooks/pre-commit
	@echo '# Run multi-language code quality checks' >> .git/hooks/pre-commit
	@echo 'echo "$(YELLOW)Running multi-language code quality checks...$(RESET)"' >> .git/hooks/pre-commit
	@echo '' >> .git/hooks/pre-commit
	@echo '# Run all project quality checks' >> .git/hooks/pre-commit
	@echo 'if ! make check >/dev/null 2>&1; then' >> .git/hooks/pre-commit
	@echo '    echo "$(RED)Code quality checks failed. Please fix the issues.$(RESET)"' >> .git/hooks/pre-commit
	@echo '    echo "$(YELLOW)Tip: Run '\''make check'\'' to see detailed error messages$(RESET)"' >> .git/hooks/pre-commit
	@echo '    echo "$(YELLOW)Or run language-specific checks: make check-go/check-ts/check-java/check-python$(RESET)"' >> .git/hooks/pre-commit
	@echo '    exit 1' >> .git/hooks/pre-commit
	@echo 'fi' >> .git/hooks/pre-commit
	@echo '' >> .git/hooks/pre-commit
	@echo 'echo "$(GREEN)All pre-commit checks passed!$(RESET)"' >> .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "$(GREEN)Git pre-commit hook (fmt + checks) installed$(RESET)"

hooks-fmt: ## Install pre-commit hook (formatting only)
	@echo "$(YELLOW)Installing Git pre-commit hook (fmt only)...$(RESET)"
	@mkdir -p .git/hooks
	@echo '#!/bin/sh' > .git/hooks/pre-commit
	@echo '# Auto-format code before commit (no quality checks)' >> .git/hooks/pre-commit
	@echo 'echo "$(YELLOW)Running code formatting...$(RESET)"' >> .git/hooks/pre-commit
	@echo '' >> .git/hooks/pre-commit
	@echo '# Run formatting' >> .git/hooks/pre-commit
	@echo 'make fmt' >> .git/hooks/pre-commit
	@echo '' >> .git/hooks/pre-commit
	@echo '# Check if any files were modified by formatting' >> .git/hooks/pre-commit
	@echo 'if [ -n "$$(git diff --name-only)" ]; then' >> .git/hooks/pre-commit
	@echo '    echo "$(GREEN)Code formatting completed. Adding formatted files to commit...$(RESET)"' >> .git/hooks/pre-commit
	@echo '    git add -u' >> .git/hooks/pre-commit
	@echo '    echo "$(GREEN)Formatted files added to commit.$(RESET)"' >> .git/hooks/pre-commit
	@echo 'else' >> .git/hooks/pre-commit
	@echo '    echo "$(GREEN)No formatting changes needed.$(RESET)"' >> .git/hooks/pre-commit
	@echo 'fi' >> .git/hooks/pre-commit
	@echo '' >> .git/hooks/pre-commit
	@echo 'echo "$(GREEN)Pre-commit formatting completed!$(RESET)"' >> .git/hooks/pre-commit
	@echo 'echo "$(YELLOW)Note: Run '\''make check-all'\'' manually for quality checks$(RESET)"' >> .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "$(GREEN)Git pre-commit hook (fmt only) installed$(RESET)"

hooks-commit-msg: ## Install commit-msg hook for commit message format validation
	@echo "$(YELLOW)Installing Git commit-msg hook...$(RESET)"
	@mkdir -p .git/hooks
	@echo '#!/bin/sh' > .git/hooks/commit-msg
	@echo '# Validate commit message format (Conventional Commits)' >> .git/hooks/commit-msg
	@echo '' >> .git/hooks/commit-msg
	@echo 'commit_regex="^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(\(.+\))?: .{1,50}"' >> .git/hooks/commit-msg
	@echo '' >> .git/hooks/commit-msg
	@echo 'if ! grep -qE "$$commit_regex" "$$1"; then' >> .git/hooks/commit-msg
	@echo '    echo "\033[31mCommit message format error!\033[0m"' >> .git/hooks/commit-msg
	@echo '    echo "Expected format: <type>(<scope>): <description>"' >> .git/hooks/commit-msg
	@echo '    echo "Types: build, chore, ci, docs, feat, fix, perf, refactor, revert, style, test"' >> .git/hooks/commit-msg
	@echo '    echo "Example: feat: add user authentication"' >> .git/hooks/commit-msg
	@echo '    echo "Example: fix(auth): resolve login validation issue"' >> .git/hooks/commit-msg
	@echo '    exit 1' >> .git/hooks/commit-msg
	@echo 'fi' >> .git/hooks/commit-msg
	@echo '' >> .git/hooks/commit-msg
	@echo 'echo "\033[32mCommit message format validated!\033[0m"' >> .git/hooks/commit-msg
	@chmod +x .git/hooks/commit-msg
	@echo "$(GREEN)Git commit-msg hook installed$(RESET)"

hooks-pre-push: ## Install pre-push hook for branch naming convention validation
	@echo "$(YELLOW)Installing Git pre-push hook...$(RESET)"
	@mkdir -p .git/hooks
	@echo '#!/bin/sh' > .git/hooks/pre-push
	@echo '# Validate branch naming convention before push' >> .git/hooks/pre-push
	@echo '' >> .git/hooks/pre-push
	@echo 'current_branch=$$(git branch --show-current)' >> .git/hooks/pre-push
	@echo '' >> .git/hooks/pre-push
	@echo 'if echo "$$current_branch" | grep -qE "^(main|master|feature/.*|fix/.*|docs/.*|refactor/.*|test/.*|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9])$$"; then' >> .git/hooks/pre-push
	@echo '    echo "\033[32m✅ Branch $$current_branch meets push naming conventions\033[0m"' >> .git/hooks/pre-push
	@echo 'else' >> .git/hooks/pre-push
	@echo '    echo "\033[31m❌ Branch $$current_branch does not meet push naming conventions\033[0m"' >> .git/hooks/pre-push
	@echo '    echo "\033[33mSuggested rename: feature-$$current_branch or hotfix-$$current_branch\033[0m"' >> .git/hooks/pre-push
	@echo '    echo "\033[33mAllowed branch formats: main, feature/*, fix/*, docs/*, refactor/*, test/*, or descriptive names\033[0m"' >> .git/hooks/pre-push
	@echo '    exit 1' >> .git/hooks/pre-push
	@echo 'fi' >> .git/hooks/pre-push
	@chmod +x .git/hooks/pre-push
	@echo "$(GREEN)Git pre-push hook installed$(RESET)"

# =============================================================================
# Git Hooks Uninstallation
# =============================================================================

hooks-uninstall: ## Uninstall all Git hooks
	@echo "$(YELLOW)Uninstalling all Git hooks...$(RESET)"
	@if [ -f .git/hooks/pre-commit ]; then \
		rm -f .git/hooks/pre-commit; \
		echo "$(GREEN)✓ Removed pre-commit hook$(RESET)"; \
	else \
		echo "$(BLUE)- pre-commit hook not found$(RESET)"; \
	fi
	@if [ -f .git/hooks/commit-msg ]; then \
		rm -f .git/hooks/commit-msg; \
		echo "$(GREEN)✓ Removed commit-msg hook$(RESET)"; \
	else \
		echo "$(BLUE)- commit-msg hook not found$(RESET)"; \
	fi
	@if [ -f .git/hooks/pre-push ]; then \
		rm -f .git/hooks/pre-push; \
		echo "$(GREEN)✓ Removed pre-push hook$(RESET)"; \
	else \
		echo "$(BLUE)- pre-push hook not found$(RESET)"; \
	fi
	@echo "$(GREEN)All Git hooks uninstalled$(RESET)"

hooks-uninstall-pre: ## Uninstall pre-commit hook
	@echo "$(YELLOW)Uninstalling pre-commit hook...$(RESET)"
	@if [ -f .git/hooks/pre-commit ]; then \
		rm -f .git/hooks/pre-commit; \
		echo "$(GREEN)Pre-commit hook removed$(RESET)"; \
	else \
		echo "$(BLUE)Pre-commit hook not found$(RESET)"; \
	fi

hooks-uninstall-msg: ## Uninstall commit-msg hook
	@echo "$(YELLOW)Uninstalling commit-msg hook...$(RESET)"
	@if [ -f .git/hooks/commit-msg ]; then \
		rm -f .git/hooks/commit-msg; \
		echo "$(GREEN)Commit-msg hook removed$(RESET)"; \
	else \
		echo "$(BLUE)Commit-msg hook not found$(RESET)"; \
	fi

# Combined installation commands
hooks-install: hooks-check-all hooks-commit-msg hooks-pre-push ## Install all Git hooks (pre-commit full mode + commit-msg + pre-push)
	@echo "$(GREEN)All Git hooks installed!$(RESET)"

hooks-install-basic: hooks-fmt hooks-commit-msg hooks-pre-push ## Install basic Git hooks (pre-commit lightweight mode + commit-msg + pre-push)
	@echo "$(GREEN)Basic Git hooks installed!$(RESET)"

# =============================================================================
# Branch Management
# =============================================================================

create-branch-helpers: ## Create Git branch management helper script
	@echo "$(YELLOW)Creating Git branch management helper script...$(RESET)"
	@mkdir -p .git
	@if [ ! -f .git/git-branch-helpers.sh ]; then \
		echo '#!/bin/bash' > .git/git-branch-helpers.sh; \
		echo '' >> .git/git-branch-helpers.sh; \
		echo '# Git Branch Management Helper Script' >> .git/git-branch-helpers.sh; \
		echo '# Part of Multi-Language CI/CD Development Toolchain' >> .git/git-branch-helpers.sh; \
		echo '' >> .git/git-branch-helpers.sh; \
		echo '# Colors for output' >> .git/git-branch-helpers.sh; \
		echo "RED='\033[31m'" >> .git/git-branch-helpers.sh; \
		echo "GREEN='\033[32m'" >> .git/git-branch-helpers.sh; \
		echo "YELLOW='\033[33m'" >> .git/git-branch-helpers.sh; \
		echo "BLUE='\033[34m'" >> .git/git-branch-helpers.sh; \
		echo "RESET='\033[0m'" >> .git/git-branch-helpers.sh; \
		echo '' >> .git/git-branch-helpers.sh; \
		echo '# Function to create a new branch with GitHub Flow naming' >> .git/git-branch-helpers.sh; \
		echo 'new_branch() {' >> .git/git-branch-helpers.sh; \
		echo '    local branch_type=$$1' >> .git/git-branch-helpers.sh; \
		echo '    local branch_name=$$2' >> .git/git-branch-helpers.sh; \
		echo '    if [ -z "$$branch_type" ] || [ -z "$$branch_name" ]; then' >> .git/git-branch-helpers.sh; \
		echo '        echo -e "$${RED}Error: Both type and name are required$${RESET}"' >> .git/git-branch-helpers.sh; \
		echo '        echo "Usage: make new-branch type=feature name=user-auth"' >> .git/git-branch-helpers.sh; \
		echo '        echo "Types: feature, fix, docs, refactor, test"' >> .git/git-branch-helpers.sh; \
		echo '        exit 1' >> .git/git-branch-helpers.sh; \
		echo '    fi' >> .git/git-branch-helpers.sh; \
		echo '    local full_branch_name="$$branch_type/$$branch_name"' >> .git/git-branch-helpers.sh; \
		echo '    echo -e "$${YELLOW}Creating $$branch_type branch: $$full_branch_name$${RESET}"' >> .git/git-branch-helpers.sh; \
		echo '    if git branch --list | grep -q "$$full_branch_name"; then' >> .git/git-branch-helpers.sh; \
		echo '        echo -e "$${RED}Error: Branch $$full_branch_name already exists$${RESET}"' >> .git/git-branch-helpers.sh; \
		echo '        exit 1' >> .git/git-branch-helpers.sh; \
		echo '    fi' >> .git/git-branch-helpers.sh; \
		echo '    git checkout -b "$$full_branch_name"' >> .git/git-branch-helpers.sh; \
		echo '    echo -e "$${GREEN}✅ Created and switched to $$branch_type branch: $$full_branch_name$${RESET}"' >> .git/git-branch-helpers.sh; \
		echo '}' >> .git/git-branch-helpers.sh; \
		echo '' >> .git/git-branch-helpers.sh; \
		echo '# Convenience function for feature branches' >> .git/git-branch-helpers.sh; \
		echo 'new_feature() {' >> .git/git-branch-helpers.sh; \
		echo '    new_branch "feature" "$$1"' >> .git/git-branch-helpers.sh; \
		echo '}' >> .git/git-branch-helpers.sh; \
		echo '' >> .git/git-branch-helpers.sh; \
		echo '# Convenience function for fix branches' >> .git/git-branch-helpers.sh; \
		echo 'new_fix() {' >> .git/git-branch-helpers.sh; \
		echo '    new_branch "fix" "$$1"' >> .git/git-branch-helpers.sh; \
		echo '}' >> .git/git-branch-helpers.sh; \
		echo '' >> .git/git-branch-helpers.sh; \
		echo '# Function to list remote branches' >> .git/git-branch-helpers.sh; \
		echo 'list_remote_branches() {' >> .git/git-branch-helpers.sh; \
		echo '    echo -e "$${BLUE}Remote branches:$${RESET}"' >> .git/git-branch-helpers.sh; \
		echo '    git fetch --quiet' >> .git/git-branch-helpers.sh; \
		echo '    git branch -r | grep -E "(origin/main|origin/master|origin/feature/|origin/fix/|origin/docs/|origin/refactor/|origin/test/)"' >> .git/git-branch-helpers.sh; \
		echo '}' >> .git/git-branch-helpers.sh; \
		echo '' >> .git/git-branch-helpers.sh; \
		echo '# Function to display help' >> .git/git-branch-helpers.sh; \
		echo 'branch_help() {' >> .git/git-branch-helpers.sh; \
		echo '    echo -e "$${BLUE}GitHub Flow Branch Management Help$${RESET}"' >> .git/git-branch-helpers.sh; \
		echo '    echo ""' >> .git/git-branch-helpers.sh; \
		echo '    echo "Branch types and examples:"' >> .git/git-branch-helpers.sh; \
		echo '    echo "  feature/user-auth    - New features"' >> .git/git-branch-helpers.sh; \
		echo '    echo "  fix/login-bug        - Bug fixes"' >> .git/git-branch-helpers.sh; \
		echo '    echo "  docs/api-guide       - Documentation"' >> .git/git-branch-helpers.sh; \
		echo '    echo "  refactor/cleanup     - Code refactoring"' >> .git/git-branch-helpers.sh; \
		echo '    echo "  test/unit-coverage   - Testing"' >> .git/git-branch-helpers.sh; \
		echo '    echo ""' >> .git/git-branch-helpers.sh; \
		echo '    echo "Available commands: new-branch, new-feature, new-fix, list-remote-branches, branch-help"' >> .git/git-branch-helpers.sh; \
		echo '}' >> .git/git-branch-helpers.sh; \
		echo '' >> .git/git-branch-helpers.sh; \
		echo '# Main logic' >> .git/git-branch-helpers.sh; \
		echo 'case "$$1" in' >> .git/git-branch-helpers.sh; \
		echo '    "new-branch") new_branch "$$2" "$$3" ;;' >> .git/git-branch-helpers.sh; \
		echo '    "new-feature") new_feature "$$2" ;;' >> .git/git-branch-helpers.sh; \
		echo '    "new-fix") new_fix "$$2" ;;' >> .git/git-branch-helpers.sh; \
		echo '    "list-remote-branches") list_remote_branches ;;' >> .git/git-branch-helpers.sh; \
		echo '    "branch-help") branch_help ;;' >> .git/git-branch-helpers.sh; \
		echo '    *) echo "Unknown command: $$1"; branch_help; exit 1 ;;' >> .git/git-branch-helpers.sh; \
		echo 'esac' >> .git/git-branch-helpers.sh; \
		chmod +x .git/git-branch-helpers.sh; \
		echo "$(GREEN)Git branch management helper script created$(RESET)"; \
	else \
		echo "$(BLUE)Git branch management helper script already exists$(RESET)"; \
	fi

branch-setup: create-branch-helpers ## Setup branch management strategy
	@echo "$(YELLOW)Setting up branch management...$(RESET)"
	@if [ -f .git/hooks/pre-push ]; then chmod +x .git/hooks/pre-push; fi
	@echo "$(GREEN)Branch management setup completed!$(RESET)"
	@echo ""
	@echo "$(BLUE)GitHub Flow Branch Commands:$(RESET)"
	@echo "  make new-branch type=<type> name=<name> - Create <type>/<name> branch (type: feature, fix, docs, refactor, test)"
	@echo "  make new-feature name=<name>      - Create feature/<name> branch (shortcut)"
	@echo "  make new-fix name=<name>          - Create fix/<name> branch (shortcut)"
	@echo "  make clean-branches               - Clean up merged branches"
	@echo "  make list-remote-branches         - List remote branches meeting conventions"
	@echo "  make branch-help                  - Show GitHub Flow branch management help"
	@echo ""
	@echo "$(YELLOW)Note: For Pull Request management, see makefiles/git-pr.mk (advanced users)$(RESET)"

new-branch: ## Create branch with type/name format (usage: make new-branch type=feature name=user-auth)
	@.git/git-branch-helpers.sh new-branch $(type) $(name)

new-feature: ## Create feature branch (usage: make new-feature name=user-auth)
	@.git/git-branch-helpers.sh new-feature $(name)

new-fix: ## Create fix branch (usage: make new-fix name=login-bug)
	@.git/git-branch-helpers.sh new-fix $(name)

clean-branches: ## Clean up merged local branches
	@.git/git-branch-helpers.sh clean-branches

list-remote-branches: ## List remote branches that meet naming conventions
	@.git/git-branch-helpers.sh list-remote-branches

branch-help: ## Show branch management help
	@.git/git-branch-helpers.sh branch-help

# Check if current branch can be pushed
check-branch: ## Check if current branch meets push naming conventions
	@current_branch=$$(git branch --show-current); \
	if echo "$$current_branch" | grep -qE "^(main|master|feature/.*|fix/.*|docs/.*|refactor/.*|test/.*|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9])$$"; then \
		echo "$(GREEN)✅ Current branch $$current_branch meets push naming conventions$(RESET)"; \
	else \
		echo "$(RED)❌ Current branch $$current_branch does not meet push naming conventions$(RESET)"; \
		echo "$(YELLOW)Suggested rename: feature/$$current_branch or fix/$$current_branch$(RESET)"; \
	fi

# Safe push (check branch name first)
safe-push: check-branch ## Safely push current branch to remote
	@current_branch=$$(git branch --show-current); \
	if echo "$$current_branch" | grep -qE "^(main|master|feature/.*|fix/.*|docs/.*|refactor/.*|test/.*|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9])$$"; then \
		echo "$(GREEN)Pushing $$current_branch to remote...$(RESET)"; \
		git push origin $$current_branch; \
	else \
		echo "$(RED)Push rejected: branch name does not meet conventions$(RESET)"; \
		exit 1; \
	fi