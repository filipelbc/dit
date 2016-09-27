
install:
	python3 setup.py install

venv:
	python3 -m virtualenv -p python3 venv
	venv/bin/pip3 install -r requirements.txt

clean:
	make -C tests clean
	rm -rf __pycache__/ venv/ dist/ dit.egg-info/ build/
