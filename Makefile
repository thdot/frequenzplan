SHELL := /bin/bash

html/data.json: Frequenzplan.pdf parse.py
	./parse.py $< $@

PDF_URL = https://www.bundesnetzagentur.de/SharedDocs/Downloads/DE/Sachgebiete/Telekommunikation/Unternehmen_Institutionen/Frequenzen/20210114_Frequenzplan.pdf?__blob=publicationFile
Frequenzplan.pdf:
	curl -o $@ $(PDF_URL)

run-http.server:
	python3 -m http.server --directory html

clean:
	rm -f html/data.json
