.PHONY: build
build:
	docker-compose build

.PHONY: start
start:
	docker-compose up -d

.PHONY: stop
stop:
	docker-compose down -v

.PHONY: format
format:
	black . && isort .

.PHONY: makemigrations
makemigrations:
	@read -p "Enter migration message: " MSG; \
	docker exec users_fastapi alembic revision --autogenerate -m "$$MSG"

.PHONY: migrate
migrate:
	docker exec users_fastapi alembic upgrade head
