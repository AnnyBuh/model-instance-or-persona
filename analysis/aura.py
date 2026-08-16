"""Render an affective aura per corpus, in the instrument's visual language, as print-safe SVG.

    python3 analysis/aura.py            # writes report/fig4-auras.svg and report/project-image.svg

The iris in the source application is a canvas renderer with animation, ripple counts driven by commenters, and an
altitude core. None of that survives a print page, so this is a deliberate reduction rather than a
port, and the mapping is stated in the figure caption because a picture whose axes are not declared is
decoration.

What carries meaning here, and nothing else does:

    ring colour      the affective system, in the instrument's own system colours
    ring radius      the rate: share of texts in that corpus in which the system fired
    edge waviness    dysregulation: the share of that system's signals coded below the line,
                     either shutdown or overwhelm, rather than above it. This is the source application's `below`
                     tear rule. The shipped rule there instead tears the negative systems by
                     category, which encodes nothing colour does not already say, so it is not
                     used here.
    ripple count     corpus size, log-scaled, so a 56-post corpus is visibly not a 1,586-comment one

Rings are drawn largest first so the strongest system sits backmost, as in the original. Everything is
additive light on a dark ground, so each aura sits on its own dark square on a white page, as the eye
does in the source application. The ground is square rather than round because a circular ground reads as
another ring and competes with the outermost system for the eye.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SYS = ["seeking", "rage", "fear", "lust", "care", "grief", "play"]
COL = {"seeking": "#e0aa12", "rage": "#e0463a", "fear": "#2bb56a", "lust": "#e06aa0",
       "care": "#4a90d9", "grief": "#9166e6", "play": "#8fce2a"}

GROUND = "#0b0b10"


def ripples(n):
    """Corpus size to ripple count, log-scaled and clamped, in the spirit of the source application's ripple ceiling."""
    if n <= 0:
        return 5
    return int(max(5, min(26, round(5 + 21 * math.log(max(n, 20) / 20) / math.log(1600 / 20)))))


def ring_path(cx, cy, r, bumps, amp, phase):
    """A closed wavy circle. amp is a fraction of r, matching the source application's 0.045 floor and 0.135 ceiling."""
    steps = max(180, bumps * 24)
    pts = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        rr = r * (1 + amp * math.sin(bumps * t + phase))
        pts.append((cx + rr * math.cos(t), cy + rr * math.sin(t)))
    d = "M %.2f %.2f " % pts[0] + " ".join("L %.2f %.2f" % p for p in pts[1:]) + " Z"
    return d


def aura(cx, cy, R, rates, n, phase_seed=0, below=None):
    """One aura. rates is {system: 0..1}; below is {system: 0..1}, the dysregulated share."""
    below = below or {}
    order = sorted(SYS, key=lambda s: -rates.get(s, 0.0))
    mx = max([rates.get(s, 0.0) for s in SYS] + [1e-9])
    bumps = ripples(n)
    side = 2 * R
    out = ['<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="%s"/>'
           % (cx - R, cy - R, side, side, R * 0.07, GROUND)]
    out.append('<g style="mix-blend-mode:screen">')
    for rank, s in enumerate(order):
        v = rates.get(s, 0.0)
        if v <= 0.002:
            continue
        # Radius carries the square root of the share, so area is proportional, with a floor that
        # keeps two near-equal systems from collapsing into one disc. Same shape as the source application's proportional sizing.
        amp = 0.045 + 0.135 * max(0.0, min(1.0, below.get(s, 0.0)))
        # Keep the wave crests inside the dark ground: the old version sized rings to the disc
        # radius, so every outer crest was clipped by the edge of the disc.
        frac = 0.22 + 0.72 * math.sqrt(v / mx)
        r = R * min(0.92, frac) / (1 + amp)
        phase = (phase_seed + rank * 1.7) % (2 * math.pi)
        d = ring_path(cx, cy, r, bumps, amp, phase)
        out.append('<path d="%s" fill="%s" opacity="0.42" filter="url(#soft)"/>' % (d, COL[s]))
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.1" opacity="0.85"/>'
                   % (d, COL[s]))
    out.append("</g>")
    return "\n".join(out)


def defs():
    return ('<defs><filter id="soft" x="-30%" y="-30%" width="160%" height="160%">'
            '<feGaussianBlur stdDeviation="3.2"/></filter></defs>')


def legend(x, y, gap=86):
    out = []
    for i, s in enumerate(SYS):
        cx = x + i * gap
        out.append('<circle cx="%.1f" cy="%.1f" r="4.2" fill="%s"/>' % (cx, y, COL[s]))
        out.append('<text x="%.1f" y="%.1f" font-family="Helvetica,Arial,sans-serif" '
                   'font-size="11" fill="#444">%s</text>' % (cx + 9, y + 4, s))
    return "\n".join(out)


def load_rates():
    """Per-corpus rate per system, from the committed full-rates file."""
    d = json.load(open(os.path.join(ROOT, "data/full-rates.json")))
    return d


if __name__ == "__main__":
    print(json.dumps(load_rates(), indent=1)[:1200])
