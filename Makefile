
VENV_DIR=.venv

.PHONY: venv
venv:
	python3 -m venv ${VENV_DIR}

deps: ${VENV_DIR}/bin/pip requirements.txt
	${VENV_DIR}/bin/pip install -r requirements.txt

freeze: ${VENV_DIR}/bin/pip
	${VENV_DIR}/bin/pip freeze > requirements.txt
