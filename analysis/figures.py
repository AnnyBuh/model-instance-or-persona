"""Build the three report figures as standalone SVG, sized for print.

    python3 analysis/figures.py

Figures are static because the deliverable is a PDF. Every mark is directly labelled, which is also
the relief the palette validator asks for on the aqua slot, and the report carries the full tables so
no value is available only as a colour.

Palette: validated categorical slots 1 to 3 (blue, orange, aqua), fixed order, never cycled.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rates  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "report")

INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#8a8880"
GRID = "#e6e5e0"
SURFACE = "#fcfcfb"
SERIES = {"A": "#2a78d6", "B": "#eb6834", "C": "#1baf7a"}
NAMES = {"A": "bereavement", "B": "consumer loss", "C": "AI loss"}
FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load_rates():
    reads, cmap = [], {}
    for stage in ("stage1", "stage2", "stage3"):
        d = os.path.join(ROOT, "data", stage)
        for name in sorted(os.listdir(os.path.join(d, "reads"))):
            if name.endswith(".reads.json"):
                reads.extend(json.load(open(os.path.join(d, "reads", name))))
        cmap.update({int(k): v for k, v in json.load(open(os.path.join(d, "corpus-map.json"))).items()})
    return rates.corpus_rates(reads, cmap)


# --------------------------------------------------------------- figure 1: the placement
def fig_placement(R):
    W, H = 760, 280
    L, Rt, T = 150, 60, 70
    plot = W - L - Rt
    x = lambda v: L + plot * v / 100.0
    s = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
         'font-family="%s">' % (W, H, W, H, FONT),
         '<rect width="%d" height="%d" fill="%s"/>' % (W, H, SURFACE),
         '<text x="%d" y="28" font-size="15" font-weight="600" fill="%s">Where AI loss sits, on GRIEF</text>' % (L - 110, INK),
         '<text x="%d" y="48" font-size="12" fill="%s">share of comments in which the GRIEF system fired, with 90%% intervals</text>' % (L - 110, INK2)]
    for v in range(0, 101, 20):  # recessive grid
        s.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="1"/>'
                 % (x(v), T, x(v), T + 128, GRID))
        s.append('<text x="%.1f" y="%d" font-size="11" fill="%s" text-anchor="middle">%d%%</text>'
                 % (x(v), T + 148, MUTED, v))
    order = ["B", "C", "A"]
    for i, c in enumerate(order):
        r = R[c]["rates"]["grief"]
        y = T + 24 + i * 40
        lo, hi, val = 100 * r["lo"], 100 * r["hi"], 100 * r["rate"]
        s.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2" '
                 'stroke-linecap="round"/>' % (x(lo), y, x(hi), y, SERIES[c]))
        s.append('<circle cx="%.1f" cy="%.1f" r="6" fill="%s" stroke="%s" stroke-width="2"/>'
                 % (x(val), y, SERIES[c], SURFACE))
        s.append('<text x="%d" y="%.1f" font-size="12.5" fill="%s" text-anchor="end">%s</text>'
                 % (L - 14, y + 4, INK, esc(NAMES[c])))
        s.append('<text x="%d" y="%.1f" font-size="10.5" fill="%s" text-anchor="end">n=%d</text>'
                 % (L - 14, y + 18, MUTED, R[c]["read"]))
        s.append('<text x="%.1f" y="%.1f" font-size="12.5" font-weight="600" fill="%s">%.1f%%</text>'
                 % (x(hi) + 10, y + 4, INK, val))
    s.append('<text x="%d" y="%d" font-size="11.5" fill="%s">Every condition was written down before '
             'collection: above consumer loss, below bereavement, closer to consumer loss.</text>'
             % (L - 110, H - 16, INK2))
    s.append("</svg>")
    return "\n".join(s)


# --------------------------------------------------------------- figure 2: the seven systems
def fig_systems(R):
    W = 760
    rowh, grp = 26, 96
    H = 90 + grp * 7 + 30
    L, Rt = 130, 90
    plot = W - L - Rt
    x = lambda v: L + plot * v / 100.0
    s = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
         'font-family="%s">' % (W, H, W, H, FONT),
         '<rect width="%d" height="%d" fill="%s"/>' % (W, H, SURFACE),
         '<text x="20" y="26" font-size="15" font-weight="600" fill="%s">The shape of each corpus, on seven systems</text>' % INK,
         '<text x="20" y="46" font-size="12" fill="%s">AI loss is not miniature bereavement. It is consumer-level anger, carried through jokes, with grief underneath.</text>' % INK2]
    lx = 20
    for c in ("A", "B", "C"):  # legend, always present for 3 series
        s.append('<rect x="%d" y="58" width="10" height="10" rx="2" fill="%s"/>' % (lx, SERIES[c]))
        s.append('<text x="%d" y="67" font-size="11.5" fill="%s">%s</text>' % (lx + 15, INK2, esc(NAMES[c])))
        lx += 22 + 7 * len(NAMES[c])
    top = 92
    for j, sysname in enumerate(rates.SYSTEMS):
        gy = top + j * grp
        s.append('<text x="%d" y="%d" font-size="12.5" font-weight="600" fill="%s" text-anchor="end">%s</text>'
                 % (L - 14, gy + 30, INK, sysname))
        for i, c in enumerate(("A", "B", "C")):
            r = R[c]["rates"][sysname]
            v = 100 * r["rate"]
            y = gy + i * rowh
            s.append('<rect x="%d" y="%.1f" width="%.1f" height="%d" rx="4" fill="%s"/>'
                     % (L, y, max(2.0, x(v) - L), rowh - 8, SERIES[c]))  # 2px gap via height
            s.append('<text x="%.1f" y="%.1f" font-size="11.5" fill="%s">%.1f%%</text>'
                     % (x(v) + 8, y + 13, INK, v))
        s.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="1"/>'
                 % (L, gy + grp - 14, W - Rt + 40, gy + grp - 14, GRID))
    s.append("</svg>")
    return "\n".join(s)


# --------------------------------------------------------------- figure 3: what was lost
def fig_entity(counts, n):
    W, H = 760, 300
    L, Rt, T = 150, 90, 84
    plot = W - L - Rt
    order = ["none", "model", "persona", "instance", "unspecified"]
    mx = max(counts.get(k, 0) for k in order) or 1
    x = lambda v: L + plot * v / mx
    s = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
         'font-family="%s">' % (W, H, W, H, FONT),
         '<rect width="%d" height="%d" fill="%s"/>' % (W, H, SURFACE),
         '<text x="20" y="26" font-size="15" font-weight="600" fill="%s">What the words say was lost</text>' % INK,
         '<text x="20" y="46" font-size="12" fill="%s">%d AI-loss comments, coded blind, one label each, verbatim evidence required</text>' % (INK2, n),
         '<text x="20" y="64" font-size="12" fill="%s">Most name no counterpart at all. Among those that do, the version beats the particular one.</text>' % INK2]
    for i, k in enumerate(order):
        v = counts.get(k, 0)
        y = T + i * 40
        s.append('<rect x="%d" y="%d" width="%.1f" height="24" rx="4" fill="%s"/>'
                 % (L, y, max(2.0, x(v) - L), "#2a78d6" if k != "none" else "#b9c6d6"))
        s.append('<text x="%d" y="%d" font-size="12.5" fill="%s" text-anchor="end">%s</text>'
                 % (L - 14, y + 17, INK, k))
        s.append('<text x="%.1f" y="%d" font-size="12.5" font-weight="600" fill="%s">%d  (%.0f%%)</text>'
                 % (x(v) + 10, y + 17, INK, v, 100.0 * v / n))
    s.append("</svg>")
    return "\n".join(s)


def main():
    R = load_rates()
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "fig1-placement.svg"), "w").write(fig_placement(R))
    open(os.path.join(OUT, "fig2-systems.svg"), "w").write(fig_systems(R))
    ent_dir = os.path.join(ROOT, "data", "entity")
    counts, n = {}, 0
    if os.path.isdir(ent_dir):
        for f in sorted(os.listdir(ent_dir)):
            if f.endswith(".entity.json"):
                for r in json.load(open(os.path.join(ent_dir, f))):
                    counts[r["label"]] = counts.get(r["label"], 0) + 1
                    n += 1
    if n:
        open(os.path.join(OUT, "fig3-entity.svg"), "w").write(fig_entity(counts, n))
    print("figures written to report/ (entity n=%d)" % n)


if __name__ == "__main__":
    main()
