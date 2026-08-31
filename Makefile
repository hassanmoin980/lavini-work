.PHONY: run test evaluate

run:
	python3 -m app.server

test:
	python3 -m unittest discover -s tests -v

evaluate:
	python3 -m app.evaluation --data data/public_cases.jsonl
