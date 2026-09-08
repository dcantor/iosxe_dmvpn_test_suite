"""Render the same slide model to HTML, one page per slide, for Chrome to print.

Same inches, multiplied by 96 to give CSS pixels, so the PDF and the PPTX are
laid out from identical numbers.
"""
import sys, html
from content import W, H, MONO
from slides import S

PX = 96.0
FONTS = {
    "Cambria": "Cambria, 'Bookman Old Style', Georgia, serif",
    "Calibri": "Calibri, 'Segoe UI', 'DejaVu Sans', Arial, sans-serif",
    "Courier New": "'Courier New', 'DejaVu Sans Mono', monospace",
}
ALIGN = {"l": "left", "c": "center", "r": "right"}
VA = {"t": "flex-start", "c": "center", "b": "flex-end"}

def esc(s):
    return html.escape(s).replace("\n", "<br>")

def px(v):
    return f"{v * PX:.2f}px"

def render(e):
    k = e["k"]
    if k == "rect":
        st = [f"left:{px(e['x'])}", f"top:{px(e['y'])}", f"width:{px(e['w'])}",
              f"height:{px(e['h'])}"]
        st.append(f"background:#{e['fill']}" if e["fill"] else "background:transparent")
        if e["radius"]:
            st.append(f"border-radius:{px(e['radius'])}")
        if e["line"]:
            st.append(f"box-shadow:inset 0 0 0 {e['lw']}px #{e['line']}")
        if e["shadow"]:
            st.append("filter:drop-shadow(0 1px 2px rgba(22,35,43,.10))")
        return f'<div class="b" style="{";".join(st)}"></div>'
    if k == "text":
        st = [f"left:{px(e['x'])}", f"top:{px(e['y'])}", f"width:{px(e['w'])}",
              f"height:{px(e['h'])}", f"font-size:{e['size']}pt",
              f"color:#{e['color']}", f"font-family:{FONTS.get(e['font'], FONTS['Calibri'])}",
              f"text-align:{ALIGN[e['align']]}", f"justify-content:{VA[e['va']]}",
              f"line-height:{e['lh']}"]
        if e["bold"]:
            st.append("font-weight:700")
        if e["italic"]:
            st.append("font-style:italic")
        return f'<div class="t" style="{";".join(st)}"><div>{esc(e["text"])}</div></div>'
    if k == "bullets":
        rows = []
        for item in e["items"]:
            rows.append(
                f'<div style="display:flex;gap:{px(0.16)};margin-bottom:{px(max(0, e["gap"] - 0.22))}">'
                f'<span style="color:#{e["dot"]};line-height:1.24">&bull;</span>'
                f'<span style="line-height:1.24">{esc(item)}</span></div>')
        st = [f"left:{px(e['x'])}", f"top:{px(e['y'])}", f"width:{px(e['w'])}",
              f"font-size:{e['size']}pt", f"color:#{e['color']}",
              f"font-family:{FONTS['Calibri']}"]
        return f'<div class="b" style="{";".join(st)}">{"".join(rows)}</div>'
    if k == "line":
        x1, y1, x2, y2 = e["x1"], e["y1"], e["x2"], e["y2"]
        if abs(y2 - y1) < 1e-6:
            st = [f"left:{px(min(x1,x2))}", f"top:{px(y1)}", f"width:{px(abs(x2-x1))}",
                  f"height:{e['w']}px", f"background:#{e['color']}"]
        else:
            st = [f"left:{px(x1)}", f"top:{px(min(y1,y2))}", f"width:{e['w']}px",
                  f"height:{px(abs(y2-y1))}", f"background:#{e['color']}"]
        return f'<div class="b" style="{";".join(st)}"></div>'
    if k == "circle":
        st = [f"left:{px(e['x'])}", f"top:{px(e['y'])}", f"width:{px(e['d'])}",
              f"height:{px(e['d'])}", f"background:#{e['fill']}", "border-radius:50%",
              "display:flex;align-items:center;justify-content:center",
              f"color:#{e['color']}", f"font-size:{e['size']}pt",
              f"font-family:{FONTS['Calibri']}"]
        if e["bold"]:
            st.append("font-weight:700")
        return f'<div class="b" style="{";".join(st)}">{esc(e["text"] or "")}</div>'
    return ""

def main(out):
    pages = []
    for elems in S:
        pages.append('<section class="slide">' + "".join(render(e) for e in elems) + "</section>")
    doc = f"""<!doctype html><meta charset="utf-8"><title>DMVPN Lab Testbed</title>
<style>
@page {{ size: {W}in {H}in; margin: 0; }}
* {{ box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
html, body {{ margin:0; padding:0; }}
.slide {{ position:relative; width:{W}in; height:{H}in; overflow:hidden;
          page-break-after:always; break-after:page; background:#fff; }}
.slide:last-child {{ page-break-after:auto; break-after:auto; }}
.b {{ position:absolute; }}
.t {{ position:absolute; display:flex; flex-direction:column; }}
.t > div {{ width:100%; }}
</style>
{"".join(pages)}"""
    with open(out, "w") as fh:
        fh.write(doc)
    print("wrote", out)

if __name__ == "__main__":
    main(sys.argv[1])
