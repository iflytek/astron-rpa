# =============================================================================
# GitHub Flow - Pull Request Helpers (ADVANCED USERS ONLY)
# =============================================================================
#
# ⚠️  WARNING: These commands require repository write permissions and may
#    interfere with your team's code review process. Use with caution!
#
# 🎯 INTENDED FOR:
#    - Repository maintainers
#    - Team leads
#    - Experienced developers who understand the implications
#
# 🚫 NOT RECOMMENDED FOR:
#    - Junior developers
#    - Contributors without merge permissions
#    - Teams with strict review processes
#
# 📋 PREREQUISITES:
#    - GitHub CLI (gh) installed and authenticated
#    - Repository write access
#    - Understanding of your team's PR workflow
#
# 🔧 TO ENABLE:
#    1. Read ADVANCED-PR-SETUP.md first!
#    2. Uncomment the include line in the main Makefile:
#       # include makefiles/git-pr.mk
#
# =============================================================================

push-and-pr: safe-push ## ⚠️ ADVANCED: Push current branch and create Pull Request
	@echo "$(RED)⚠️  WARNING: This will create a Pull Request. Ensure you have proper permissions!$(RESET)"
	@echo "$(YELLOW)Creating Pull Request...$(RESET)"
	@current_branch=$$(git branch --show-current); \
	if command -v gh >/dev/null 2>&1; then \
		gh pr create --title "$$current_branch" --body "## Summary\n\nBrief description of changes\n\n## Testing\n\n- [ ] Unit tests pass\n- [ ] Integration tests pass\n- [ ] Manual testing completed" || true; \
	else \
		echo "$(YELLOW)GitHub CLI (gh) not installed. Please create PR manually at:$(RESET)"; \
		echo "$(BLUE)https://github.com/$$(git remote get-url origin | sed 's/.*github.com[:\\/]//' | sed 's/\\.git$$//').git/compare/$$current_branch$(RESET)"; \
	fi

pr-status: ## 🔍 Show current branch PR status
	@if command -v gh >/dev/null 2>&1; then \
		current_branch=$$(git branch --show-current); \
		echo "$(YELLOW)PR status for branch: $$current_branch$(RESET)"; \
		gh pr view --json state,title,url,mergeable 2>/dev/null || echo "$(BLUE)No PR found for current branch$(RESET)"; \
	else \
		echo "$(RED)GitHub CLI (gh) required for this command$(RESET)"; \
	fi

pr-list: ## 📋 List open Pull Requests
	@if command -v gh >/dev/null 2>&1; then \
		echo "$(YELLOW)Open Pull Requests:$(RESET)"; \
		gh pr list; \
	else \
		echo "$(RED)GitHub CLI (gh) required for this command$(RESET)"; \
	fi

pr-merge: ## ⚠️ DANGER: Merge current branch PR (requires approval + write access)
	@echo "$(RED)🚨 DANGER: This will merge and delete the branch! Are you sure?$(RESET)"
	@echo "$(YELLOW)Press Ctrl+C to cancel, or Enter to continue...$(RESET)"
	@read -r
	@if command -v gh >/dev/null 2>&1; then \
		current_branch=$$(git branch --show-current); \
		echo "$(YELLOW)Merging PR for branch: $$current_branch$(RESET)"; \
		gh pr merge --squash --delete-branch || echo "$(RED)Failed to merge PR. Check if PR exists and is approved$(RESET)"; \
	else \
		echo "$(RED)GitHub CLI (gh) required for this command$(RESET)"; \
	fi

switch-to-main: ## 🔄 Switch to main branch and pull latest changes
	@echo "$(YELLOW)Switching to main branch...$(RESET)"
	@git checkout main 2>/dev/null || git checkout master
	@echo "$(YELLOW)Pulling latest changes...$(RESET)"
	@git pull origin main 2>/dev/null || git pull origin master
	@echo "$(GREEN)✅ Switched to main and updated$(RESET)"

# GitHub Flow workflow helper
github-flow: ## 📚 GitHub Flow workflow guide
	@echo "$(BLUE)🔄 GitHub Flow Workflow Guide$(RESET)"
	@echo ""
	@echo "$(GREEN)Basic Development Flow:$(RESET)"
	@echo "  1. make new-branch type=feature name=my-feature  # Create feature branch"
	@echo "  2. # ... make your changes, commit them ..."
	@echo "  3. make fmt && make check                        # Format and check code"
	@echo "  4. make safe-push                               # Push to remote"
	@echo ""
	@echo "$(YELLOW)Advanced PR Flow (if enabled):$(RESET)"
	@echo "  5. make push-and-pr                             # Create PR (⚠️  advanced)"
	@echo "  6. # ... wait for code review and approval ..."
	@echo "  7. make pr-merge                                # Merge PR (🚨 dangerous)"
	@echo "  8. make switch-to-main                          # Return to main branch"
	@echo ""
	@echo "$(RED)⚠️  Advanced commands require proper permissions!$(RESET)"
	@echo "$(BLUE)📖 See ADVANCED-PR-SETUP.md for setup instructions$(RESET)"