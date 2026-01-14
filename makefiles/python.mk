.PHONY: fmt-python check-python
# Backend Code Quality Commands
fmt-python:
	@echo "[Format] Running ruff format..."
	@uv run --project engine --dev ruff format ./engine
	@uv run --project ./backend/openapi-service --dev ruff format ./backend/openapi-service
	@echo "[Done] Code formatting complete"

check-python:
	@echo "[Check] Running ruff check..."
	@uv run --project engine --dev ruff check --fix ./engine
	@uv run --project ./backend/openapi-service --dev ruff check --fix ./backend/openapi-service
	@uv run --project engine --dev ruff check ./engine
	@uv run --project ./backend/openapi-service --dev ruff check ./backend/openapi-service
	@echo "[Done] Code check complete"