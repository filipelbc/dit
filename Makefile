
install:
	python3 setup.py install

venv:
	python3 -m virtualenv -p python3 venv
	pip3 install -r requirements.txt

clean:
	rm -rf __pycache__/ venv/ dist/ dit.egg-info/ build/ tests/ditdir
