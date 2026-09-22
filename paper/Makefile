# =============================================================================
#  WCA-Bench paper -- Makefile
#
#  Targets
#    make / make all   build both the English and Chinese PDFs (+ figures)
#    make en           build the English  PDF (main.pdf)
#    make zh           build the Chinese  PDF (zh/main.pdf)
#    make figures      regenerate figures/*.pdf from examples/leaderboard.csv
#    make check        validate \input / \cite / environment pairing (both languages)
#    make arxiv        arXiv submission tarball for the English version
#    make arxiv-zh     arXiv submission tarball for the Chinese version
#    make clean        remove auxiliaries (keep PDFs)
#    make distclean    remove auxiliaries, generated figures and PDFs
#
#  On Windows, run inside a POSIX shell (Git Bash / WSL / MSYS2), or call
#  `latexmk -xelatex main.tex` directly from cmd.exe.
# =============================================================================

MAIN    := main
LATEXMK := latexmk
PYTHON  ?= python
SHELL   := /bin/sh

.PHONY: all en zh pdf figures check arxiv arxiv-zh clean distclean

all: en zh

en: figures
	$(LATEXMK) -xelatex -interaction=nonstopmode $(MAIN).tex

zh: figures
	cd zh && $(LATEXMK) -xelatex -interaction=nonstopmode $(MAIN).tex

pdf: all

# Regenerate the result figures from the real leaderboard CSV.
figures:
	$(PYTHON) figures/make_figures.py

# Static sanity checks on both language versions.
check:
	$(PYTHON) check_bib.py

# Assemble the files arXiv expects for the English paper, then create a tarball.
arxiv: en
	rm -rf arxiv-upload && mkdir -p arxiv-upload
	cp $(MAIN).tex preamble.tex references.bib arxiv-upload/
	cp -r sections figures arxiv-upload/
	rm -f arxiv-upload/figures/make_figures.py
	tar -czf wcabench-arxiv.tar.gz -C arxiv-upload .
	@echo "Created wcabench-arxiv.tar.gz"

# Chinese variant: bundle the shared bibliography and rewrite the relative path.
arxiv-zh: zh
	rm -rf arxiv-upload-zh && mkdir -p arxiv-upload-zh/figures
	cp zh/$(MAIN).tex zh/preamble.tex arxiv-upload-zh/
	cp -r zh/sections arxiv-upload-zh/
	cp references.bib arxiv-upload-zh/
	cp figures/*.pdf arxiv-upload-zh/figures/
	sed -i.bak 's#\.\./references#references#' arxiv-upload-zh/$(MAIN).tex
	rm -f arxiv-upload-zh/$(MAIN).tex.bak
	tar -czf wcabench-zh-arxiv.tar.gz -C arxiv-upload-zh .
	@echo "Created wcabench-zh-arxiv.tar.gz"

clean:
	$(LATEXMK) -c $(MAIN).tex
	-cd zh && $(LATEXMK) -c $(MAIN).tex

distclean: clean
	-$(LATEXMK) -C $(MAIN).tex
	-cd zh && $(LATEXMK) -C $(MAIN).tex
	rm -f figures/*.pdf wcabench-arxiv.tar.gz wcabench-zh-arxiv.tar.gz
	rm -rf arxiv-upload arxiv-upload-zh
