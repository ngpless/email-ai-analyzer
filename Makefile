.PHONY: help install test cov lint run-server run-client build-exe clean

help:
	@echo "Доступные команды:"
	@echo "  install       — установить зависимости"
	@echo "  test          — прогнать pytest"
	@echo "  cov           — прогнать с покрытием"
	@echo "  lint          — проверить код (ruff)"
	@echo "  run-server    — запустить FastAPI"
	@echo "  run-client    — запустить PyQt6-клиент"
	@echo "  build-exe     — собрать .exe через PyInstaller"
	@echo "  clean         — удалить кэш и собранное"

install:
	python -m pip install -r requirements.txt

test:
	python -m pytest -v

cov:
	python -m pytest --cov=src/email_analyzer --cov-report=term-missing

lint:
	python -m ruff check src tests

run-server:
	python -m uvicorn email_analyzer.backend.main:app --reload --app-dir src

run-client:
	python -m email_analyzer.client.main

build-exe:
	python scripts/build_exe.py

clean:
	rm -rf build dist .pytest_cache htmlcov .coverage
	find . -name __pycache__ -type d -exec rm -rf {} +
