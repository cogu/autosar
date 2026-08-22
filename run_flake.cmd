@echo off
flake8 --max-line-length=120 --extend-ignore=D107,D200,D205,D400,D401 src
flake8 --max-line-length=120 --extend-ignore=D101,D102,D107,D200,D205,D400,D401,E402 tests
flake8 --max-line-length=120 --extend-ignore=D107,D200,D205,D400,D401 examples
flake8 --max-line-length=120 --extend-ignore=D107,D200,D205,D400,D401 dev_utils