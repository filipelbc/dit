.PHONY: all is_venv run

all: is_venv
	make -C .. install
	make run

is_venv:
	test `env | grep '^VIRTUAL_ENV'`

run:
	./runner *.py
