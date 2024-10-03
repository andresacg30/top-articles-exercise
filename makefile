.PHONY: run tests test

run:
	python main.py

tests:
	python -m pytest main.py

test:
	python -m pytest main.py -k $(name)