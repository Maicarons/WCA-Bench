# -----------------------------------------------------------------------------
# .latexmkrc -- 使用 XeLaTeX 编译中文版
#
# 用法：  latexmk -xelatex main.tex
# -----------------------------------------------------------------------------

# pdf_mode = 5 -> 使用 xelatex，并用 xdvipdfmx 生成 PDF。
$pdf_mode = 5;

# 自动运行 BibTeX（参考文献位于 ../references.bib）。
$bibtex_use = 2;

# 反复编译直到交叉引用与文献稳定。
$max_repeat = 5;
