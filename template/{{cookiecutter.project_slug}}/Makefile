.PHONY: dev up down check fmt lint

up:
	docker compose up --build

down:
	docker compose down

dev:
	cd apps/web && npm run dev

check: lint
	cd apps/agent && uv run basedpyright
	cd apps/web && npm run typecheck

lint:
	cd apps/agent && uvx ruff check . && uvx black --check .
	cd apps/web && npx biome check .

fmt:
	cd apps/agent && uvx ruff check --fix . && uvx black .
	cd apps/web && npx biome check --write .
