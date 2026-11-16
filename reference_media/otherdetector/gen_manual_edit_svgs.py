"""Generates the illustrations of the manual edit examples on
docs/module_docs/uv/otherdetector_data_handling.md.

Usage (from the repository root, no dependencies):
    py reference_media/otherdetector/gen_manual_edit_svgs.py [output folder]

Without an output folder, the SVGs are written to docs/module_docs/uv/.

Wording in the figures: "MS row" is an MS feature list row, "UV row" is an aligned other detector
row (UV stands for all other detectors here).
"""
import math
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "module_docs", "uv")

FONT = "Roboto, 'Helvetica Neue', Arial, sans-serif"
INK = "#1f2328"
MUTED = "#57606a"
LINE = "#d0d7de"
PANEL = "#f6f8fa"
MS_COLOR = "#424a53"
ROW_COLORS = {"R1": "#0072B2", "M": "#0072B2", "N": "#CC79A7"}
GREEN = "#009E73"
ORANGE = "#E69F00"
GREY = "#8c959f"

LINK_STYLE = {
    "calc": (GREEN, ""),
    "manual": (ORANGE, "6 4"),
    "aligned": (GREY, "2 4"),
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=12, fill=INK, weight="normal", anchor="start", extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}" {extra}>{esc(s)}</text>')


def text_width(s, size):
    return len(s) * size * 0.56


def dash(d):
    return f'stroke-dasharray="{d}"' if d else ""


def pill(cx, cy, s, size, stroke, fill="#ffffff", txt=INK, weight="normal"):
    w = text_width(s, size) + 12
    h = size + 7
    return (f'<rect x="{cx - w / 2:.1f}" y="{cy - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{h / 2:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>'
            + text(cx, cy + size * 0.36, s, size, txt, weight, "middle"))


def area_path(px, py, base, rt, height, sigma):
    rt_a, rt_b = rt - 3.2 * sigma, rt + 3.2 * sigma
    n = 60
    pts = [(px(rt_a), base)]
    for i in range(n + 1):
        r = rt_a + (rt_b - rt_a) * i / n
        pts.append((px(r), py(height * math.exp(-0.5 * ((r - rt) / sigma) ** 2))))
    pts.append((px(rt_b), base))
    return "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts) + " Z"


MS_DASH = {False: "", True: "7 3"}


def chromatogram(x, y, w, h, rt_range, uv_peaks, ms_peaks, label):
    """
    uv_peaks: list of (rt, rel_height, sigma, uv_row or None)
    ms_peaks: list of (rt, sigma, rel_height, ms_row_label, dashed), drawn in the background. The
    key above the plot names them.
    """
    out = [text(x, y - 8, label, 11.5, MUTED)]
    rt0, rt1 = rt_range
    base = y + h

    def px(rt):
        return x + (rt - rt0) / (rt1 - rt0) * w

    def py(v):
        return base - v * (h - 12)

    # MS features in the background, larger than the UV features
    kx = x + w
    for ms_rt, ms_sigma, ms_height, ms_label, dashed in reversed(ms_peaks):
        out.append(f'<path d="{area_path(px, py, base, ms_rt, ms_height, ms_sigma)}" '
                   f'fill="{MS_COLOR}" fill-opacity="0.07" stroke="{MS_COLOR}" '
                   f'stroke-width="1.4" {dash(MS_DASH[dashed])}/>')
    # key: right aligned, same order as given
    for ms_rt, ms_sigma, ms_height, ms_label, dashed in reversed(ms_peaks):
        s = f"{ms_label} feature"
        kx -= text_width(s, 11)
        out.append(text(kx, y - 8, s, 11, MS_COLOR, "bold"))
        kx -= 30
        out.append(f'<rect x="{kx}" y="{y - 18}" width="22" height="12" rx="2" '
                   f'fill="{MS_COLOR}" fill-opacity="0.07" stroke="{MS_COLOR}" '
                   f'stroke-width="1.4" {dash(MS_DASH[dashed])}/>')
        kx -= 18

    # UV features
    for rt, height, sigma, row in uv_peaks:
        d = area_path(px, py, base, rt, height, sigma)
        if row:
            color = ROW_COLORS[row]
            out.append(f'<path d="{d}" fill="{color}" fill-opacity="0.35" stroke="{color}" '
                       f'stroke-width="1.3"/>')
        else:
            out.append(f'<path d="{d}" fill="#ffffff" fill-opacity="0.7" stroke="{GREY}" '
                       f'stroke-width="1.2" stroke-dasharray="3 2"/>')

    # UV trace line
    n = 240
    pts = []
    for i in range(n + 1):
        rt = rt0 + (rt1 - rt0) * i / n
        v = sum(p[1] * math.exp(-0.5 * ((rt - p[0]) / p[2]) ** 2) for p in uv_peaks) + 0.015
        pts.append(f"{px(rt):.1f},{py(v):.1f}")
    out.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{ROW_COLORS["R1"]}" '
               f'stroke-opacity="0.55" stroke-width="1.2"/>')

    # axis
    out.append(f'<line x1="{x}" y1="{base}" x2="{x + w}" y2="{base}" stroke="{MUTED}"/>')
    for rt, height, sigma, row in uv_peaks:
        cx = px(rt)
        out.append(f'<line x1="{cx:.1f}" y1="{base}" x2="{cx:.1f}" y2="{base + 4}" '
                   f'stroke="{MUTED}"/>')
        out.append(text(cx, base + 17, f"{rt:g} min", 11, MUTED, anchor="middle"))
        ty = py(height) - 13
        if row:
            color = ROW_COLORS[row]
            out.append(pill(cx, ty, row, 11, color, color, "#ffffff", "bold"))
        else:
            out.append(pill(cx, ty, "not aligned", 10.5, GREY, "#ffffff", MUTED))
    return "\n".join(out)


def ms_box(x, y, label, w=100, h=30, dashed=False):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="#ffffff" '
            f'stroke="{MS_COLOR}" stroke-width="1.4" {dash(MS_DASH[dashed])}/>'
            + text(x + w / 2, y + h / 2 + 4.3, label, 12, INK, "bold", "middle"))


def row_box(x, y, name, lines, w=150, removed=False, empty=False):
    h = 22 + 16 * len(lines)
    if empty:
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="none" '
                f'stroke="{GREY}" stroke-dasharray="4 3"/>'
                + text(x + w / 2, y + h / 2 + 4, name, 11.5, MUTED, anchor="middle",
                       extra='font-style="italic"'))
    color = GREY if removed else ROW_COLORS[name]
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="#ffffff" '
           f'stroke="{color}" stroke-width="{1.2 if removed else 1.8}" '
           f'{dash("4 3") if removed else ""}/>',
           f'<rect x="{x}" y="{y}" width="6" height="{h}" rx="2" fill="{color}"/>']
    title = f"UV row {name} (removed)" if removed else f"UV row {name}"
    out.append(text(x + 14, y + 16, title, 12, MUTED if removed else color, "bold"))
    for i, line in enumerate(lines):
        out.append(text(x + 14, y + 33 + 16 * i, line, 11.5, MUTED if removed else INK))
    return "\n".join(out)


def link(x1, y1, x2, y2, kind, label, t=0.5, dy=0):
    color, d = LINK_STYLE[kind]
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2" '
           f'{dash(d)}/>']
    out.append(pill(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t + dy, label, 11, color))
    return "\n".join(out)


def panel(x, y, w, h, title):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{PANEL}" '
            f'stroke="{LINE}"/>' + text(x + 14, y + 22, title, 13.5, INK, "bold"))


def arrow(x, y):
    return (f'<path d="M{x - 9},{y - 12} L{x + 7},{y} L{x - 9},{y + 12}" fill="none" '
            f'stroke="{MUTED}" stroke-width="3" stroke-linecap="round" '
            f'stroke-linejoin="round"/>')


def legend(x, y, items):
    out = []
    for kind, label in items:
        if kind in LINK_STYLE:
            color, d = LINK_STYLE[kind]
            out.append(f'<line x1="{x}" y1="{y}" x2="{x + 26}" y2="{y}" stroke="{color}" '
                       f'stroke-width="2" {dash(d)}/>')
            x += 32
        else:
            swatch = {
                "ms_peak": f'fill="{MS_COLOR}" fill-opacity="0.08" stroke="{MS_COLOR}"',
                "aligned_peak": f'fill="{ROW_COLORS["R1"]}" fill-opacity="0.35" '
                                f'stroke="{ROW_COLORS["R1"]}"',
                "processed_peak": f'fill="#ffffff" stroke="{GREY}" stroke-dasharray="3 2"',
            }[kind]
            out.append(f'<rect x="{x}" y="{y - 6}" width="16" height="12" rx="2" {swatch}/>')
            x += 22
        out.append(text(x, y + 4, label, 11.5, MUTED))
        x += text_width(label, 11.5) + 22
    return "\n".join(out)


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
            f'height="{h}" font-family="{FONT}" role="img" aria-label="{esc(title)}">\n'
            f'<title>{esc(title)}</title>\n'
            f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n{body}\n</svg>\n')


def write(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


TOP, GAP, MS_X, ROW_W = 10, 44, 16, 150
PEAK_LEGEND = [("ms_peak", "MS feature"), ("aligned_peak", "UV feature in a UV row"),
               ("processed_peak", "UV feature, not aligned")]


# ---------------------------------------------------------------- example 1: pick a different peak
def example_pick_peak():
    pw, ph = 470, 350
    xs = [10, 10 + pw + GAP]
    W, H = xs[1] + pw + 10, TOP + ph + 40
    body = []
    states = [
        ("Before: R1 holds the UV feature at 13.3 min",
         [(13.3, 0.62, 0.035, "R1"), (13.5, 0.45, 0.035, None)], "file A: 13.3 min",
         [("calc", "Calculated 0.91"), ("calc", "Calculated 0.88")]),
        ("After Define as correlated on 13.5 min",
         [(13.3, 0.62, 0.035, None), (13.5, 0.45, 0.035, "R1")], "file A: 13.5 min",
         [("manual", "Manual"), ("manual", "Manual, now 13.5 min")]),
    ]
    # decision: MS row 2 is an adduct of MS row 1, same RT and shape, lower intensity. The MS
    # features are wide and their apex is between the UV features
    ms_peaks = [(13.43, 0.1, 1.0, "MS row 1", False), (13.43, 0.1, 0.75, "MS row 2", True)]
    for x, (title, peaks, cell, links) in zip(xs, states):
        body.append(panel(x, TOP, pw, ph, title))
        body.append(chromatogram(x + 24, TOP + 62, pw - 48, 134, (13.05, 13.8), peaks,
                                 ms_peaks, "file A"))
        ms1_y, ms2_y = TOP + 250, TOP + 302
        body.append(ms_box(x + MS_X, ms1_y, "MS row 1"))
        body.append(ms_box(x + MS_X, ms2_y, "MS row 2", dashed=True))
        rx, ry = x + pw - ROW_W - 16, TOP + 264
        body.append(row_box(rx, ry, "R1", [cell], ROW_W))
        body.append(link(x + MS_X + 100, ms1_y + 15, rx, ry + 12, *links[0]))
        body.append(link(x + MS_X + 100, ms2_y + 15, rx, ry + 34, *links[1]))
    body.append(arrow(xs[1] - GAP / 2, TOP + ph / 2))
    body.append(legend(20, TOP + ph + 22,
                       PEAK_LEGEND + [("calc", "Calculated"), ("manual", "Manual")]))
    write("manual_edit_pick_peak.svg",
          svg(W, H, "\n".join(body), "Example: pick a different peak of the same trace"))


def overlay_chromatogram(x, y, w, h, rt_range, traces, ms_peak, brackets=()):
    """
    Single plot with the UV traces of several raw data files and one MS feature in the background.
    traces: list of (file_label, dashed, [(rt, rel_height, sigma, uv_row or None)])
    ms_peak: (rt, sigma, rel_height, ms_row_label)
    brackets: list of (rt_from, rt_to, level, label, color). An upside down U from peak top to peak
    top that marks the RT difference, level in px above the higher peak tag. A bracket to the right
    is labeled next to its end, a bracket to the left above its bar.
    """
    out = []
    rt0, rt1 = rt_range
    base = y + h

    def px(rt):
        return x + (rt - rt0) / (rt1 - rt0) * w

    def py(v):
        return base - v * (h - 12)

    # key: right aligned, MS feature first
    kx = x + w
    keys = [(label, dashed) for label, dashed, _ in traces]
    for label, dashed in reversed(keys):
        s = f"{label} UV trace"
        kx -= text_width(s, 11)
        out.append(text(kx, y - 8, s, 11, MUTED))
        kx -= 30
        out.append(f'<line x1="{kx}" y1="{y - 12}" x2="{kx + 22}" y2="{y - 12}" '
                   f'stroke="{ROW_COLORS["R1"]}" stroke-width="1.6" '
                   f'{dash("5 3") if dashed else ""}/>')
        kx -= 18
    ms_rt, ms_sigma, ms_height, ms_label = ms_peak
    s = f"{ms_label} feature"
    kx -= text_width(s, 11)
    out.append(text(kx, y - 8, s, 11, MS_COLOR, "bold"))
    kx -= 30
    out.append(f'<rect x="{kx}" y="{y - 18}" width="22" height="12" rx="2" fill="{MS_COLOR}" '
               f'fill-opacity="0.07" stroke="{MS_COLOR}" stroke-width="1.4"/>')

    # MS feature in the background, larger than the UV features
    out.append(f'<path d="{area_path(px, py, base, ms_rt, ms_height, ms_sigma)}" '
               f'fill="{MS_COLOR}" fill-opacity="0.07" stroke="{MS_COLOR}" stroke-width="1.4"/>')

    # UV features, broad ones first so narrow ones stay visible on top
    all_peaks = [(p, dashed) for _, dashed, peaks in traces for p in peaks]
    for (rt, height, sigma, row), dashed in sorted(all_peaks, key=lambda e: -e[0][2]):
        d = area_path(px, py, base, rt, height, sigma)
        stroke_dash = 'stroke-dasharray="5 3"' if dashed else ""
        if row:
            color = ROW_COLORS[row]
            opacity = 0.18 if dashed else 0.4
            out.append(f'<path d="{d}" fill="{color}" fill-opacity="{opacity}" stroke="{color}" '
                       f'stroke-width="1.4" {stroke_dash}/>')
        else:
            out.append(f'<path d="{d}" fill="#ffffff" fill-opacity="0.7" stroke="{GREY}" '
                       f'stroke-width="1.2" stroke-dasharray="3 2"/>')

    # axis with one tick per UV feature
    out.append(f'<line x1="{x}" y1="{base}" x2="{x + w}" y2="{base}" stroke="{MUTED}"/>')
    out.append(text(x + w, base + 17, "RT (min)", 11, MUTED, anchor="end"))
    for (rt, height, sigma, row), dashed in all_peaks:
        cx = px(rt)
        out.append(f'<line x1="{cx:.1f}" y1="{base}" x2="{cx:.1f}" y2="{base + 4}" '
                   f'stroke="{MUTED}"/>')
        out.append(text(cx, base + 17, f"{rt:.2f}", 11, MUTED, anchor="middle"))

    # RT difference brackets from tag top to tag top
    tops = {rt: py(height) - 22 for (rt, height, sigma, row), _ in all_peaks}
    for rt_from, rt_to, level, label, color in brackets:
        bar = min(tops[rt_from], tops[rt_to]) - level
        x1, x2 = px(rt_from), px(rt_to)
        out.append(f'<path d="M{x1:.1f},{tops[rt_from] - 3:.1f} L{x1:.1f},{bar:.1f} '
                   f'L{x2:.1f},{bar:.1f} L{x2:.1f},{tops[rt_to] - 3:.1f}" fill="none" '
                   f'stroke="{color}" stroke-width="1.6"/>')
        # decision: brackets to the right are labeled next to their end, brackets to the left
        # above their bar, so the labels do not cross the shared leg
        halo = 'paint-order="stroke" stroke="#ffffff" stroke-width="3"'
        if x2 > x1:
            out.append(text(x2 + 6, bar + 4, label, 11, color, "bold", "start", halo))
        else:
            out.append(text((x1 + x2) / 2, bar - 5, label, 11, color, "bold", "middle", halo))

    # tags of the UV rows
    for (rt, height, sigma, row), dashed in all_peaks:
        cx, ty = px(rt), py(height) - 13
        if row:
            color = ROW_COLORS[row]
            out.append(pill(cx, ty, row, 11, color, color, "#ffffff", "bold"))
        else:
            out.append(pill(cx, ty, "not aligned", 10.5, GREY, "#ffffff", MUTED))
    return "\n".join(out)


# ---------------------------------------------------------------- example 2: fix a misalignment
def example_misalignment():
    pw, ph = 500, 420
    xs = [10, 10 + pw + GAP]
    W, H = xs[1] + pw + 10, TOP + ph + 40
    body = []
    rx_off = pw - ROW_W - 16
    m_y, n_y = TOP + 300, TOP + 368
    ms1_y = TOP + 340
    rt_range = (1.16, 1.44)

    # decision: file A has one broad UV feature that encloses both narrow UV features of file B. It
    # seeds UV row M, and the lower file B feature at 1.33 min joins because it is closer to the
    # seed (1.3 min) than the higher one at 1.26 min, which matches the MS feature
    # decision: the MS feature is as wide as the UV feature of file A, its apex is shifted slightly
    # towards the higher file B feature
    ms_peak = (1.285, 0.04, 0.95, "MS row 1")
    for i, x in enumerate(xs):
        before = i == 0
        body.append(panel(x, TOP, pw, ph,
                          "Before: file B aligned to the wrong UV feature" if before
                          else "After Define as correlated on 1.26 min in file B"))
        traces = [("file A", True, [(1.30, 0.5, 0.04, "M")]),
                  ("file B", False, [(1.26, 0.62, 0.007, "N" if before else "M"),
                                     (1.33, 0.3, 0.007, "M" if before else None)])]
        brackets = [(1.30, 1.33, 6, "Δ 0.03 min, closest", ROW_COLORS["M"]),
                    (1.30, 1.26, 16, "Δ 0.04 min", MUTED)] if before else []
        body.append(overlay_chromatogram(x + 24, TOP + 62, pw - 48, 190, rt_range, traces,
                                         ms_peak, brackets))
        body.append(ms_box(x + MS_X, ms1_y, "MS row 1"))
        if before:
            body.append(row_box(x + rx_off, m_y, "M", ["file A: 1.30 min", "file B: 1.33 min"],
                                ROW_W))
            body.append(row_box(x + rx_off, n_y, "N", ["file B: 1.26 min"], ROW_W))
            body.append(link(x + MS_X + 100, ms1_y + 8, x + rx_off, m_y + 27, "calc",
                             "Calculated A 0.96, B Aligned", t=0.5, dy=-6))
            body.append(link(x + MS_X + 100, ms1_y + 22, x + rx_off, n_y + 19, "calc",
                             "Calculated B 0.93", t=0.5, dy=6))
        else:
            body.append(row_box(x + rx_off, m_y, "M", ["file A: 1.30 min", "file B: 1.26 min"],
                                ROW_W))
            body.append(row_box(x + rx_off, n_y, "N", ["1.26 min moved to M"], ROW_W,
                                removed=True))
            body.append(link(x + MS_X + 100, ms1_y + 15, x + rx_off, m_y + 27, "calc",
                             "Calculated A 0.96, B 0.93", t=0.5))

    body.append(arrow(xs[1] - GAP / 2, TOP + ph / 2))
    body.append(legend(20, TOP + ph + 22, PEAK_LEGEND + [("calc", "Calculated")]))
    write("manual_edit_fix_misalignment.svg",
          svg(W, H, "\n".join(body), "Example: fix a misalignment"))


# ---------------------------------------------------------------- example 3: fully manual workflow
def example_fully_manual():
    pw, ph, gap = 350, 350, 40
    xs = [10, 10 + pw + gap, 10 + 2 * (pw + gap)]
    W, H = xs[2] + pw + 10, TOP + ph + 40
    row_w = 130
    rx_off = pw - row_w - 16
    ms_y, row_y = TOP + 272, TOP + 258
    body = []
    states = [
        ("Before: no alignment", "file A", 5.2, 5.13, None, None, None),
        ("Define as correlated in file A", "file A", 5.2, 5.13, "R1", ["file A: 5.2 min"],
         "Manual (A)"),
        ("Define as correlated in file B", "file B", 5.25, 5.17, "R1",
         ["file A: 5.2 min", "file B: 5.25 min"], "Manual (A, B)"),
    ]
    for x, (title, label, rt, ms_rt, row, cells, link_label) in zip(xs, states):
        body.append(panel(x, TOP, pw, ph, title))
        body.append(chromatogram(x + 24, TOP + 62, pw - 48, 134, (4.8, 5.5),
                                 [(rt, 0.55, 0.035, row)],
                                 [(ms_rt, 0.09, 1.0, "MS row 1", False)], label))
        body.append(ms_box(x + MS_X, ms_y, "MS row 1", w=84))
        if cells is None:
            body.append(row_box(x + rx_off, row_y, "no UV rows", ["", ""], row_w, empty=True))
        else:
            body.append(row_box(x + rx_off, row_y, "R1", cells, row_w))
            body.append(link(x + MS_X + 84, ms_y + 15, x + rx_off, ms_y + 15, "manual",
                             link_label))
    body.append(arrow(xs[1] - gap / 2, TOP + ph / 2))
    body.append(arrow(xs[2] - gap / 2, TOP + ph / 2))
    body.append(legend(20, TOP + ph + 22,
                       [("ms_peak", "MS feature"), ("aligned_peak", "UV feature in a UV row"),
                        ("processed_peak", "UV feature (processed or manually integrated)"),
                        ("manual", "Manual")]))
    write("manual_edit_fully_manual.svg",
          svg(W, H, "\n".join(body), "Example: fully manual workflow"))


example_pick_peak()
example_misalignment()
example_fully_manual()
print("written to", OUT)
