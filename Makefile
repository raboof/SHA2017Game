all: dist

.PHONY: dist

dist: *.py
	for i in *.py; do echo $$i; pyminifier -O $$i > dist/$$i ; done
