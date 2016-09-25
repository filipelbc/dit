
all: clean is_venv set_env
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
	$(file > DIT_TESTING,1)
