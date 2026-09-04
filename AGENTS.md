# Test and verification

Use the virtual environment in .venv for running unit test and flake8 check.

Running unit tests:

```bash
python -m unittest discover -v tests test_*.py
```

Checking changes with flake:

```bash
flake8 --max-line-length=120 --extend-ignore=D107,D200,D205,D400,D401 src
flake8 --max-line-length=120 --extend-ignore=D101,D102,D107,D200,D205,D400,D401,E402 tests
flake8 --max-line-length=120 --extend-ignore=D107,D200,D205,D400,D401 examples
flake8 --max-line-length=120 --extend-ignore=D107,D200,D205,D400,D401 dev_utils
```

Running pylint:

```bash
pylint src
```

# Updating enumeration.py

The entries of the enum IdentifiableSubTypes should be kept sorted.