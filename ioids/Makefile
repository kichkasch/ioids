# Makefile
#
# Inter-Organisational Intrusion Detection System
# Michael Pilgermann
# mpilgerm@glam.ac.uk
#
# last change Makefile: 2005-11-07
#
# global parameters
TITLE=		"Inter-Organisational Intrusion Detection System"
#URL=		"http://www.glam.ac.uk/soc/research/isrg.php"
URL=		"http://j4-itrl-12.comp.glam.ac.uk/g4ds/"

API_DOC_DIR=	apidoc/

# program names
EPYDOC=		/usr/bin/epydoc 
ZIP=		/usr/bin/zip 
ZIP_PAR=	-j
MKDIR=		mkdir
RM=		rm -f
PYTHON=		python

$(API_DOC_DIR):
	$(MKDIR) $(API_DOC_DIR)

api-docs:	$(API_DOC_DIR)
	$(EPYDOC) --html --inheritance listed -o $(API_DOC_DIR) --name $(TITLE) --url $(URL) --css blue *.py 
	
docs:   api-docs

clean:
	$(RM) *.pyc 

lines:
	wc -l *.py 
	
distribution:	
	$(PYTHON) setup.py sdist --formats=gztar,zip

install:	setup.py
	$(PYTHON) setup.py install

