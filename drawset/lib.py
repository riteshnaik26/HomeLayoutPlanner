"""
Shared drafting helpers for the RCC residential drawing package.
Units: feet (decimal) for all internal geometry. Sheets rendered on a
landscape sheet with a title block, north arrow and graphic scale bar.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path
import matplotlib.patheffects as pe
import numpy as np
import textwrap

PROJECT_TITLE = "PROPOSED G+1+TERRACE RESIDENTIAL BUILDING"
CLIENT = "Owner"
DRAWN_BY = "Prepared with Claude (schematic design aid)"
DATE = "20-09-2026"

FIG_W, FIG_H = 22.0, 15.5   # inches, landscape sheet

# Multipliers applied to NOTES / TITLE-BLOCK text only (not the drawing
# itself). Left at 1.0 for the normal (large-format) build; the A4-only
# build script raises these before calling each sheet's make(), so the A4
# PDF gets larger, more legible notes/title text without touching the
# large-format PDF or the main drawing's own (overlap-tuned) geometry.
# TITLE_SCALE is kept modest: the left-hand project-title field is already
# width-constrained at 1.0x (long text, fixed-width box) so it is NOT
# scaled at all -- only the sheet title ("plan name"), SCALE/DWG NO and
# SHEET NN fields (right side, generous width) pick up TITLE_SCALE.
TEXT_SCALE = 1.0
TITLE_SCALE = 1.0

def new_sheet(sheet_no, title, scale_txt="AS SHOWN", drawing_no=""):
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    ax = fig.add_axes([0.045, 0.10, 0.93, 0.86])  # main drawing area
    ax.set_aspect('equal')
    ax.set_anchor('NW')
    ax.axis('off')
    _border(fig)
    _titleblock(fig, sheet_no, title, scale_txt, drawing_no)
    return fig, ax

def _border(fig):
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    rect = mpatches.Rectangle((0.012, 0.012), 0.976, 0.976, fill=False,
                               lw=2.2, edgecolor='black')
    ax.add_patch(rect)
    rect2 = mpatches.Rectangle((0.02, 0.02), 0.96, 0.96, fill=False,
                                lw=0.6, edgecolor='black')
    ax.add_patch(rect2)

def _dampen(length, short_thresh, long_thresh, scale):
    # Scales the (scale-1) boost down as text gets longer, reaching exactly
    # 1.0x (i.e. NO boost, but never below the original size) for very long
    # text. When scale==1.0 (large-format build) this is always 1.0
    # regardless of length -- that build is never touched.
    if length <= short_thresh:
        return scale
    if length >= long_thresh:
        return 1.0
    frac = (long_thresh - length) / (long_thresh - short_thresh)
    return 1.0 + (scale - 1.0) * frac

def _fit_fontsize(fig, s, base_fontsize, target_scale, max_width_in, **kwargs):
    """Return a fontsize that boosts base_fontsize toward base_fontsize*
    target_scale, but shrinks (never below base_fontsize) so the rendered
    single-line width of `s` never exceeds max_width_in inches. Measures
    the ACTUAL rendered text extent (font metrics) instead of guessing a
    per-character width, so it stays correct regardless of string length
    or font. When target_scale<=1.0 (large-format build) this is a no-op
    that always returns base_fontsize -- that build is never touched."""
    if target_scale <= 1.0:
        return base_fontsize
    fs = base_fontsize * target_scale
    renderer = fig.canvas.get_renderer()
    probe = fig.text(-1, -1, s, fontsize=fs, **kwargs)
    width_in = probe.get_window_extent(renderer=renderer).width / fig.dpi
    probe.remove()
    if width_in > max_width_in:
        fs = max(base_fontsize, fs * (max_width_in / width_in))
    return fs

def _titleblock(fig, sheet_no, title, scale_txt, drawing_no):
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    # Title block grows taller when TITLE_SCALE > 1 (A4 build only) to give
    # the bigger text room; the large-format build (TITLE_SCALE==1) keeps
    # the exact original 0.095 box height.
    grow = max(0.0, TITLE_SCALE - 1.0)
    x0, y0, x1, y1 = 0.02, 0.02, 0.98, 0.095 + grow * 0.09
    v = (y1 - y0) / 0.075   # vertical proportional-growth factor (1.0 = original box height)
    ax.add_patch(mpatches.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, lw=1.4))
    ax.plot([x0 + 0.48, x0 + 0.48], [y0, y1], color='black', lw=0.9)
    ax.plot([x0, x1], [y0 + 0.045*v, y0 + 0.045*v], color='black', lw=0.7)
    # Fields that must stay single-line get a fontsize measured against the
    # ACTUAL rendered text width (via _fit_fontsize) so they boost toward
    # TITLE_SCALE but never overflow their column, however long the string
    # is -- exact, unlike guessing a per-character width. Proposed and layout
    # name sections each use half of the full-width footer; the layout section
    # leaves room for the SHEET box at the far right.
    left_col_in = (0.48 - 0.01 - 0.005) * FIG_W
    right_col_in = (x1 - 0.09 - (x0 + 0.495) - 0.005) * FIG_W
    subtitle = "G+1+TERRACE RCC RESIDENTIAL (2 UNITS) — SCHEMATIC DESIGN / GFC-BASIS SET"
    client_line = f"Client: {CLIENT}    Date: {DATE}    Not for construction without RCC/Architect stamp"
    scale_line = f"SCALE: {scale_txt}"
    proj_fs = _fit_fontsize(fig, PROJECT_TITLE, 13, TITLE_SCALE, left_col_in,
                             fontweight='bold', family='monospace')
    sub_fs = _fit_fontsize(fig, subtitle, 8.3, TITLE_SCALE, left_col_in, family='monospace')
    client_fs = _fit_fontsize(fig, client_line, 7.3, TITLE_SCALE, left_col_in,
                               family='monospace', style='italic')
    title_fs = _fit_fontsize(fig, title, 11.5, TITLE_SCALE, right_col_in,
                              fontweight='bold', family='monospace')
    scale_fs = _fit_fontsize(fig, scale_line, 8.5, TITLE_SCALE, right_col_in, family='monospace')
    ax.text(x0 + 0.01, y1 - 0.012*v, PROJECT_TITLE, fontsize=proj_fs, fontweight='bold',
            va='top', ha='left', family='monospace')
    ax.text(x0 + 0.01, y0 + 0.034*v, subtitle,
            fontsize=sub_fs, va='top', ha='left', family='monospace')
    ax.text(x0 + 0.01, y0 + 0.006*v, client_line,
            fontsize=client_fs, va='bottom', ha='left', family='monospace', style='italic')
    ax.text(x0 + 0.495, y1 - 0.012*v, title, fontsize=title_fs, fontweight='bold',
            va='top', ha='left', family='monospace')
    ax.text(x0 + 0.495, y0 + 0.022*v, scale_line, fontsize=scale_fs,
            va='center', ha='left', family='monospace')
    ax.text(x0 + 0.495, y0 + 0.006*v, f"DWG NO: {drawing_no}", fontsize=8.5*TITLE_SCALE,
            va='center', ha='left', family='monospace')
    ax.text(x1 - 0.012, y0 + 0.014*v, f"SHEET\n{sheet_no}", fontsize=12*TITLE_SCALE, fontweight='bold',
            va='center', ha='right', family='monospace')
    return y1   # top edge of the title block, so notes_block can sit flush above it

def notes_block(fig, notes, x=0.025, y=0.088, fontsize=8, title="NOTES:", wrap_width=None):
    # Border ALWAYS sized to fit the actual text (line count x fontsize),
    # flush on top of the title block -- not a fixed-height placeholder --
    # so it can never overflow into the title block or the drawing above,
    # however many notes there are or however big the font is. Works the
    # same for the large-format build (TEXT_SCALE==1) and the A4 build
    # (TEXT_SCALE>1, which additionally boosts the font itself).
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis('off')
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    wrapped_notes = [textwrap.fill(n, width=wrap_width) if wrap_width else n for n in notes]
    txt = title + "\n" + "\n".join(f"{i+1}. {n}" for i, n in enumerate(wrapped_notes))
    fs = fontsize * max(TEXT_SCALE, 1.0)
    n_lines = 1 + sum(n.count("\n") + 1 for n in wrapped_notes)
    linespacing = 1.25
    line_h = fs * linespacing / 72.0 / FIG_H
    title_block_top = 0.095 + max(0.0, TITLE_SCALE - 1.0) * 0.09
    box_bottom = title_block_top
    box_top = box_bottom + n_lines * line_h + 0.012
    ax.add_patch(mpatches.Rectangle((0.018, box_bottom), 0.964, box_top - box_bottom,
                                     fill=False, lw=1.2))
    ax.text(x, box_top - 0.008, txt, fontsize=fs, va='top', ha='left', family='monospace',
            linespacing=linespacing)

# ---------------------------------------------------------------- geometry --

def draw_wall_rect(ax, x, y, w, h, thick, hatch=True, lw=1.4, fc='none'):
    """Outline rectangle wall centerline box with wall thickness shown as a
    double-line band drawn OUTSIDE the given clear rectangle is not implied;
    this draws a simple filled/hatched band rectangle of given outer extents."""
    ax.add_patch(mpatches.Rectangle((x, y), w, h, fill=hatch, facecolor='0.82' if hatch else fc,
                                     edgecolor='black', lw=lw, hatch='' ))

def wall_band(ax, x0, y0, x1, y1, thick, lw=1.1):
    """Draw a straight wall segment (centerline x0,y0 to x1,y1) with given
    thickness (ft), shown as a hatched band, works for horizontal/vertical."""
    dx, dy = x1 - x0, y1 - y0
    length = np.hypot(dx, dy)
    if length == 0:
        return
    ux, uy = dx / length, dy / length
    nx, ny = -uy, ux
    t2 = thick / 2.0
    pts = [(x0 + nx * t2, y0 + ny * t2), (x1 + nx * t2, y1 + ny * t2),
           (x1 - nx * t2, y1 - ny * t2), (x0 - nx * t2, y0 - ny * t2)]
    poly = mpatches.Polygon(pts, closed=True, facecolor='0.80', edgecolor='black', lw=lw)
    ax.add_patch(poly)

def column(ax, cx, cy, bx=1.0, by=1.25, label=None, fontsize=7.5, fc='black'):
    """RCC column, size bx x by (ft), centered at (cx,cy)."""
    ax.add_patch(mpatches.Rectangle((cx - bx/2, cy - by/2), bx, by,
                                     facecolor=fc, edgecolor='black', lw=1.0, zorder=5))
    if label:
        ax.text(cx, cy + by/2 + 0.55, label, fontsize=fontsize, ha='center', va='bottom',
                fontweight='bold', zorder=6)

def door(ax, x, y, w, wall='h', hinge='start', swing=1, thick=0.75):
    """Door opening + leaf + quarter-circle swing arc.
    wall: 'h' (opening runs along +x from (x,y)) or 'v' (opening runs along +y).
    hinge: 'start' or 'end' of the opening span.
    swing: +1 or -1, which side of the wall the leaf swings toward."""
    ax.plot([x, x + w if wall == 'h' else x], [y, y if wall == 'h' else y + w],
            color='white', lw=2.8, zorder=3)
    if wall == 'h':
        hx = x if hinge == 'start' else x + w
        far = x + w if hinge == 'start' else x
        leaf_x, leaf_y = hx, y + swing * w
        ax.plot([hx, leaf_x], [y, leaf_y], color='black', lw=1.1, zorder=4)
        ang = np.linspace(0, 90, 30)
        sgn = 1 if far > hx else -1
        arx = hx + sgn * w * np.sin(np.deg2rad(ang))
        ary = y + swing * w * np.cos(np.deg2rad(ang))
        ax.plot(arx, ary, color='black', lw=0.55, zorder=4)
    else:
        hy = y if hinge == 'start' else y + w
        far = y + w if hinge == 'start' else y
        leaf_x, leaf_y = x + swing * w, hy
        ax.plot([x, leaf_x], [hy, leaf_y], color='black', lw=1.1, zorder=4)
        ang = np.linspace(0, 90, 30)
        sgn = 1 if far > hy else -1
        ary = hy + sgn * w * np.sin(np.deg2rad(ang))
        arx = x + swing * w * np.cos(np.deg2rad(ang))
        ax.plot(arx, ary, color='black', lw=0.55, zorder=4)

def window(ax, x, y, w, wall='h', thick=0.75):
    """Window symbol: triple parallel tick lines across the wall opening."""
    if wall == 'h':
        ax.plot([x, x + w], [y, y], color='white', lw=2.6, zorder=3)
        for f in (0.0, 0.5, 1.0):
            pass
        ax.plot([x, x + w], [y - thick*0.18, y - thick*0.18], color='black', lw=1.0, zorder=4)
        ax.plot([x, x + w], [y + thick*0.18, y + thick*0.18], color='black', lw=1.0, zorder=4)
        ax.plot([x, x], [y - thick*0.18, y + thick*0.18], color='black', lw=1.0, zorder=4)
        ax.plot([x + w, x + w], [y - thick*0.18, y + thick*0.18], color='black', lw=1.0, zorder=4)
    else:
        ax.plot([x, x], [y, y + w], color='white', lw=2.6, zorder=3)
        ax.plot([x - thick*0.18, x - thick*0.18], [y, y + w], color='black', lw=1.0, zorder=4)
        ax.plot([x + thick*0.18, x + thick*0.18], [y, y + w], color='black', lw=1.0, zorder=4)
        ax.plot([x - thick*0.18, x + thick*0.18], [y, y], color='black', lw=1.0, zorder=4)
        ax.plot([x - thick*0.18, x + thick*0.18], [y + w, y + w], color='black', lw=1.0, zorder=4)

def ventilator(ax, x, y, w=1.5, wall='h', thick=0.75):
    if wall == 'h':
        ax.plot([x, x + w], [y, y], color='white', lw=2.6, zorder=3)
        ax.plot([x, x + w], [y - thick*0.12, y - thick*0.12], color='black', lw=0.8, zorder=4)
        ax.plot([x, x + w], [y + thick*0.12, y + thick*0.12], color='black', lw=0.8, zorder=4)
    else:
        ax.plot([x, x], [y, y + w], color='white', lw=2.6, zorder=3)
        ax.plot([x - thick*0.12, x - thick*0.12], [y, y + w], color='black', lw=0.8, zorder=4)
        ax.plot([x + thick*0.12, x + thick*0.12], [y, y + w], color='black', lw=0.8, zorder=4)

# ---------------------------------------------------------------- dimensions --

def _ft_in(v):
    feet = int(np.floor(v + 1e-6))
    inch = round((v - feet) * 12)
    if inch == 12:
        feet += 1; inch = 0
    if inch == 0:
        return f"{feet}'-0\""
    return f"{feet}'-{inch}\""

ft_in = _ft_in

def dim_h(ax, x0, x1, y, text=None, offset=0.0, fontsize=7.0, tick=0.18, ext=0.35, above=True):
    y = y + offset
    ax.plot([x0, x1], [y, y], color='black', lw=0.6)
    for xx in (x0, x1):
        ax.plot([xx, xx], [y - tick, y + tick], color='black', lw=0.6)
    e0 = (y - ext, y - 0.03) if above else (y + ext, y + 0.03)
    ax.plot([x0, x0], [min(e0), max(e0)], color='black', lw=0.35)
    ax.plot([x1, x1], [min(e0), max(e0)], color='black', lw=0.35)
    label = text if text is not None else _ft_in(abs(x1 - x0))
    va = 'bottom' if above else 'top'
    dy = 0.06 if above else -0.06
    ax.text((x0 + x1) / 2, y + dy, label, fontsize=fontsize, ha='center', va=va, family='monospace')

def dim_v(ax, y0, y1, x, text=None, offset=0.0, fontsize=7.0, tick=0.18, ext=0.35, right=True):
    x = x + offset
    ax.plot([x, x], [y0, y1], color='black', lw=0.6)
    for yy in (y0, y1):
        ax.plot([x - tick, x + tick], [yy, yy], color='black', lw=0.6)
    e0 = (x - ext, x - 0.03) if not right else (x + 0.03, x + ext)
    ax.plot([min(e0), max(e0)], [y0, y0], color='black', lw=0.35)
    ax.plot([min(e0), max(e0)], [y1, y1], color='black', lw=0.35)
    label = text if text is not None else _ft_in(abs(y1 - y0))
    ha = 'left' if right else 'right'
    dx = 0.08 if right else -0.08
    ax.text(x + dx, (y0 + y1) / 2, label, fontsize=fontsize, ha=ha, va='center',
            rotation=90, family='monospace')

def chain_dim_h(ax, xs, y, offset=0.0, fontsize=6.8, above=True):
    for i in range(len(xs) - 1):
        dim_h(ax, xs[i], xs[i+1], y, offset=offset, fontsize=fontsize, above=above)

def chain_dim_v(ax, ys, x, offset=0.0, fontsize=6.8, right=True):
    for i in range(len(ys) - 1):
        dim_v(ax, ys[i], ys[i+1], x, offset=offset, fontsize=fontsize, right=right)

def room_label(ax, cx, cy, name, dims="", fontsize=9.0):
    """Single text object (name + dims on one call) so a post-hoc plan
    rotation (rotate_plan_cw90) keeps both lines together instead of the
    two independently-positioned calls drifting apart into an overlap."""
    txt = f"{name}\n{dims}" if dims else name
    ax.text(cx, cy, txt, fontsize=fontsize, ha='center', va='center', fontweight='bold', family='monospace')

def north_arrow(fig, x, y, size=0.028, angle=0):
    """x,y in figure-fraction coordinates (0..1). angle: degrees CLOCKWISE
    from pointing up (0=up, the original default; 90=right, for rotated plans)."""
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.patch.set_alpha(0)
    rad = np.deg2rad(angle)
    dx, dy = np.sin(rad), np.cos(rad)
    ax.annotate('', xy=(x + dx*size, y + dy*size), xytext=(x - dx*size*0.2, y - dy*size*0.2),
                arrowprops=dict(arrowstyle='-|>', lw=1.6, color='black'))
    ax.text(x + dx*size*1.28, y + dy*size*1.28, 'N', fontsize=13, ha='center', va='center', fontweight='bold')
    circ = mpatches.Circle((x + dx*size*0.4, y + dy*size*0.4), size * 0.75, fill=False, lw=0.8)
    ax.add_patch(circ)

def rotate_plan_cw90(ax):
    """Rotate all DATA-space content of `ax` 90 deg CLOCKWISE (so North,
    previously +y/up, now points +x/right); remaps axis limits to match.
    Call AFTER all drawing + set_view() for this axes. Text is kept upright
    (rotation reset to 0) for readability; pair with north_arrow(..., angle=90)."""
    import matplotlib.transforms as mtransforms
    rot = mtransforms.Affine2D().rotate_deg(-90)
    base = ax.transData
    for artist in list(ax.patches) + list(ax.lines) + list(ax.collections) + list(ax.artists):
        try:
            artist.set_transform(rot + base)
        except Exception:
            pass
    for txt in list(ax.texts):
        x, y = txt.get_position()
        txt.set_position((y, -x))
        txt.set_rotation(0)
    xlim = ax.get_xlim(); ylim = ax.get_ylim()
    ax.set_xlim(ylim[0], ylim[1])
    ax.set_ylim(-xlim[1], -xlim[0])

def scale_bar_ft(ax, x0, y0, unit=10, n=4, fontsize=6.5):
    """Draws a graphic bar-scale in feet directly in data (feet) coordinates."""
    for i in range(n):
        col = 'black' if i % 2 == 0 else 'white'
        ax.add_patch(mpatches.Rectangle((x0 + i*unit, y0), unit, unit*0.12,
                                         facecolor=col, edgecolor='black', lw=0.6))
    for i in range(n + 1):
        ax.text(x0 + i*unit, y0 - unit*0.18, f"{i*unit}", fontsize=fontsize, ha='center', va='top', family='monospace')
    ax.text(x0, y0 + unit*0.35, "SCALE (FT)", fontsize=fontsize, ha='left', va='bottom', family='monospace')

def set_view(ax, xmin, xmax, ymin, ymax, pad=3.0):
    ax.set_xlim(xmin - pad, xmax + pad)
    ax.set_ylim(ymin - pad, ymax + pad)

def hatch_section_cut(ax, x, y, w, h, spacing=0.35, lw=0.5):
    """Rectangle with 45-degree diagonal hatch (RCC-in-section convention)."""
    ax.add_patch(mpatches.Rectangle((x, y), w, h, facecolor='none', edgecolor='black', lw=1.0))
    k = -h
    while k <= w:
        xA, yA, xB, yB = k, 0, k + h, h
        xs = np.linspace(xA, xB, 40)
        ys = np.linspace(yA, yB, 40)
        mask = (xs >= 0) & (xs <= w) & (ys >= 0) & (ys <= h)
        if mask.any():
            ax.plot(x + xs[mask], y + ys[mask], color='black', lw=lw)
        k += spacing
