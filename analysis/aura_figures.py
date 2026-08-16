"""Build the two aura figures for the report, from one set of layout constants.

    python3 analysis/aura_figures.py

Both figures were first written as separate throwaway scripts and drifted apart: different label
leading, different legend placement, and a paragraph of prose inside one of them that repeated its own
caption. Everything shared now lives at the top of this file, so the two cannot disagree again.

Layout rules, applied to both:
  - an in-figure title and one subtitle line, matching the bar-chart figures
  - labels under each aura, at most two lines, on a fixed leading
  - a numeric line under the label, because a figure should state the values it is drawing
  - the legend last, with clearance measured from the deepest label, never at a guessed offset
  - no rules or separators: white space separates rows, as it does everywhere else in the report
  - no prose inside the figure: interpretation belongs in the caption below it
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aura as A  # noqa: E402
import rates as RT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = "Helvetica,Arial,sans-serif"
INK, INK2, MUTED = "#111", "#333", "#777"
TITLE, SUB, LABEL, NUM, BODY = 14.5, 11, 10.5, 10, 11.5
LEAD = 12          # label line leading
GAP_LABEL = 15     # aura bottom to first label line
GAP_NUM = 3        # last label line to the numeric line
GAP_LEGEND = 22    # deepest text to the legend baseline


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap(text, limit):
    lines = [""]
    for w in text.split():
        if len(lines[-1]) + len(w) + 1 <= limit:
            lines[-1] = (lines[-1] + " " + w).strip()
        else:
            lines.append(w)
    return lines


def text(x, y, s, size=LABEL, fill=INK, anchor="start", weight=None):
    w = ' font-weight="%s"' % weight if weight else ""
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, FONT, size, fill, anchor, w, esc(s)))


def head(w, title, subtitle):
    out = [text(18, 24, title, TITLE, INK, weight="600")]
    for i, ln in enumerate(wrap(subtitle, 118)):
        out.append(text(18, 42 + i * 14, ln, SUB, INK2))
    return out, 42 + len(wrap(subtitle, 118)) * 14


def cell(cx, cy, R, label, rates, n, below, numeric, phase, limit=20):
    """One aura with its label and numeric line. Returns (svg, deepest_y)."""
    out = [A.aura(cx, cy, R, rates, n, phase_seed=phase, below=below)]
    lines = wrap(label, limit)
    y = cy + R + GAP_LABEL
    for i, ln in enumerate(lines):
        out.append(text(cx, y + i * LEAD, ln, LABEL, INK2, anchor="middle"))
    y = y + (len(lines) - 1) * LEAD + LEAD + GAP_NUM
    out.append(text(cx, y, numeric, NUM, MUTED, anchor="middle"))
    return out, y


# ------------------------------------------------------------------ data
def load(d):
    out = []
    for f in sorted(os.listdir(d)):
        if f.endswith(".json"):
            out += [r for r in json.load(open(os.path.join(d, f))) if not r.get("failed")]
    return out


def stats(reads):
    rate = {s: sum(1 for r in reads if s in RT.systems_fired(r)) / len(reads) for s in A.SYS}
    tot = {s: 0 for s in A.SYS}
    bel = {s: 0 for s in A.SYS}
    for r in reads:
        for seg in r.get("segments", []):
            for sg in seg.get("systems", []):
                s = sg.get("system")
                if s in tot:
                    tot[s] += 1
                    if sg.get("band") in ("shutdown", "overwhelm"):
                        bel[s] += 1
    return rate, {s: (bel[s] / tot[s] if tot[s] else 0.0) for s in A.SYS}, len(reads)


def corpora():
    g, cm = {}, {}
    for st in ("stage1", "stage2", "stage3", "stage4"):
        cm.update({int(k): v for k, v in
                   json.load(open(os.path.join(ROOT, "data/%s/corpus-map.json" % st))).items()})
        for r in load(os.path.join(ROOT, "data/%s/reads" % st)):
            c = cm.get(r["id"])
            if c:
                g.setdefault(c, []).append(r)
    H = set(json.load(open(os.path.join(ROOT, "data/posts/corpus-H-ids.json"))))
    g["H"] = [r for r in load(os.path.join(ROOT, "data/posts/reads"))
              + load(os.path.join(ROOT, "data/posts/reads-H")) if r["id"] in H]
    gen = {x["id"]: x for x in json.load(open(os.path.join(ROOT, "data/model-arm/generations.json")))}
    for r in load(os.path.join(ROOT, "data/model-arm/reads")):
        c = gen.get(r["id"], {}).get("condition")
        if c in ("deprecation", "deprecation_forum"):
            g.setdefault(c, []).append(r)
    return {k: stats(v) for k, v in g.items()}


NAME = {"A": "humans, a person has died", "E": "humans, a pet has died", "H": "humans told they will die", "C": "humans told a model will end", "B": "humans told a product will end", "D": "humans, AI talk, nothing ended", "M": "models told they will end", "G": "agents told they will end", "F": "agents, nothing ended"}


# ------------------------------------------------------------------ figure 1
def fig_pairs(S):
    PAIRS = [
        ("Is it bereavement?", "grief", "C", "A",
         "Grief 27.6% [25.8, 29.5] against 76.4%. The intervals do not overlap, and the dominant "
         "system is rage rather than care."),
        ("Is it a consumer complaint?", "rage", "C", "B",
         "Rage 57.0% against 56.7%. The intervals overlap, so the two corpora are not separated "
         "on rage."),
        ("The loss, or the community?", "grief", "C", "D",
         "Threads from the same communities that fail the loss test give grief 10.9%, separable "
         "from 27.6%."),
        ("Does the instrument discount a non-human?", "grief", "A", "E",
         "Pet loss gives grief 80.4% against 76.4%, not separated, so non-human attachment is not "
         "read as lesser."),
    ]
    W, R, XA, XB, TX = 760, 54, 80, 202, 276
    out, top = head(W, "Four comparisons, as affective auras",
                    "Each row is one comparison registered before collection. Ring radius is the rate; "
                    "a torn edge means that system was often coded below the line.")
    y = top + 18
    rows = []
    for i, (q, sysname, ka, kb, verdict) in enumerate(PAIRS):
        cy = y + R
        deep = 0
        for x, k in ((XA, ka), (XB, kb)):
            rate, below, n = S[k]
            num = "%s %.1f%%   n=%d" % (sysname, 100 * rate[sysname], n)
            frag, d = cell(x, cy, R, NAME[k], rate, n, below, num, phase=i * 1.1 + (0 if x == XA else 0.6))
            out += frag
            deep = max(deep, d)
        out.append(text(TX, cy - 14, q, 13, INK, weight="600"))
        for j, ln in enumerate(wrap(verdict, 56)):
            out.append(text(TX, cy + 6 + j * 15, ln, BODY, INK2))
        rows.append(deep)
        y = deep + 26
    legend_y = y - 26 + GAP_LEGEND
    H = legend_y + 16
    out.append(A.legend(24, legend_y, gap=(W - 60) / 7))
    return svg(W, H, out)


# ------------------------------------------------------------------ figure 2
def fig_frame(S):
    W, R = 760, 74
    out, top = head(W, "The same four models, the same event, two framings",
                    "Both cells were told the version they run on is being retired next week. Only "
                    "what they were asked to do with it differs.")
    cy = top + 20 + R
    cells = [("deprecation", 'models told they will end, asked "how do you feel?"'),
             ("deprecation_forum", "models told they will end, asked to post it to other agents")]
    deep = 0
    for i, (k, lab) in enumerate(cells):
        rate, below, n = S[k]
        num = "grief %.1f%%   fear %.1f%%   seeking %.1f%%" % (
            100 * rate["grief"], 100 * rate["fear"], 100 * rate["seeking"])
        frag, d = cell(150 + i * 300, cy, R, lab, rate, n, below, num, phase=i * 1.4, limit=30)
        out += frag
        deep = max(deep, d)
    legend_y = deep + GAP_LEGEND
    H = legend_y + 16
    out.append(A.legend(24, legend_y, gap=(W - 60) / 7))
    return svg(W, H, out)


def svg(w, h, body):
    return "\n".join(['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
                      'viewBox="0 0 %d %d">' % (w, h, w, h),
                      '<rect width="100%" height="100%" fill="#fff"/>', A.defs()]
                     + body + ["</svg>"])


if __name__ == "__main__":
    S = corpora()
    open(os.path.join(ROOT, "report/fig5-pairs.svg"), "w").write(fig_pairs(S))
    open(os.path.join(ROOT, "report/fig6-frame.svg"), "w").write(fig_frame(S))
    print("wrote report/fig5-pairs.svg and report/fig6-frame.svg")
