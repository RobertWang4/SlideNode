.PHONY: local-up local-down local-logs dev-backend dev-frontend dev-test

local-up:
	docker compose -f infra/docker-compose.yml up --build

local-down:
	docker compose -f infra/docker-compose.yml down

local-logs:
	docker compose -f infra/docker-compose.yml logs -f --tail=200

# Non-Docker local development
dev-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

dev-test:
	cd backend && PYTHONPATH=. pytest tests/ -v
