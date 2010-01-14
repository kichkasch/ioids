# Makefile
#
# Grid for Digital Security - Test service
# Michael Pilgermann
# mpilgerm@glam.ac.uk
#
# last change Makefile: 2005-09-19
#
# global parameters
TITLE=		"Grid for Digital Security - Test service"
#URL=		"http://www.glam.ac.uk/soc/research/isrg.php"
URL=		"http://j4-itrl-12.comp.glam.ac.uk/g4ds/"

API_DOC_DIR=	apidoc/

# program names
EPYDOC=		/usr/bin/epydoc 
ZIP=		/usr/bin/zip 
ZIP_PAR=	-j
MKDIR=		mkdir
RM=		rm
PYTHON=		python

$(API_DOC_DIR):
	$(MKDIR) $(API_DOC_DIR)

api-docs:	$(API_DOC_DIR)
	$(EPYDOC) --inheritance listed -o $(API_DOC_DIR) -n $(TITLE) -u $(URL) -c blue *.py protocols/*.py algorithms/*.py

docs:   api-docs

clean:
	$(RM) *.pyc 

lines:
	wc -l *.py


