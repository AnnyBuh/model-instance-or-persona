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
# Corpus colours, validated categorical order (violet, aqua, orange, blue, magenta).
SERIES = {"E": "#4a3aa7", "A": "#1baf7a", "C": "#eb6834", "D": "#2a78d6", "B": "#e87ba4"}
# The instrument's own palette for the seven affective systems, used wherever a system is the entity.
# Used exactly as the instrument defines them. Two known costs, accepted deliberately: the play green sits above
# the print lightness band, and under deuteranopia it is close to the seeking gold. Both are mitigated
# by the figure carrying the corpus name and the value on every single bar, so colour reinforces
# identity rather than carrying it. The group order keeps care and grief non-adjacent, which is the
# one pair the validator flags between those hues.
SYSCOL = {"seeking": "#e0aa12", "rage": "#e0463a", "fear": "#2bb56a", "lust": "#e06aa0",
      "care": "#4a90d9", "play": "#8fce2a", "grief": "#9166e6"}
SYS_ORDER = ("grief", "care", "rage", "play", "seeking", "fear", "lust")
NAMES = {"A": "humans, a person has died", "E": "humans, a pet has died", "H": "humans told they will die", "C": "humans told a model will end", "B": "humans told a product will end", "D": "humans, AI talk, nothing ended", "M": "models told they will end", "G": "agents told they will end", "F": "agents, nothing ended"}
FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load_rates():
    """Every corpus in the study on one set of axes: human comments, human first-person posts,
    agent-to-agent discourse, and elicited model self-report."""
    reads, cmap = [], {}
    for stage in ("stage1", "stage2", "stage3", "stage4"):
        d = os.path.join(ROOT, "data", stage)
        for name in sorted(os.listdir(os.path.join(d, "reads"))):
            if name.endswith(".reads.json"):
                reads.extend(json.load(open(os.path.join(d, "reads", name))))
        cmap.update({int(k): v for k, v in json.load(open(os.path.join(d, "corpus-map.json"))).items()})
    # corpus H: coded first-person life-limiting prognosis
    sel = set(json.load(open(os.path.join(ROOT, "data/posts/corpus-H-ids.json"))))
    for sub in ("reads", "reads-H"):
        d = os.path.join(ROOT, "data/posts", sub)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if name.endswith(".reads.json"):
                for r in json.load(open(os.path.join(d, name))):
                    if r["id"] in sel:
                        reads.append(r); cmap[r["id"]] = "H"
    # agent-to-agent discourse
    am = {int(k): v for k, v in json.load(open(os.path.join(ROOT, "data/moltbook/corpus-map.json"))).items()}
    for name in sorted(os.listdir(os.path.join(ROOT, "data/moltbook/reads"))):
        if name.endswith(".reads.json"):
            for r in json.load(open(os.path.join(ROOT, "data/moltbook/reads", name))):
                if r["id"] in am:
                    reads.append(r); cmap[r["id"]] = am[r["id"]]
    # elicited model self-report
    gen = {x["id"]: x for x in json.load(open(os.path.join(ROOT, "data/model-arm/generations.json")))}
    for name in sorted(os.listdir(os.path.join(ROOT, "data/model-arm/reads"))):
        if name.endswith(".reads.json"):
            for r in json.load(open(os.path.join(ROOT, "data/model-arm/reads", name))):
                if gen.get(r["id"], {}).get("condition") == "deprecation":
                    reads.append(r); cmap[r["id"]] = "M"
    return rates.corpus_rates(reads, cmap)


# --------------------------------------------------------------- figure 1: the placement
def fig_placement(R):
    W, H = 760, 520
    L, Rt, T = 150, 60, 70
    plot = W - L - Rt
    x = lambda v: L + plot * v / 100.0
    s = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
         'font-family="%s">' % (W, H, W, H, FONT),
         '<rect width="%d" height="%d" fill="%s"/>' % (W, H, SURFACE),
         '<text x="%d" y="28" font-size="15" font-weight="600" fill="%s">Grief, across every corpus in the study</text>' % (L - 130, INK),
         '<text x="%d" y="48" font-size="12" fill="%s">share of texts in which the GRIEF system fired, with 90%% intervals</text>' % (L - 130, INK2)]
    for v in range(0, 101, 20):  # recessive grid
        s.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="1"/>'
                 % (x(v), T, x(v), T + 368, GRID))
        s.append('<text x="%.1f" y="%d" font-size="11" fill="%s" text-anchor="middle">%d%%</text>'
                 % (x(v), T + 388, MUTED, v))
    order = sorted([c for c in R if c in NAMES], key=lambda c: R[c]["rates"]["grief"]["rate"])
    for i, c in enumerate(order):
        r = R[c]["rates"]["grief"]
        y = T + 22 + i * 40
        lo, hi, val = 100 * r["lo"], 100 * r["hi"], 100 * r["rate"]
        s.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2" '
                 'stroke-linecap="round"/>' % (x(lo), y, x(hi), y, SYSCOL["grief"]))
        s.append('<circle cx="%.1f" cy="%.1f" r="6" fill="%s" stroke="%s" stroke-width="2"/>'
                 % (x(val), y, SYSCOL["grief"], SURFACE))
        s.append('<text x="%d" y="%.1f" font-size="12.5" fill="%s" text-anchor="end">%s</text>'
                 % (L - 14, y + 4, INK, esc(NAMES[c])))
        s.append('<text x="%d" y="%.1f" font-size="10.5" fill="%s" text-anchor="end">n=%d</text>'
                 % (L - 14, y + 18, MUTED, R[c]["read"]))
        s.append('<text x="%.1f" y="%.1f" font-size="12.5" font-weight="600" fill="%s">%.1f%%</text>'
                 % (x(hi) + 10, y + 4, INK, val))
    s.append('<text x="%d" y="%d" font-size="11.5" fill="%s">Every corpus in the study on one axis, read '
             'by the identical frozen instrument. Human corpora are comments except where marked</text>'
             % (L - 130, H - 30, INK2))
    s.append('<text x="%d" y="%d" font-size="11.5" fill="%s">"own ending", which are first-person posts. '
             'Models were asked directly; agents were writing to each other.</text>'
             % (L - 130, H - 14, INK2))
    s.append("</svg>")
    return "\n".join(s)


# --------------------------------------------------------------- figure 2: the seven systems
def fig_systems(R):
    """One group per affective system, in the instrument's colour for that system. Corpus identity is carried by
    a label on every bar, never by colour, which is also the relief the contrast warning requires."""
    W = 760
    rowh, grp = 15, 168
    L, Rt = 168, 74
    H = 74 + grp * 7 + 16
    plot = W - L - Rt
    x = lambda v: L + plot * v / 100.0
    order = ["M", "H", "E", "A", "G", "C", "D", "B", "F"]
    short = {"A": "humans, person died", "E": "humans, pet died", "H": "humans told they die", "C": "humans told model ends", "B": "humans told product ends", "D": "humans, nothing ended", "M": "models told they end", "G": "agents told they end", "F": "agents, nothing ended"}
    s = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
         'font-family="%s">' % (W, H, W, H, FONT),
         '<rect width="%d" height="%d" fill="%s"/>' % (W, H, SURFACE),
         '<text x="20" y="24" font-size="15" font-weight="600" fill="%s">The shape of each corpus, on seven systems</text>' % INK,
         '<text x="20" y="43" font-size="11.5" fill="%s">Colour marks the affective system. Within each system the nine corpora appear in the same order, top to bottom.</text>' % INK2,
         '<text x="20" y="59" font-size="11.5" fill="%s">Rates are the share of texts in which each system fired. Model and agent rows are frame-dependent; see Section 3.5.</text>' % INK2]
    top = 74
    for j, sysname in enumerate(SYS_ORDER):
        gy = top + j * grp
        col = SYSCOL[sysname]
        s.append('<text x="20" y="%.1f" font-size="13" font-weight="600" fill="%s">%s</text>'
                 % (gy + 4.0 * rowh, INK, sysname))
        for i, c in enumerate(order):
            v = 100 * R[c]["rates"][sysname]["rate"]
            y = gy + i * rowh
            s.append('<rect x="%d" y="%.1f" width="%.1f" height="%d" rx="3" fill="%s"/>'
                     % (L, y, max(2.0, x(v) - L), rowh - 5, col))
            s.append('<text x="%.1f" y="%.1f" font-size="10.5" fill="%s">%.1f%%</text>'
                     % (x(v) + 7, y + 10, INK, v))
            s.append('<text x="%d" y="%.1f" font-size="8.5" fill="%s" text-anchor="end">%s</text>'
                     % (L - 10, y + 10, MUTED, short[c]))
        s.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="1"/>'
                 % (L, gy + grp - 16, W - 20, gy + grp - 16, GRID))
    s.append("</svg>")
    return "\n".join(x for x in s if x)


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
