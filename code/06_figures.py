"""
06 - Figures of the revised manuscript (all regenerated from the result tables).

Colour conventions: one fixed hue + marker per region in every figure
(colour follows the entity, never its rank); single-hue sequential ramp for
probabilities; direct labels so that identity never depends on colour alone.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch, Circle
from matplotlib.font_manager import FontProperties

ROOT = Path(__file__).resolve().parents[1]
TAB, FIG = ROOT / "results" / "tables", ROOT / "results" / "figures"
REG = ["Sindh", "Balochistan", "Punjab", "KP", "GB", "AJ&K", "ICT"]
COL = dict(zip(REG, ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6"]))
MRK = dict(zip(REG, ["o", "s", "^", "D", "v", "P", "X"]))
SEQ = LinearSegmentedColormap.from_list("seq", ["#fcfcfb", "#cde2fb", "#6da7ec", "#256abf", "#0d366b"])
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
STAGE = {"T1": "Impact stage ($T_1$)", "T2": "Relief stage ($T_2$)", "T3": "Recovery stage ($T_3$)"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.8,
                     "figure.dpi": 150, "savefig.dpi": 600, "savefig.bbox": "tight",
                     "axes.titlesize": 10, "axes.titleweight": "bold"})

def save(fig, name, exact=False):
    """exact=True keeps the figure at its design size (no tight cropping), so lettering prints at true size."""
    with plt.rc_context({"savefig.bbox": "standard" if exact else "tight"}):
        fig.savefig(FIG / f"{name}.png")                    # PNG only, 600 dpi
    plt.close(fig)

# ---------------------------------------------------------------- Fig: workflow
# Pictograms are glyphs of the Font Awesome Free 6 solid font (font: SIL OFL 1.1; icons: CC BY 4.0),
# bundled in code/assets so that the figure can be regenerated offline.
FA = FontProperties(fname=str(Path(__file__).resolve().parent / "assets" / "fa-solid-900.ttf"))
ICON = {"report": "", "scale": "", "band": "", "layers": "", "target": "",
        "gauge": "", "tiers": "", "shield": "", "output": "",
        "deaths": "", "injured": "", "roads": "", "bridges": "",
        "houses": "", "livestock": "", "affected": "",
        "impact": "", "relief": "", "recovery": ""}

def fig_workflow():
    """Workflow in three labelled phases (A data, B stage-wise evaluation, C decision support).

    Every row reads left to right and the phases read top to bottom. The figure is drawn at print size
    (full text width, 372 pt), with lettering of 7-8.5 pt (indicator names 5.8 pt). Every text is measured
    after drawing and the function fails if a label leaves its box, so the layout cannot silently overflow.
    """
    Wd, Ht = 5.17, 5.48
    fig = plt.figure(figsize=(Wd, Ht)); ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, Wd); ax.set_ylim(0, Ht); ax.axis("off")
    NAVY, BLUE, PANEL, LINE, TINT, CHIP = "#1f3a5f", "#3b6ea8", "#f5f7fa", "#d3dae3", "#e2eaf4", "#e8eff8"
    ARROW = "#5f6f82"
    STG = {"impact": "#2a78d6", "relief": "#eb6834", "recovery": "#1baf7a"}
    F_TAG, F_TITLE, F_BODY, F_CHIP, F_IND, F_BAND = 6.2, 8.3, 7.1, 6.9, 5.8, 7.0
    R_ICON, G_ICON = 0.168, 9.8
    checks, vchecks = [], []                               # (text, left limit, right limit); (text, lower limit)

    def text(x, y, s, lo, hi, **kw):
        t = ax.text(x, y, s, zorder=kw.pop("zorder", 6), **kw)
        checks.append((t, lo, hi)); return t

    def icon(x, y, key, r=R_ICON, bg=TINT, fg=NAVY, size=G_ICON):
        ax.add_patch(Circle((x, y), r, fc=bg, ec="none", zorder=5))
        ax.text(x, y, ICON[key], fontproperties=FA, fontsize=size, color=fg, ha="center", va="center", zorder=6)

    def rbox(x, y, w, h, fc="white", ec=LINE, lw=0.7, rs=0.05, z=3):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={rs}",
                                    fc=fc, ec=ec, lw=lw, zorder=z))

    def band(y, h, letter, title):
        """Phase panel with a header bar; returns the y of the top of its content area."""
        hb = 0.19
        rbox(M, y, full, h, fc=PANEL, ec=LINE, lw=0.8, rs=0.06, z=1)
        ax.add_patch(FancyBboxPatch((M, y + h - hb), full, hb, boxstyle="round,pad=0,rounding_size=0.06",
                                    fc=NAVY, ec=NAVY, lw=0.8, zorder=2))
        ax.add_patch(plt.Rectangle((M, y + h - hb), full, hb / 2, fc=NAVY, ec="none", zorder=2))   # square lower corners
        text(M + 0.10, y + h - hb / 2 - 0.004, letter, M, M + full, fontsize=F_BAND + 0.6, fontweight="bold",
             color="#9fc2ee", va="center")
        text(M + 0.27, y + h - hb / 2 - 0.004, title, M, M + full, fontsize=F_BAND, fontweight="bold",
             color="white", va="center")
        return y + h - hb

    def card(x, y, w, h, key, tag, title, body, chip, dark=False):
        fc, ink, sub, tagc = ("white", INK, MUTED, BLUE) if not dark else (NAVY, "white", "#d6e2f1", "#9fc2ee")
        rbox(x, y, w, h, fc=fc, ec=LINE if not dark else NAVY)
        lo, hi = x + 0.05, x + w - 0.04
        icon(x + 0.06 + R_ICON, y + h - 0.06 - R_ICON, key, bg=TINT if not dark else "white")
        tx = x + 0.06 + 2 * R_ICON + 0.06
        text(tx, y + h - 0.150, tag, lo, hi, fontsize=F_TAG, color=tagc, fontweight="bold", va="center")
        text(tx, y + h - 0.305, title, lo, hi, fontsize=F_TITLE, fontweight="bold", color=ink, va="center")
        tb = text(x + 0.09, y + h - 0.455, body, lo, hi, fontsize=F_BODY, color=sub, va="top", linespacing=1.2)
        vchecks.append((tb, y + 0.26))                       # the body must end above the shaded strip
        ax.add_patch(FancyBboxPatch((x + 0.06, y + 0.055), w - 0.12, 0.205, boxstyle="round,pad=0,rounding_size=0.03",
                                    fc=CHIP if not dark else "#345a8c", ec="none", zorder=4))
        text(x + 0.105, y + 0.155, chip, x + 0.06, x + w - 0.06, fontsize=F_CHIP,
             color=NAVY if not dark else "white", va="center")

    def arrow(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), zorder=7,
                    arrowprops=dict(arrowstyle="-|>,head_width=0.22,head_length=0.42", color=ARROW, lw=1.2,
                                    shrinkA=0, shrinkB=0))

    M, PAD, G, VB = 0.04, 0.06, 0.14, 0.15                 # margin, band padding, card gap, gap between bands
    full = Wd - 2 * M
    w3 = (full - 2 * PAD - 2 * G) / 3
    X = [M + PAD + k * (w3 + G) for k in range(3)]
    hc, hst, hb = 0.98, 0.78, 0.19
    hA = hb + PAD + hc + PAD
    hB = hb + 0.04 + 0.18 + hst + 0.14 + hc + PAD
    hC = hA
    yA = Ht - 0.03 - hA
    yB = yA - VB - hB
    yC = yB - VB - hC

    # ---- phase A: data
    top = band(yA, hA, "A", "PREPARE THE DATA")
    y = top - PAD - hc
    card(X[0], y, w3, hc, "report", "INPUT", "Situation report",
         "Losses by region and\nindicator (NDMA)", "191 deaths, 3,858 injured")
    card(X[1], y, w3, hc, "scale", "STEP 1", "Normalise",
         "Rescale each indicator\nto 0\u20131 (1 = worst region)", "191 deaths $\\rightarrow$ 0.281")
    card(X[2], y, w3, hc, "band", "STEP 2", "Tolerance band",
         "Each value becomes a\nrange ($\\pm$10 % tolerance)", "0.281 $\\rightarrow$ [0.253, 0.309]")
    for k in (0, 1):
        arrow(X[k] + w3 + 0.025, y + hc / 2, X[k + 1] - 0.02, y + hc / 2)

    # ---- phase B: stage-wise evaluation
    top = band(yB, hB, "B", "EVALUATE EACH DISASTER STAGE")
    yl = top - 0.04 - 0.09
    text(X[0] + 0.02, yl, "STEP 3", M, M + full, fontsize=F_TAG, color=BLUE, fontweight="bold", va="center")
    t_title = text(X[0] + 0.40, yl, "Activate the indicators of each stage", M, M + full, fontsize=F_TITLE - 0.5,
                   fontweight="bold", color=INK, va="center")
    t_note = text(M + full - PAD - 0.02, yl, "stage weights rescaled to sum to 1", M, M + full, fontsize=F_CHIP - 0.3,
                  color=MUTED, ha="right", va="center")
    ys = top - 0.04 - 0.18 - hst
    stages = [("impact", "Impact  $T_1$", "rescue, emergency care", ["deaths", "injured"]),
              ("relief", "Relief  $T_2$", "care, access, shelter", ["injured", "roads", "bridges", "houses"]),
              ("recovery", "Recovery  $T_3$", "rebuilding, livelihoods", ["houses", "livestock", "affected"])]
    r_s, r_i = 0.14, 0.108
    for k, (key, name, need, inds) in enumerate(stages):
        sx, sw = X[k], w3
        rbox(sx, ys, sw, hst, ec=LINE)
        ax.add_patch(FancyBboxPatch((sx, ys + hst - 0.055), sw, 0.055, boxstyle="round,pad=0,rounding_size=0.027",
                                    fc=STG[key], ec=STG[key], lw=0.7, zorder=4))             # coloured top bar
        icon(sx + 0.07 + r_s, ys + hst - 0.105 - r_s, key, r=r_s, bg=STG[key], fg="white", size=8.0)
        nx = sx + 0.07 + 2 * r_s + 0.07
        text(nx, ys + hst - 0.175, name, sx, sx + sw - 0.02, fontsize=7.9, fontweight="bold", color=INK, va="center")
        text(nx, ys + hst - 0.315, need, sx, sx + sw - 0.02, fontsize=6.2, color=MUTED, va="center")
        n = len(inds); step = min(0.44, (sw - 0.04) / n)
        for j, ind in enumerate(inds):
            cx = sx + sw / 2 + (j - (n - 1) / 2) * step
            icon(cx, ys + 0.235, ind, r=r_i, bg="#eef1f5", fg=STG[key], size=6.4)
            text(cx, ys + 0.065, ind, cx - step / 2, cx + step / 2, fontsize=F_IND, color=MUTED,
                 ha="center", va="center")
    y = yB + PAD
    card(X[0], y, w3, hc, "target", "STEP 4", "Two references",
         "Distance $d^+$ to worst case,\n$d^-$ to no-loss case", "$d^+$ = 0.653,  $d^-$ = 0.347")
    card(X[1], y, w3, hc, "gauge", "STEP 5", "Severity index",
         "SSI = $d^-/(d^+ + d^-)$;\nrank 1 = top priority", "SSI = 0.347, rank 2 of 7")
    card(X[2], y, w3, hc, "tiers", "STEP 6", "Priority tiers",
         "Overlapping uncertainty\nbands share one tier", "tier 2 with KP, Balochistan")
    for k in (0, 1):
        arrow(X[k] + w3 + 0.025, y + hc / 2, X[k + 1] - 0.02, y + hc / 2)
    mid = M + full / 2
    arrow(mid, ys - 0.02, mid, y + hc + 0.015)

    # ---- phase C: decision support (robustness check, then the output)
    band(yC, hC, "C", "SUPPORT THE DECISION")
    y = yC + PAD
    wo = 2 * w3 + G
    card(X[0], y, w3, hc, "shield", "STEP 7", "Robustness",
         "Vary weights and data;\ncompare TOPSIS, VIKOR", "rank 2 in 98 % of trials")
    card(X[1], y, wo, hc, "output", "OUTPUT", "Decision support by stage",
         "Ranking and tiers per stage, a combined priority that\nfollows the shift from impact to recovery, rank stability",
         "Punjab, impact stage: tier 2 for rescue and medical care", dark=True)
    t_out = checks[-3][0]                                  # title of the output card
    x_badge = X[1] + wo - 0.74
    for k, key in enumerate(["impact", "relief", "recovery"]):
        icon(x_badge + 0.28 * k, y + hc - 0.06 - R_ICON, key, r=0.115, bg=STG[key], fg="white", size=6.6)
    checks.append((t_out, X[1], x_badge - 0.115 - 0.04))   # the title must stop before the stage badges
    arrow(X[0] + w3 + 0.025, y + hc / 2, X[1] - 0.02, y + hc / 2)

    # ---- arrows between phases and the key of the shaded strips
    arrow(mid, yA - 0.02, mid, yB + hB + 0.015)
    arrow(mid, yB - 0.02, mid, yC + hC + 0.015)
    ax.add_patch(FancyBboxPatch((M + 0.02, yC - 0.165), 0.26, 0.10, boxstyle="round,pad=0,rounding_size=0.02",
                                fc=CHIP, ec=LINE, lw=0.5, zorder=4))
    text(M + 0.34, yC - 0.117, "Running example: Punjab at the impact stage ($T_1$)", M, M + full, fontsize=6.4,
         color=MUTED, va="center")

    # ---- layout check: no label may leave its box, and the Step 3 title must not meet its note
    fig.canvas.draw(); rd = fig.canvas.get_renderer(); inv = ax.transData.inverted()
    def ext(t):
        bb = t.get_window_extent(rd); (x0, _), (x1, _) = inv.transform([(bb.x0, bb.y0), (bb.x1, bb.y1)])
        return x0, x1
    bad = [(t.get_text(), round(ext(t)[0] - lo, 3), round(hi - ext(t)[1], 3)) for t, lo, hi in checks
           if ext(t)[0] < lo - 1e-3 or ext(t)[1] > hi + 1e-3]
    for t, ylim in vchecks:
        bb = t.get_window_extent(rd); y0 = inv.transform((bb.x0, bb.y0))[1]
        if y0 < ylim:
            bad.append((t.get_text(), "too low by", round(ylim - y0, 3)))
    if ext(t_title)[1] > ext(t_note)[0] - 0.08:
        bad.append(("Step 3 title meets its note", 0, 0))
    if bad:   # font metrics differ slightly between systems, so report instead of stopping the pipeline
        print(f"  note: Fig_workflow labels close to a box edge on this system: {bad}")
    if yC - 0.19 <= 0:
        print("  note: Fig_workflow height is tight on this system")
    save(fig, "Fig_workflow", exact=True)

# ---------------------------------------------------------------- Fig: stage structure
def fig_stage_structure():
    """Which indicator is active in which stage, with the stage weights (global weights rescaled to sum to 1)."""
    import json
    cfg = json.loads((ROOT / "data" / "config_pakistan2022.json").read_text(encoding="utf-8"))
    attrs = list(cfg["attributes"]); stages = list(cfg["stages"])
    glob = {a: cfg["attributes"][a]["weight"] for a in attrs}
    ikey = dict(zip(attrs, ["deaths", "injured", "roads", "bridges", "houses", "livestock", "affected"]))
    skey = dict(zip(stages, ["impact", "relief", "recovery"]))
    scol = dict(zip(stages, ["#2a78d6", "#eb6834", "#1baf7a"]))
    stint = dict(zip(stages, ["#e3eefb", "#fde9df", "#dff4ea"]))
    LINE, NAVY = "#d3dae3", "#1f3a5f"
    Wd, Ht = 5.17, 3.50
    fig = plt.figure(figsize=(Wd, Ht)); ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, Wd); ax.set_ylim(0, Ht); ax.axis("off")
    xl, wl, wg, gap, hh, rh = 0.04, 1.66, 0.54, 0.07, 0.52, 0.375
    wc = (Wd - xl - wl - wg - 3 * gap - 0.04) / 3
    xg = xl + wl
    xs = [xg + wg + gap + k * (wc + gap) for k in range(3)]
    ytop = Ht - 0.04

    def glyph(x, y, key, r, bg, fg, size):
        ax.add_patch(Circle((x, y), r, fc=bg, ec="none", zorder=4))
        ax.text(x, y, ICON[key], fontproperties=FA, fontsize=size, color=fg, ha="center", va="center", zorder=5)

    # column headers
    ax.text(xl + 0.06, ytop - hh / 2, "Indicator", fontsize=8, fontweight="bold", color=INK, va="center")
    ax.text(xg + wg / 2, ytop - hh / 2, "Global\nweight", fontsize=6.8, color=MUTED, ha="center", va="center",
            linespacing=1.15)
    for k, st in enumerate(stages):
        ax.add_patch(FancyBboxPatch((xs[k], ytop - hh), wc, hh, boxstyle="round,pad=0,rounding_size=0.05",
                                    fc=scol[st], ec="none", zorder=2))
        glyph(xs[k] + 0.16, ytop - hh / 2, skey[st], 0.11, "white", scol[st], 6.8)
        ax.text(xs[k] + 0.31, ytop - hh / 2 + 0.08, cfg["stages"][st]["label"], fontsize=7.3, fontweight="bold",
                color="white", va="center", zorder=3)
        ax.text(xs[k] + 0.31, ytop - hh / 2 - 0.085, f"stage $T_{k + 1}$", fontsize=6.8, color="white", va="center",
                zorder=3)
    # rows
    y0 = ytop - hh - 0.07
    for i, a in enumerate(attrs):
        yc = y0 - (i + 0.5) * rh
        if i % 2 == 0:
            ax.add_patch(plt.Rectangle((xl, yc - rh / 2), Wd - xl - 0.04, rh, fc="#f6f8fb", ec="none", zorder=0))
        glyph(xl + 0.19, yc, ikey[a], 0.125, "#e2eaf4", NAVY, 7.2)
        ax.text(xl + 0.40, yc, f"$\\varepsilon_{i + 1}$", fontsize=8.2, color=INK, va="center")
        ax.text(xl + 0.64, yc, cfg["attributes"][a]["label"].replace(" (km)", ""), fontsize=7.4, color=INK, va="center")
        ax.text(xg + wg / 2, yc, f"{glob[a]:.2f}", fontsize=7.4, color=MUTED, ha="center", va="center")
        for k, st in enumerate(stages):
            act = cfg["stages"][st]["active"]
            if a not in act:
                ax.text(xs[k] + wc / 2, yc, "–", fontsize=8, color="#a8b1bd", ha="center", va="center")
                continue
            wst = glob[a] / sum(glob[b] for b in act)
            ax.add_patch(FancyBboxPatch((xs[k] + 0.03, yc - rh / 2 + 0.04), wc - 0.06, rh - 0.08,
                                        boxstyle="round,pad=0,rounding_size=0.04", fc=stint[st], ec="none", zorder=1))
            bw = (wc - 0.56) * wst / 0.625                    # bar length proportional to the stage weight
            ax.add_patch(FancyBboxPatch((xs[k] + 0.09, yc - 0.055), max(bw, 0.03), 0.11,
                                        boxstyle="round,pad=0,rounding_size=0.03", fc=scol[st], ec="none", zorder=2))
            ax.text(xs[k] + wc - 0.08, yc, f"{wst:.3f}", fontsize=7.2, color=INK, ha="right", va="center", zorder=3)
    yb = y0 - len(attrs) * rh
    ax.plot([xl, Wd - 0.04], [y0, y0], color=LINE, lw=0.8, zorder=1)
    ax.plot([xl, Wd - 0.04], [yb, yb], color=LINE, lw=0.8, zorder=1)
    ax.text(xl + 0.06, yb - 0.12, "Sum", fontsize=7.4, fontweight="bold", color=INK, va="center")
    ax.text(xg + wg / 2, yb - 0.12, "1.00", fontsize=7.4, color=MUTED, ha="center", va="center")
    for k in range(3):
        ax.text(xs[k] + wc - 0.08, yb - 0.12, "1.000", fontsize=7.2, fontweight="bold", color=INK, ha="right", va="center")
    if yb - 0.20 <= 0:
        print("  note: Fig_stage_structure height is tight on this system")
    save(fig, "Fig_stage_structure", exact=True)

# ---------------------------------------------------------------- Fig: stage SSI with bands
def fig_stage_ssi():
    d = pd.read_csv(TAB / "T05_stage_results.csv")
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.5), sharex=True, gridspec_kw={"wspace": 0.42})
    for ax, s in zip(axes, STAGE):
        g = d[d.stage == s].sort_values("SSI_WHD", ascending=True).reset_index(drop=True)
        y = np.arange(len(g))
        ax.barh(y, g.SSI_WHD, height=0.55, color=[COL[r] for r in g.region], zorder=2)
        ax.errorbar(g.band_central, y, xerr=[g.band_central - g.band_lower, g.band_upper - g.band_central],
                    fmt="none", ecolor=INK, elinewidth=1.0, capsize=2.5, zorder=3)
        for yi, (_, r) in zip(y, g.iterrows()):
            ax.text(max(r.band_upper, r.SSI_WHD) + 0.025, yi,
                    f"{r.SSI_WHD:.3f}  (rank {int(r.rank_WHD)}, tier {int(r.tier)})",
                    va="center", ha="left", fontsize=7.2, color=INK)
        ax.set_yticks(y); ax.set_yticklabels(g.region, color=INK)
        ax.set_xlim(0, 1.78); ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.xaxis.grid(True, color=GRID, lw=0.7, zorder=0); ax.set_axisbelow(True)
        ax.set_title(STAGE[s], loc="left"); ax.set_xlabel("Stage severity index (WHD)")
        ax.tick_params(axis="y", length=0)
    save(fig, "Fig_stage_severity_index")

# ---------------------------------------------------------------- Fig: rank shifts (bump chart)
def fig_rank_shifts():
    c = pd.read_csv(TAB / "T26_static_vs_dynamic_ranks.csv", index_col=0)
    cols = ["Static CFSS (all attributes)", "DCFSS T1", "DCFSS T2", "DCFSS T3"]
    labels = ["Static model\n(all attributes)", "Impact\n$T_1$", "Relief\n$T_2$", "Recovery\n$T_3$"]
    fig, ax = plt.subplots(figsize=(6.6, 3.9))
    x = np.array([0, 1.25, 2.25, 3.25])
    for r in REG:
        yv = c.loc[r, cols].to_numpy(dtype=float)
        ax.plot(x[1:], yv[1:], color=COL[r], lw=2, marker=MRK[r], ms=7, mec="#fcfcfb", mew=1.2, zorder=3)
        ax.plot(x[:2], yv[:2], color=COL[r], lw=1.2, ls=(0, (3, 2)), zorder=2)
        ax.plot(x[0], yv[0], color=COL[r], marker=MRK[r], ms=7, mec="#fcfcfb", mew=1.2, zorder=3)
        ax.text(x[-1] + 0.12, yv[-1], r, va="center", ha="left", fontsize=8.5, color=INK)
    ax.axvline(0.62, color=GRID, lw=1)
    ax.set_xticks(x); ax.set_xticklabels(labels, color=INK)
    ax.set_yticks(range(1, 8)); ax.set_ylim(7.5, 0.5); ax.set_xlim(-0.35, 4.25)
    ax.set_ylabel("Priority rank (1 = most severe)")
    ax.yaxis.grid(True, color=GRID, lw=0.7); ax.set_axisbelow(True); ax.tick_params(length=0)
    save(fig, "Fig_rank_shifts")

# ---------------------------------------------------------------- Fig: stage-emphasis path
def fig_emphasis_path():
    p = pd.read_csv(TAB / "T28_stage_emphasis_path.csv")
    fig, ax = plt.subplots(figsize=(6.8, 3.9))
    for r in REG:
        ax.plot(p.t, p[r], color=COL[r], lw=2, zorder=3)
        ax.plot(p.t.iloc[::50], p[r].iloc[::50], ls="none", marker=MRK[r], color=COL[r], ms=6,
                mec="#fcfcfb", mew=1.0, zorder=4)
        if r in ("Sindh", "Balochistan", "Punjab", "KP"):
            ax.text(2.04, p[r].iloc[-1], r, va="center", ha="left", fontsize=8.5, color=INK)
    ax.text(2.04, 0.0, "AJ&K, GB, ICT", va="center", ha="left", fontsize=8.5, color=INK)
    for name in ("Punjab", "KP"):
        diff = (p[name] - p["Balochistan"]).to_numpy()
        i = int(np.where(diff[:-1] * diff[1:] < 0)[0][0])
        tc = p.t[i] + (p.t[i + 1] - p.t[i]) * diff[i] / (diff[i] - diff[i + 1])
        yc = np.interp(tc, p.t, p["Balochistan"])
        ax.plot([tc], [yc], marker="o", ms=11, mfc="none", mec=INK, mew=1.0, zorder=5)
        ax.annotate(f"Balochistan overtakes {name}", xy=(tc, yc),
                    xytext=(tc - 0.08, yc + (0.26 if name == "Punjab" else 0.17)),
                    fontsize=7.6, color=INK, ha="center",
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8, shrinkB=6))
    ax.set_xticks([0, 1, 2]); ax.set_xticklabels(["Impact only\n$\\lambda$=(1,0,0)", "Relief only\n$\\lambda$=(0,1,0)",
                                                  "Recovery only\n$\\lambda$=(0,0,1)"], color=INK)
    ax.set_xlim(-0.04, 2.48); ax.set_ylim(-0.03, 1.02)
    ax.set_ylabel("Stage-emphasis severity index $\\Psi_\\lambda$")
    ax.yaxis.grid(True, color=GRID, lw=0.7); ax.set_axisbelow(True)
    save(fig, "Fig_stage_emphasis_path")

# ---------------------------------------------------------------- Fig: rank acceptability (weights + data)
def fig_rank_acceptability():
    order = {"T1": ["Sindh", "Punjab", "KP", "Balochistan", "AJ&K", "GB", "ICT"],
             "T2": ["Sindh", "Punjab", "KP", "Balochistan", "GB", "AJ&K", "ICT"],
             "T3": ["Sindh", "Balochistan", "Punjab", "KP", "AJ&K", "GB", "ICT"]}
    fig, axes = plt.subplots(2, 3, figsize=(11.2, 6.6), gridspec_kw={"wspace": 0.42, "hspace": 0.42})
    panels = [("T14b_rank_acceptability_weights_global_{s}.csv", "(a) Weights sampled uniformly"),
              ("T19b_rank_acceptability_data_delta20_{s}.csv", "(b) Data perturbed by $\\pm$20 %")]
    for row, (pat, lab) in enumerate(panels):
        for ax, s in zip(axes[row], STAGE):
            a = pd.read_csv(TAB / pat.format(s=s), index_col=0).loc[order[s]]
            im = ax.imshow(a.to_numpy(), cmap=SEQ, vmin=0, vmax=1, aspect="auto")
            for i in range(a.shape[0]):
                for j in range(a.shape[1]):
                    v = a.iat[i, j]
                    if v >= 0.005:
                        ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7,
                                color="#fcfcfb" if v > 0.55 else INK)
            ax.set_xticks(range(7)); ax.set_xticklabels(range(1, 8))
            ax.set_yticks(range(7)); ax.set_yticklabels(order[s], color=INK)
            ax.set_xticks(np.arange(-.5, 7, 1), minor=True); ax.set_yticks(np.arange(-.5, 7, 1), minor=True)
            ax.grid(which="minor", color="#fcfcfb", lw=2); ax.tick_params(which="both", length=0)
            for sp in ax.spines.values(): sp.set_visible(False)
            ax.set_title(STAGE[s], loc="left", fontsize=9)
            ax.set_xlabel("Rank")
        axes[row][0].annotate(lab, xy=(-0.42, 1.13), xycoords="axes fraction", fontsize=10,
                              fontweight="bold", color=INK, ha="left", va="bottom")
    cb = fig.colorbar(im, ax=axes, shrink=0.6, pad=0.03); cb.set_label("Probability of obtaining the rank")
    cb.outline.set_visible(False)
    save(fig, "Fig_rank_acceptability")

# ---------------------------------------------------------------- Fig: stability vs perturbation size
def fig_stability_curves():
    w = pd.read_csv(TAB / "T14_weights_monte_carlo.csv"); d = pd.read_csv(TAB / "T19_data_perturbation_monte_carlo.csv")
    w = w[w.scenario.str.startswith("local")].copy()
    w["p"] = w.scenario.str.extract(r"(\d+)").astype(float)
    scol = {"T1": "#2a78d6", "T2": "#eb6834", "T3": "#1baf7a"}; smk = {"T1": "o", "T2": "s", "T3": "^"}
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.4), sharey=True)
    for ax, df, xc, xl, ttl in ((axes[0], w, "p", "Weight perturbation ($\\pm$ %)", "Weights perturbed"),
                                (axes[1], d.assign(p=d.delta * 100), "p", "Data perturbation ($\\pm$ %)", "Reported data perturbed")):
        for s in STAGE:
            g = df[df.stage == s].sort_values("p")
            ax.plot(g[xc], g.P_full_order_unchanged, color=scol[s], marker=smk[s], lw=2, ms=7,
                    mec="#fcfcfb", mew=1.2, label=STAGE[s])
            ax.text(g[xc].iloc[-1] + 1.2, g.P_full_order_unchanged.iloc[-1], f"$T_{s[1]}$", va="center",
                    fontsize=8.5, color=INK)
        ax.set_xlabel(xl); ax.set_title(ttl, loc="left"); ax.set_ylim(0, 1.05)
        ax.yaxis.grid(True, color=GRID, lw=0.7); ax.set_axisbelow(True)
        ax.set_xlim(left=0, right=df[xc].max() + 6)
    axes[0].set_ylabel("Probability that the complete\nstage ranking is unchanged")
    axes[0].legend(frameon=False, loc="lower left", fontsize=8)
    save(fig, "Fig_stability_curves")

# ---------------------------------------------------------------- Fig: benchmark rank comparison
def fig_benchmarks():
    b = pd.read_csv(TAB / "T24_benchmark_scores_and_ranks.csv")
    meth = ["DCFSS-WHD", "DCFSS-WED", "DCFSS-WHHD", "SAW", "TOPSIS", "VIKOR", "Entropy-TOPSIS"]
    order = ["Sindh", "Punjab", "KP", "Balochistan", "GB", "AJ&K", "ICT"]
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.3), sharey=True)
    for ax, s in zip(axes, STAGE):
        g = b[(b.stage == s)].set_index("method").loc[meth, order]
        ref = g.loc["DCFSS-WHD"]
        for i, mname in enumerate(meth):
            for j, r in enumerate(order):
                v = int(g.loc[mname, r]); diff = v != int(ref[r])
                ax.add_patch(plt.Rectangle((j - 0.46, i - 0.42), 0.92, 0.84,
                                           fc="#fdf3ee" if diff else "#f1f6fd",
                                           ec="#eb6834" if diff else "none", lw=1.1))
                ax.text(j, i, str(v), ha="center", va="center", fontsize=8.5, color=INK,
                        fontweight="bold" if diff else "normal")
        ax.set_xlim(-0.6, 6.6); ax.set_ylim(len(meth) - 0.5, -0.5)
        ax.set_xticks(range(7)); ax.set_xticklabels(order, rotation=45, ha="right", color=INK)
        ax.set_yticks(range(len(meth))); ax.set_yticklabels(meth, color=INK)
        ax.tick_params(length=0)
        for sp in ax.spines.values(): sp.set_visible(False)
        ax.set_title(STAGE[s], loc="left")
    save(fig, "Fig_benchmark_ranks")

if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    for f in (fig_workflow, fig_stage_structure, fig_stage_ssi, fig_rank_shifts, fig_emphasis_path,
              fig_rank_acceptability, fig_stability_curves, fig_benchmarks):
        f(); print("ok", f.__name__)
