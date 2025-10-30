.PHONY: install run test clean help

help:
	@echo "Second Brain - Available Commands"
	@echo "=================================="
	@echo "make install    - Install dependencies"
	@echo "make run       - Start the API server"
	@echo "make test      - Run test suite"
	@echo "make clean     - Clean generated files"
	@echo "make format    - Format code with black"

install:
	pip install -r requirements.txt

run:
	python -m app.main

test:
	python test_api.py

format:
	black app/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
