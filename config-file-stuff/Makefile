all: submit_config.json


submit_config.json: roster.csv
	python makeconfig.py > submit_config.json

roster.csv: PZSR_SUBJECT_CLASS_ROSTER.csv
	python makecsv.py

.PHONY: clean
clean:
	rm -f roster.csv
	rm -f submit_config.json
