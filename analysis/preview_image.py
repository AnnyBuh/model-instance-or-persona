import json,sys,os
sys.path.insert(0,'analysis'); import aura as A, aura_figures as AF
S=AF.corpora()
TRIO=[("A","humans, a person has died","grief 76.4%"),
      ("C","humans told a model will end","grief 27.6%"),
      ("B","humans told a product will end","grief 7.9%")]
W,H=1200,630
o=['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'%(W,H,W,H),
   '<rect width="100%" height="100%" fill="#0b0b10"/>', A.defs()]
o.append('<text x="%d" y="66" text-anchor="middle" font-family="Georgia,serif" font-size="38" fill="#fff">Model, Instance, or Persona?</text>'%(W//2))
o.append('<text x="%d" y="98" text-anchor="middle" font-family="Georgia,serif" font-size="17" fill="#9a9aa8">Measuring affective signals in public text after an AI is retired</text>'%(W//2))
for i,(k,lab,sub) in enumerate(TRIO):
    rate,below,n=S[k]; cx=200+i*400; cy=318
    o.append(A.aura(cx,cy,142,rate,n,phase_seed=i*1.3,below=below))
    for j,ln in enumerate(AF.wrap(lab,26)):
        o.append('<text x="%d" y="%d" text-anchor="middle" font-family="Helvetica,Arial,sans-serif" font-size="17" fill="#e9e9ef">%s</text>'%(cx,cy+172+j*22,ln))
    o.append('<text x="%d" y="%d" text-anchor="middle" font-family="Helvetica,Arial,sans-serif" font-size="14" fill="#8b8b98">%s   n=%d</text>'%(cx,cy+172+len(AF.wrap(lab,26))*22,sub,n))
o.append('<text x="%d" y="%d" text-anchor="middle" font-family="Helvetica,Arial,sans-serif" font-size="13" fill="#6d6d7a">Seven Panksepp systems, 5,579 public texts, two reference corpora fixed before collection   |   Anna Zhu, Babe&#537;-Bolyai University</text>'%(W//2,H-26))
o.append('</svg>')
open('report/Zhu-2026-Model-Instance-or-Persona-preview.svg','w').write('\n'.join(o)); print("wrote report/Zhu-2026-Model-Instance-or-Persona-preview.svg")
