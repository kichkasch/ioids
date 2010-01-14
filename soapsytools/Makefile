# Makefile
#
# Tools for SoapSy XML Database
# Michael Pilgermann
# mpilgerm@glam.ac.uk
#
# last change Makefile: 2005-11-24
#
# global parameters
TITLE="SoapSy Tools"
URL="http://j4-itrl-12.comp.glam.ac.uk/g4ds/"

API_DOC_DIR=apidoc/

# program names
EPYDOC=/usr/bin/epydoc 
ZIP=/usr/bin/zip 
ZIP_PAR=-j
MKDIR=mkdir
RM=rm -f
PYTHON=python

$(API_DOC_DIR):
	$(MKDIR) $(API_DOC_DIR)

api-docs:$(API_DOC_DIR)
	$(EPYDOC) --inheritance listed -o $(API_DOC_DIR) -n $(TITLE) -u $(URL) -c blue *.py 

docs:   api-docs

clean:
	$(RM) *.pyc 

lines:
	wc -l *.py 

distribution:
	$(PYTHON) setup.py sdist --formats=gztar,zip

install:setup.py
	$(PYTHON) setup.py install

