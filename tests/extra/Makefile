
all: clean set_env
	./runner.sh

clean:
	rm -rf *.diff *.out DIT_TESTING

ok: clean set_env
	rm -f *.ok
	./oker.sh

set_env:
	@echo "1" > DIT_TESTING
