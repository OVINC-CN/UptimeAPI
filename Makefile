PY_FILES := $(shell git ls-files '*.py')

.PHONY: pylint pre-commit lint

pylint:
	pylint --disable=C0114,W0613,C0115,W1113,W0223,C0116,R0903 --max-line-length=120 $(PY_FILES)

pre-commit:
	pre-commit run -a

lint: pre-commit pylint
