

.PHONY: env
venv: env
	python3 -m venv env

deps: env/bin/pip
	./env/bin/pip install -r requirements.txt

freeze:
	./env/bin/pip freeze > requirements.txt
