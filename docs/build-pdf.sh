#!/usr/bin/env bash
# Build setup-guide.pdf from setup-guide.md
# Usage: cd docs && ./build-pdf.sh

set -euo pipefail
cd "$(dirname "$0")"

pandoc setup-guide.md -o setup-guide.pdf \
  --pdf-engine=xelatex \
  -V geometry:margin=1in \
  -V fontsize=11pt \
  -V documentclass=article \
  -V colorlinks=true \
  -V linkcolor=blue \
  -V urlcolor=blue \
  -H header.tex

echo "Done: setup-guide.pdf"
