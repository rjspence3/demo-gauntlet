.PHONY: install lint typecheck test clean run-backend run-frontend

install:
	pip install -e .[dev]
	cd frontend && npm install

lint:
	pylint backend
	# cd frontend && npm run lint

typecheck:
	mypy -p backend

test:
	pytest

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf backend/__pycache__

run-backend:
	uvicorn backend.main:app --reload

run-frontend:
	cd frontend && npm run dev
