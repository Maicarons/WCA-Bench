# -----------------------------------------------------------------------------
# .latexmkrc -- build the paper with XeLaTeX
#
# Usage:  latexmk -xelatex main.tex
# -----------------------------------------------------------------------------

# pdf_mode = 5 -> run xelatex and convert the XDV to PDF with xdvipdfmx.
# The xdvipdfmx invocation itself is left at latexmk's default, which supplies
# the input file and the -o output flag; overriding it here previously dropped
# the input filename and made xdvipdfmx read from an empty stdin.
$pdf_mode = 5;

# Run BibTeX automatically and report errors.
$bibtex_use = 2;

# Re-run passes until cross-references and citations are stable.
$max_repeat = 5;
