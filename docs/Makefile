# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

view:
	open build/html/index.html

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

clean: 
	rm -rf build
	echo "Deleted directory build/"

	rm -rf source/modules
	echo "Deleted directory source/modules"

ibm_zos_core: 
    # Very static temporary way of generating what is needed
	mkdir build
	echo "Created directory build/"

	mkdir -p source/modules
	echo "Created directory source/modules/"

	#mv ../plugins/modules/__init__.py ../plugins/modules/__init__.py.skip
	echo "Rename ../plugins/modules/__init__.py with extension .skip"

	ansible-doc-extractor --template templates/module.rst.j2 source/modules ../plugins/modules/*.py
	echo "Build RST files for ../plugins/modules/*.py and into source/modules"

	#@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	echo "Build HTML, use command Make view  to see local results"

	#mv ../plugins/modules/__init__.py.skip mv ../plugins/modules/__init__.py
	echo "Rename ../plugins/modules/__init__.py.skip to .py"

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
