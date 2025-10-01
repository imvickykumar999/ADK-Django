# Makefile for Django project (Ubuntu-friendly)

# ===== Variables (override with: make VAR=value target) =====
PYTHON ?= python
MANAGE := $(PYTHON) manage.py
DB     ?= default              # which Django DB alias to use

# Celery settings
APP      ?= pantrio_backend
LOGLEVEL ?= info
POOL     ?= solo               # on Linux you can use "prefork" if you want
CELERY   ?= celery             # e.g., "poetry run celery" or "venv/bin/celery"

.PHONY: help install rn mg mgs cs test lint shell celeryw celeryb celery load load_aisle load_email_templates load_tagcategories

help:
	@echo "Makefile commands:"
	@echo "  make install                - Install requirements"
	@echo "  make rn                     - Run Django dev server"
	@echo "  make mg                     - Apply migrations"
	@echo "  make mgs                    - Create new migrations"
	@echo "  make cs                     - Create a superuser"
	@echo "  make test                   - Run tests"
	@echo "  make lint                   - Lint Python files with flake8"
	@echo "  make shell                  - Start Django shell"
	@echo "  make load FIXTURES='path1.json path2.json' [DB=default] - Load fixture(s)"
	@echo "  make load_aisle             - Load aisle_space_fixture.json"
	@echo "  make load_email_templates   - Load email_templates.json"
	@echo "  make load_tagcategories     - Load tagcategories.json"
	@echo "  make celeryw                - Start Celery worker"
	@echo "  make celeryb                - Start Celery beat"
	@echo "  make celery                 - Start worker and beat in parallel"

install:
	pip install -r requirements.txt

rn:
	$(MANAGE) runserver 

mg:
	$(MANAGE) migrate

mgs:
	$(MANAGE) makemigrations

cs:
	$(MANAGE) createsuperuser

test:
	$(MANAGE) test

lint:
	flake8 .

shell:
	$(MANAGE) shell

# ===== Fixture loading =====
# Usage:
#   make load FIXTURES='app/fixtures/a.json app/fixtures/b.json' [DB=default]
load: mg
	@if [ -z "$(FIXTURES)" ]; then \
		echo "Usage: make load FIXTURES='path/to/file1.json [file2.json ...]' [DB=default]"; \
		exit 1; \
	fi
	$(MANAGE) loaddata $(FIXTURES) --database $(DB)

# Convenience shortcuts for specific files
load_aisle: mg
	$(MANAGE) loaddata aisle_space_fixture.json --database $(DB)

load_email_templates: mg
	$(MANAGE) loaddata email_templates.json --database $(DB)

load_tagcategories: mg
	$(MANAGE) loaddata tagcategories.json --database $(DB)

# ===== Celery targets =====
celeryw:
	$(CELERY) -A $(APP) worker --loglevel=$(LOGLEVEL) -E -P $(POOL)

celeryb:
	$(CELERY) -A $(APP) beat --loglevel=$(LOGLEVEL)

# Run worker + beat in parallel (requires GNU make)
celery:
	$(MAKE) -j 2 celeryw celeryb

