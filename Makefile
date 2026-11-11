.PHONY: test run replay
test:
	python3 -m unittest discover -s tests -v
run:
	python3 src/pipeline.py
replay:
	python3 src/pipeline.py --snapshot data/raw/snapshot-2026-11-10
