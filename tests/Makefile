
all: is_venv
	for i in test_*; do ./$$i; done

is_venv:
	test `env | grep '^VIRTUAL_ENV'`
