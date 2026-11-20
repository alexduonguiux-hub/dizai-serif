#!/bin/bash
# An Nam Golden — dựng từ AnNam Serif (chạy SAU pipeline AnNam Serif: out/construct đã có outlines / spacing / ref_ratios)
#   bash tools/construct/golden/run.sh
set -e
cd "$(dirname "$0")/.."
R=../..
export DIZAI_OUT=$R/out/golden DIZAI_OUTI=$R/out/golden_italic DIZAI_FONTS=$R/fonts/golden
export DIZAI_FAMILY="AnNam Golden" DIZAI_PS=AnNamGolden DIZAI_XH=535
python3 golden/golden.py
cp $R/out/construct/ref_ratios.json $DIZAI_OUT/
python3 spacing.py | tail -3
echo "== QA"
for q in qa_outline qa_stroke qa_weight qa_kern; do echo "## $q"; python3 $q.py 2>&1 | grep -v Warn | tail -4; done
mkdir -p $DIZAI_OUTI && cp $DIZAI_OUT/{outlines,spacing,kerning,ref_ratios}.json $DIZAI_OUTI/
python3 export_font.py > $DIZAI_OUT/export.log 2>&1; tail -3 $DIZAI_OUT/export.log
echo DONE
