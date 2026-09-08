"""Deck content and layout, defined once.

Both renderers consume this. The coordinate system is inches on a 13.333 x 7.5
slide, which is also 1280 x 720 CSS pixels at 96dpi -- so the PPTX and the PDF
are laid out from the same numbers rather than from two descriptions that drift.
"""

W, H = 13.333, 7.5

# Deep slate and teal: an instrument-panel palette rather than a corporate blue.
INK    = "16232B"   # near-black slate, dark grounds
INK2   = "22343E"   # raised dark surface
TEAL   = "00A896"   # primary accent
TEAL_D = "017F73"   # accent, pressed
AMBER  = "E0A458"   # findings, attention
CORAL  = "C05B5B"   # failure / destructive
WHITE  = "FFFFFF"
MIST   = "EEF2F3"   # light surface
MIST2  = "E971F4"   # (unused sentinel)
LINE   = "D3DBDE"
MUTED  = "62798A"

HEAD = "Cambria"
BODY = "Calibri"
MONO = "Courier New"

def R(x, y, w, h, fill=None, radius=0, line=None, lw=1, shadow=False):
    return dict(k="rect", x=x, y=y, w=w, h=h, fill=fill, radius=radius,
                line=line, lw=lw, shadow=shadow)

def T(x, y, w, h, text, size=14, bold=False, color=INK, align="l", va="t",
      font=None, lh=1.22, italic=False):
    return dict(k="text", x=x, y=y, w=w, h=h, text=text, size=size, bold=bold,
                color=color, align=align, va=va, font=font or BODY, lh=lh,
                italic=italic)

def B(x, y, w, h, items, size=13, color=INK, gap=0.30, dot=TEAL):
    return dict(k="bullets", x=x, y=y, w=w, h=h, items=items, size=size,
                color=color, gap=gap, dot=dot)

def L(x1, y1, x2, y2, color=LINE, w=1.25, dash=False):
    return dict(k="line", x1=x1, y1=y1, x2=x2, y2=y2, color=color, w=w, dash=dash)

def C(x, y, d, fill, text=None, color=WHITE, size=13, bold=True):
    return dict(k="circle", x=x, y=y, d=d, fill=fill, text=text, color=color,
                size=size, bold=bold)

def title_block(t, sub=None, y=0.52):
    out = [T(0.75, y, 11.9, 0.62, t, size=32, bold=True, color=INK, font=HEAD)]
    if sub:
        out.append(T(0.75, y + 0.62, 11.9, 0.34, sub, size=14, color=MUTED))
    return out

def card(x, y, w, h, head, body, accent=TEAL, hsize=15, bsize=12):
    return [
        R(x, y, w, h, fill=WHITE, radius=0.09, line=LINE, shadow=True),
        R(x + 0.30, y + 0.30, 0.11, 0.11, fill=accent, radius=0.055),
        T(x + 0.52, y + 0.20, w - 0.85, 0.32, head, size=hsize, bold=True, font=HEAD),
        T(x + 0.30, y + 0.62, w - 0.60, h - 0.80, body, size=bsize, color=MUTED, lh=1.32),
    ]

def stat(x, y, w, value, label, color=TEAL):
    return [
        T(x, y, w, 0.78, value, size=44, bold=True, color=color, font=HEAD, align="l"),
        T(x, y + 0.80, w, 0.30, label, size=11.5, color=MUTED, align="l"),
    ]

def chip(x, y, w, h, text, fill, color=WHITE, size=11.5, bold=True):
    return [R(x, y, w, h, fill=fill, radius=h / 2),
            T(x, y, w, h, text, size=size, bold=bold, color=color, align="c", va="c")]
