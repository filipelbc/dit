
all: is_venv clean set_env
	make -C .. install
	make run

is_venv:
	test `env | grep '^VIRTUAL_ENV'`

clean:
	rm -rf *.diff *.out ./ditdir DIT_TESTING

set_env:
	@echo "1" > DIT_TESTING

ok: clean is_venv set_env
	make -C .. install
	rm -f *.ok
	./oker.sh test_*.sh

run: clean set_env
	./runner.sh test_*.sh

ci: run
