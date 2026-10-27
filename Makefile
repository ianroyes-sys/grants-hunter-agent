test:
	python3 -m unittest discover -s engine -v
	python3 -m unittest discover -s tests -v

.PHONY: test
