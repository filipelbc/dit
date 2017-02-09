.PHONY: install install-completion venv clean

install:
	pip3 install -r requirements.txt
	python3 -c 'from dit.completion import _save_command_info; _save_command_info()'
	python3 setup.py install

install-completion:
	install -m 0644 bash-completion/dit /usr/share/bash-completion/completions/

venv:
	python3 -m virtualenv -p python3 venv
	venv/bin/pip3 install -r requirements.txt

clean:
	make -C tests clean
	make -C tests/extra clean
	rm -rf __pycache__/ venv/ dist/ dit.egg-info/ build/
