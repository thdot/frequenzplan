SHELL := /bin/bash

html/data.json: Frequenzplan.txt parse.py
	./parse.py $< $@

Frequenzplan.txt: Frequenzplan.pdf
	pdftotext -layout $< $@

PDF_URL = https://www.bundesnetzagentur.de/SharedDocs/Downloads/DE/Sachgebiete/Telekommunikation/Unternehmen_Institutionen/Frequenzen/20210114_Frequenzplan.pdf?__blob=publicationFile
Frequenzplan.pdf:
	curl -o $@ $(PDF_URL)

http.server-run:
	python3 -m http.server --directory html
