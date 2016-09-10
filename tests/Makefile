
all: clean is_venv
	./runner.sh

is_venv:
	test `env | grep '^VIRTUAL_ENV'`

clean:
	rm -rf *.diff *.out ./ditdir

ok: clean is_venv
	rm -f *.ok
	./oker.sh
