default:
	pyinstaller main.spec

init:
	pip install -r requirements.txt

test:
	pytest
