
all: is_venv clean set_env
	make -C .. install
	./runner.sh

is_venv:
	test `env | grep '^VIRTUAL_ENV'`

clean:
	rm -rf *.diff *.out ./ditdir DIT_TESTING

ok: clean is_venv set_env
	rm -f *.ok
	./oker.sh

set_env:
	@echo "1" > DIT_TESTING

ci-tests: clean set_env
	./runner.sh
