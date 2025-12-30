venv:
	python3 -m venv .venv

pre-install: venv
	.venv/bin/python -m pip install pytest
	.venv/bin/python -m pip install coverage


install: pre-install
	./.venv/bin/pip install -r requirements.txt

build:
	docker compose build

test: install
	./.venv/bin/python -m pytest -q

coverage: install
	./.venv/bin/python -m coverage run -m pytest
	./.venv/bin/python -m coverage report -m

# Generate HTML coverage report in htmlcov/index.html
coverage-html: install
	./.venv/bin/python -m coverage run -m pytest
	./.venv/bin/python -m coverage html
	@echo "HTML coverage report generated at htmlcov/index.html"

# Open HTML coverage report (Linux desktop)
coverage-open: coverage-html
	xdg-open htmlcov/index.html || true

clean:
	rm -rf htmlcov .pytest_cache local src/db.sqlite3 .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +

fclean: clean
	rm -rf .venv

# sci:
# lint:
# format:
# clean:
