#!/bin/bash
# An Nam Golden — dựng từ AnNam Serif (chạy SAU pipeline AnNam Serif: out/construct đã có outlines / spacing / ref_ratios)
#   bash tools/construct/golden/run.sh
set -e
cd "$(dirname "$0")/.."
R=../..
export DIZAI_OUT=$R/out/golden DIZAI_OUTI=$R/out/golden_italic DIZAI_FONTS=$R/fonts/golden
export DIZAI_FAMILY="AnNam Golden" DIZAI_PS=AnNamGolden DIZAI_XH=535
python3 golden/golden.py
DIZAI_RTOL=1.5 DIZAI_CTOL=0.3 python3 compat_masters.py | grep '^compat'   # ghép cấu trúc R / B + liền tiếp tuyến khi nội suy (S18, S25…)
cp $R/out/construct/ref_ratios.json $DIZAI_OUT/
python3 spacing.py | tail -3
echo "== QA"
for q in qa_outline qa_stroke qa_weight qa_kern; do echo "## $q"; python3 $q.py 2>&1 | grep -v Warn | tail -4; done
mkdir -p $DIZAI_OUTI && cp $DIZAI_OUT/{outlines,spacing,kerning,ref_ratios}.json $DIZAI_OUTI/
python3 export_font.py > $DIZAI_OUT/export.log 2>&1; tail -3 $DIZAI_OUT/export.log
PV_OUT=$DIZAI_OUT PV_OUTI=$DIZAI_OUTI PV_FONTS=$DIZAI_FONTS PV_PS=AnNamGolden PV_NAME="AnNam Golden" PV_HTML=annam-golden.html PV_XH=535 PV_GUIDES=0 python3 preview_html.py | cut -c1-120
echo DONE
(cd "$(git rev-parse --show-toplevel)" && python3 tools/construct/qa_lines.py tools/construct/qa_ref/AnNamSerif-v0918-%s.otf fonts/golden/otf/AnNamGolden-%s.otf --xh=535 | grep -v "^    ")
(cd "$(git rev-parse --show-toplevel)" && python3 tools/construct/qa_bars.py fonts/golden/otf/AnNamGolden-%s.otf 42 56.5 AEFHLTZeftz)
(cd "$(git rev-parse --show-toplevel)" && python3 tools/construct/qa_arms.py fonts/golden/otf/AnNamGolden-%s.otf)
