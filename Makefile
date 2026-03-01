.PHONY: local-up local-up-quick local-down local-logs dev-backend dev-frontend dev-test setup check-setup dev

# ─── Docker Compose ───────────────────────────────────────────────
local-up:
	docker compose -f infra/docker-compose.yml up --build

local-up-quick:
	docker compose -f infra/docker-compose.yml up

local-down:
	docker compose -f infra/docker-compose.yml down

local-logs:
	docker compose -f infra/docker-compose.yml logs -f --tail=200

# ─── Non-Docker local development ────────────────────────────────
dev-backend:
	cd backend && .venv/bin/python3.12 -m uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

dev-test:
	cd backend && PYTHONPATH=. .venv/bin/python3.12 -m pytest tests/ -v

# ─── One-command setup ────────────────────────────────────────────
setup:
	@echo "==> Checking prerequisites..."
	@command -v python3.12 >/dev/null 2>&1 || { echo "ERROR: python3.12 not found. Install Python 3.12 first."; exit 1; }
	@command -v node >/dev/null 2>&1        || { echo "ERROR: node not found. Install Node.js first."; exit 1; }
	@command -v npm >/dev/null 2>&1         || { echo "ERROR: npm not found. Install Node.js first."; exit 1; }
	@echo "==> Setting up backend venv..."
	@if [ ! -d backend/.venv ]; then \
		python3.12 -m venv backend/.venv; \
		echo "    Created backend/.venv"; \
	else \
		echo "    backend/.venv already exists, skipping"; \
	fi
	@echo "==> Installing backend dependencies..."
	@cd backend && .venv/bin/python3.12 -m pip install -r requirements.txt -q
	@echo "==> Copying .env files (if missing)..."
	@if [ ! -f backend/.env ]; then \
		cp backend/.env.example backend/.env; \
		echo "    Created backend/.env from .env.example"; \
	else \
		echo "    backend/.env already exists, skipping"; \
	fi
	@if [ ! -f frontend/.env ]; then \
		cp frontend/.env.example frontend/.env; \
		echo "    Created frontend/.env from .env.example"; \
	else \
		echo "    frontend/.env already exists, skipping"; \
	fi
	@echo "==> Installing frontend dependencies..."
	@cd frontend && npm install --silent
	@echo ""
	@echo "Setup complete! Run 'make dev' to start development servers."

# ─── Pre-flight check (used by make dev) ─────────────────────────
check-setup:
	@test -d backend/.venv          || { echo "ERROR: backend/.venv not found. Run 'make setup' first."; exit 1; }
	@test -f backend/.env           || { echo "ERROR: backend/.env not found. Run 'make setup' first."; exit 1; }
	@test -d frontend/node_modules  || { echo "ERROR: frontend/node_modules not found. Run 'make setup' first."; exit 1; }

# ─── One-command dev (backend + frontend) ─────────────────────────
dev: check-setup
	@echo "Starting backend (:8000) and frontend (:5173)..."
	@echo "Press Ctrl+C to stop both servers."
	@trap 'kill 0' INT TERM; \
	cd backend && .venv/bin/python3.12 -m uvicorn app.main:app --reload --port 8000 & \
	cd frontend && npm run dev & \
	wait
