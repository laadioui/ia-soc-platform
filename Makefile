.PHONY: help up down restart build logs ps clean db-migrate db-upgrade seed test lint

# Default target
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'

# ============================================
# Infrastructure
# ============================================

up: ## Start all services
	docker-compose up -d
	@echo "Waiting for services to be healthy..."
	@sleep 10
	@echo "All services started. Access:"
	@echo "  Frontend:      http://localhost:3000"
	@echo "  Backend API:   http://localhost:8000/docs"
	@echo "  Keycloak:      http://localhost:8080"
	@echo "  OpenSearch:    http://localhost:9200"
	@echo "  Dashboards:    http://localhost:5601"
	@echo "  Prometheus:    http://localhost:9090"
	@echo "  Grafana:       http://localhost:3001"

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose down && docker-compose up -d

build: ## Build all Docker images
	docker-compose build --no-cache

logs: ## Follow logs of all services
	docker-compose logs -f

ps: ## List running containers
	docker-compose ps

clean: ## Remove all containers, volumes, networks
	docker-compose down -v --remove-orphans
	docker system prune -f

# ============================================
# Database
# ============================================

db-shell: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U soc_admin -d ai_soc_platform

db-migrate: ## Run Alembic migrations
	docker-compose exec backend alembic upgrade head

db-revision: ## Create new Alembic revision
	docker-compose exec backend alembic revision --autogenerate -m "$(msg)"

db-reset: ## Reset database (WARNING: destroys data)
	docker-compose exec backend alembic downgrade base
	docker-compose exec backend alembic upgrade head

# ============================================
# Development
# ============================================

dev-backend: ## Run backend in dev mode (local)
	cd services/collector-service && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Run frontend in dev mode (local)
	cd apps/frontend && npm run dev

install-backend: ## Install backend dependencies
	cd services/collector-service && pip install -e ".[dev]"

install-frontend: ## Install frontend dependencies
	cd apps/frontend && npm install

# ============================================
# Kafka
# ============================================

kafka-topics: ## List all Kafka topics
	docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list

kafka-producer: ## Open Kafka producer console
	docker-compose exec kafka kafka-console-producer --bootstrap-server localhost:9092 --topic security-events

kafka-consumer: ## Open Kafka consumer console
	docker-compose exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic security-events --from-beginning

# ============================================
# Testing & Quality
# ============================================

test: ## Run all tests
	cd services/collector-service && python -m pytest tests/ -v --tb=short

test-cov: ## Run tests with coverage
	cd services/collector-service && python -m pytest tests/ -v --cov=app --cov-report=html

lint: ## Run linting
	cd services/collector-service && ruff check app/
	cd services/collector-service && ruff format app/ --check

format: ## Format code
	cd services/collector-service && ruff check app/ --fix
	cd services/collector-service && ruff format app/

typecheck: ## Run type checking
	cd services/collector-service && mypy app/

# ============================================
# Seed & Demo
# ============================================

seed: ## Seed database with demo data
	docker-compose exec backend python scripts/seed_data.py

demo-attack: ## Simulate demo attack scenario
	docker-compose exec backend python scripts/simulate_attack.py

# ============================================
# Security
# ============================================

scan: ## Run security scanning
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image soc-backend:latest
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image soc-frontend:latest

# ============================================
# AI
# ============================================

pull-ollama-model: ## Pull Ollama model
	docker-compose exec ollama ollama pull llama3.1:8b

ai-query: ## Query AI assistant
	docker-compose exec backend python -c "import requests; r=requests.post('http://localhost:8000/api/v1/ai/analyze', json={'query':'$(query)'}); print(r.json())"
