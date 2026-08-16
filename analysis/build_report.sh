set -e
cd /Users/annazhu/Documents/VibeCoding/apartresearch
python3 -c "
h=open('report/main.html').read()
for k,f in (('__FIG1__','fig1-placement.svg'),('__FIG2__','fig2-systems.svg'),('__FIG5__','fig5-pairs.svg'),('__FIG6__','fig6-frame.svg')):
    h=h.replace(k,open('report/'+f).read())
open('report/main.built.html','w').write(h)"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="report/Zhu-2026-Model-Instance-or-Persona.pdf" \
  "file:///Users/annazhu/Documents/VibeCoding/apartresearch/report/main.built.html" 2>/dev/null
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --window-size=1200,630 \
  --screenshot="report/Zhu-2026-Model-Instance-or-Persona-preview.png" \
  "file:///Users/annazhu/Documents/VibeCoding/apartresearch/report/Zhu-2026-Model-Instance-or-Persona-preview.svg" 2>/dev/null
