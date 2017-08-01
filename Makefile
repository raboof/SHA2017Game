all: dist

.PHONY: dist

dist: *.py
	# don't obfuscate functions, they're an API :)
	for i in *.py; do echo $$i; pyminifier --obfuscate-classes --obfuscate-variables --obfuscate-import-methods --obfuscate-builtins --replacement-length=5 $$i > dist/$$i ; done
