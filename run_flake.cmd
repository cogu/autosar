@echo off
flake8 --max-line-length=120 --ignore=D107,D200,D205,D400,D401,W503 src
flake8 --max-line-length=120 --ignore=D101,D102,D107,D200,D205,D400,D401,E402,W503 tests
flake8 --max-line-length=120 --ignore=D107,D200,D205,D400,D401,W503 examples
flake8 --max-line-length=120 --ignore=D107,D200,D205,D400,D401,W503 dev_utils