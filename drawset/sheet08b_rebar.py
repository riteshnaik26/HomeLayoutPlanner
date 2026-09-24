import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import geometry as G
import numpy as np

R = G.REBAR

def bar_dot(ax, x, y, r=0.35):
    ax.add_patch(mpatches.Circle((x, y), r, facecolor='black', edgecolor='black'))

def rect_section(ax, x0, y0, w, h, lw=1.8):
    ax.add_patch(mpatches.Rectangle((x0, y0), w, h, fill=False, edgecolor='black', lw=lw))

def stirrup_outline(ax, x0, y0, w, h, cover, lw=1.0):
    ax.add_patch(mpatches.Rectangle((x0+cover, y0+cover), w-2*cover, h-2*cover, fill=False, edgecolor='black', lw=lw))

def title_block_detail(ax, x, y, label, fontsize=8.5):
    ax.text(x, y, label, fontsize=fontsize, fontweight='bold', ha='center', family='monospace')


# Column layout: four side-by-side slots, each with a fixed left edge and a
# running Y cursor that each detail advances by its own height + margins.
COL_X = [1.0, 15.0, 29.0, 43.0]
COL_W = 10.0


def make():
    fig, ax = new_sheet("08A", "TYPICAL REINFORCEMENT DETAILS (BAR SIZES & SPACING)", "AS NOTED (schematic sections)", "S-004A")
    ax.set_aspect('equal')
    ax.axis('off')

    # Layout built TOP-DOWN: cursor_top[col] is the Y where the next item's
    # TITLE goes; each item's drawing extends downward from there, followed
    # by its notes, and the cursor then drops below the notes for the next.
    START_TOP = 58.0
    cursor_top = [START_TOP, START_TOP, START_TOP, START_TOP]
    max_y = [START_TOP]

    def place(col, height, title, draw_fn, notes_lines):
        x0 = COL_X[col]
        title_y = cursor_top[col]
        max_y[0] = max(max_y[0], title_y)
        title_block_detail(ax, x0+COL_W/2, title_y, title)
        y0 = title_y - 1.6 - height   # bottom of the drawing (it extends upward by `height`)
        draw_fn(x0, y0)
        yy = y0 - 1.3
        for line in notes_lines:
            ax.text(x0+COL_W/2, yy, line, fontsize=6.6, ha='center', family='monospace')
            yy -= 1.15
        cursor_top[col] = yy - 6.0  # generous gap prevents detail overlap

    # ---- 1. Footing (plan) -- left column ----
    def draw_footing(x0, y0):
        fs = COL_W
        ax.add_patch(mpatches.Rectangle((x0, y0), fs, fs, fill=False, edgecolor='black', lw=1.8))
        n = 9
        for i in range(1, n):
            ax.plot([x0+i*fs/n, x0+i*fs/n], [y0, y0+fs], color='black', lw=0.5)
            ax.plot([x0, x0+fs], [y0+i*fs/n, y0+i*fs/n], color='black', lw=0.5)
    place(0, COL_W, "1. ISOLATED FOOTING - PLAN (BOTTOM MESH)", draw_footing, [
        f"{R['footing']['bottom_bar']}mm dia @ {R['footing']['bottom_spacing']}mm c/c, BOTH WAYS, BOTTOM",
        "6'x6'x1'-6\" thk, bottom mesh only",
        "Pedestal 2'-0\"x2'-0\": 6 No. 12mm main bars,",
        "8mm ties @ 150mm c/c, full pedestal height",
    ])

    # ---- 2. Main beam section -- left column, below footing ----
    def draw_main_beam(x0, y0):
        bw, bh = 6.5, 13.0
        x0c = x0 + (COL_W-bw)/2
        rect_section(ax, x0c, y0, bw, bh)
        stirrup_outline(ax, x0c, y0, bw, bh, 1.0)
        for i in range(3):
            bar_dot(ax, x0c+1.0+i*(bw-2.0)/2, y0+1.0, r=0.28)
            bar_dot(ax, x0c+1.0+i*(bw-2.0)/2, y0+bh-1.0, r=0.28)
        return bh
    place(0, 13.0, "2. MAIN BEAM SECTION (9\"x18\")", draw_main_beam, [
        f"3 No. {R['main_beam']['top_bar']}mm TOP + 3 No. {R['main_beam']['bottom_bar']}mm BOTTOM",
        f"{R['main_beam']['stirrup_bar']}mm dia stirrups @ {R['main_beam']['stirrup_spacing']}mm c/c",
        f"(reduced to {R['main_beam']['stirrup_spacing_support']}mm within 2x depth of every support)",
    ])

    # ---- 3. Slab section -- second column ----
    def draw_slab(x0, y0):
        lw2, lh2 = COL_W, 5.5
        ax.add_patch(mpatches.Rectangle((x0, y0), lw2, lh2, fill=False, edgecolor='black', lw=1.8))
        xs = np.linspace(x0+0.5, x0+lw2-0.5, 14)
        ax.plot(xs, [y0+1.0]*len(xs), color='black', lw=1.0, marker='|', markersize=6)
        ax.plot(xs, [y0+lh2-1.0]*len(xs), color='black', lw=1.0, marker='|', markersize=6, linestyle=(0, (4, 2)))
        ax.text(x0-0.6, y0+1.0, "BOT", fontsize=6.0, ha='right', va='center', family='monospace')
        ax.text(x0-0.6, y0+lh2-1.0, "TOP\n(support)", fontsize=6.0, ha='right', va='center', family='monospace')
        return lh2
    place(1, 5.5, "3. SLAB SECTION (5\"-6\" THICK, TWO-WAY)", draw_slab, [
        f"Main (bottom): {R['slab']['main_bar']}mm dia @ {R['slab']['main_spacing']}mm c/c, shorter span",
        f"Distribution: {R['slab']['dist_bar']}mm dia @ {R['slab']['dist_spacing']}mm c/c",
        "Extra top steel over continuous supports, 0.3x span from face",
    ])

    # ---- 4. Column cross-section -- second column, below slab ----
    def draw_column(x0, y0):
        cw, ch = 12.0, 15.0
        x0c = x0 + (COL_W-cw)/2
        rect_section(ax, x0c, y0, cw, ch)
        stirrup_outline(ax, x0c, y0, cw, ch, 1.5)
        pts = [(x0c+1.5, y0+1.5), (x0c+cw/2, y0+1.5), (x0c+cw-1.5, y0+1.5),
               (x0c+1.5, y0+ch-1.5), (x0c+cw/2, y0+ch-1.5), (x0c+cw-1.5, y0+ch-1.5)]
        for bx, by in pts:
            bar_dot(ax, bx, by)
    ratio = 6*np.pi*(R['column']['main_bar']/2)**2/(12*15*25.4**2)*100
    place(1, 15.0, "4. COLUMN CROSS-SECTION (12\"x15\")", draw_column, [
        f"6 No. {R['column']['main_bar']}mm dia main bars (2 each face)",
        f"{R['column']['tie_bar']}mm dia ties @ {R['column']['tie_spacing']}mm c/c",
        f"(reduced to {R['column']['tie_spacing_joint']}mm within 1x column-width of every joint)",
        f"Steel ratio ≈ {ratio:.2f}% of gross area",
    ])

    # ---- 5. Secondary beam section -- third column ----
    def draw_sec_beam(x0, y0):
        sw, sh = 9.0, 12.0
        x0c = x0 + (COL_W-sw)/2
        rect_section(ax, x0c, y0, sw, sh)
        stirrup_outline(ax, x0c, y0, sw, sh, 1.5)
        for i in range(2):
            bar_dot(ax, x0c+1.8+i*(sw-3.6), y0+1.5)
            bar_dot(ax, x0c+1.8+i*(sw-3.6), y0+sh-1.5)
    place(2, 12.0, "5. SECONDARY BEAM SECTION (9\"x12\")", draw_sec_beam, [
        f"2 No. {R['secondary_beam']['top_bar']}mm TOP + 2 No. {R['secondary_beam']['bottom_bar']}mm BOTTOM",
        f"{R['secondary_beam']['stirrup_bar']}mm dia stirrups @ {R['secondary_beam']['stirrup_spacing']}mm c/c",
        "Plinth/tie beams (9\"x12\"): same detail",
    ])

    # ---- 6. Staircase waist slab -- third column, below secondary beam ----
    def draw_stair(x0, y0):
        steps = 6
        step_w, step_h = 2.4, 1.3
        x0c = x0 + (COL_W - steps*step_w)/2
        xs2, ys2 = [x0c], [y0]
        for i in range(steps):
            xs2 += [x0c+i*step_w, x0c+(i+1)*step_w]
            ys2 += [ys2[-1]+step_h, ys2[-1]+step_h]
        ax.plot(xs2, ys2, color='black', lw=1.6)
        ax.plot(xs2, [y-0.8 for y in ys2], color='black', lw=1.0, linestyle='--')
    place(2, 8.0, "6. STAIRCASE WAIST SLAB", draw_stair, [
        f"Main: {R['stair_waist']['main_bar']}mm dia @ {R['stair_waist']['main_spacing']}mm c/c, along waist",
        f"Distribution: {R['stair_waist']['dist_bar']}mm dia @ {R['stair_waist']['dist_spacing']}mm c/c, across width",
    ])

    # ---- 7. Half/edge footing -- fourth column (REVISION 7) ----
    def draw_half_footing(x0, y0):
        fw, fh = COL_W, 3.0
        x0c = x0
        ax.add_patch(mpatches.Rectangle((x0c, y0), fw, fh, fill=False, edgecolor='black', lw=1.8, hatch='//'))
        n = 9
        for i in range(1, n):
            ax.plot([x0c+i*fw/n, x0c+i*fw/n], [y0, y0+fh], color='black', lw=0.4)
        for i in range(1, 3):
            ax.plot([x0c, x0c+fw], [y0+i*fh/3, y0+i*fh/3], color='black', lw=0.4)
        ax.plot([x0c+fw, x0c+fw], [y0-0.8, y0+fh+0.8], color='black', lw=1.8)
        ax.text(x0c+fw+0.4, y0+fh/2, "boundary\n(no exten-\nsion past\nthis edge)", fontsize=5.2, va='center', family='monospace')
    place(3, 3.0, "7. HALF/EDGE FOOTING (7 No.)", draw_half_footing, [
        "P2, P3, P4, P6, P10, P11, P15",
        "Column at the boundary-side edge; footing extends the full",
        "3'-0\" only into the plot (18 sq.ft, half the normal footing).",
        f"Bottom mesh: {R['footing']['bottom_bar']}mm dia @ {R['footing']['bottom_spacing']}mm c/c, both ways",
        "Tie/plinth beam acts as a STRAP BEAM to the next interior",
        "footing, resisting the eccentric moment -- engineer to confirm.",
    ])

    # ---- 8. Corner/quarter footing -- fourth column (REVISION 7) ----
    def draw_corner_footing(x0, y0):
        fs = COL_W * 0.35
        yb = y0 + 1.3
        x0c = x0 + (COL_W-fs)/2
        ax.add_patch(mpatches.Rectangle((x0c, yb), fs, fs, fill=False, edgecolor='black', lw=1.8, hatch='xx'))
        n = 6
        for i in range(1, n):
            ax.plot([x0c+i*fs/n, x0c+i*fs/n], [yb, yb+fs], color='black', lw=0.4)
            ax.plot([x0c, x0c+fs], [yb+i*fs/n, yb+i*fs/n], color='black', lw=0.4)
        ax.plot([x0c+fs, x0c+fs], [yb-0.6, yb+fs+0.6], color='black', lw=1.8)
        ax.plot([x0c-0.6, x0c+fs+0.6], [yb, yb], color='black', lw=1.8)
        ax.text(x0c+fs/2, y0+0.3, "2 property lines meet here", fontsize=5.4, ha='center', family='monospace')
    place(3, 6.4, "8. CORNER/QUARTER FOOTING (2 No.)", draw_corner_footing, [
        "P1, P5",
        "Trimmed on BOTH sides at the two true plot corners",
        "(9 sq.ft, a quarter of the normal footing). Strap beams",
        "both ways are essential -- structural engineer to confirm",
        "adequacy, or increase footing depth/reinforcement here.",
    ])

    ax.set_xlim(-2, 55)
    ax.set_ylim(min(cursor_top)-1, max_y[0]+2)

    notes_block(fig, [
        f"Grades assumed: concrete {G.CONCRETE_GRADE}, reinforcement {G.FE_GRADE} -- confirm with structural engineer.",
        "All sizes shown are PRELIMINARY / thumb-rule detailing, consistent with typical practice for a low-rise (G+1) RCC-framed residence on rocky soil; they are for coordination and budgeting only.",
        "Nominal cover: 50mm to footings, 40mm to columns, 25mm to beams, 15-20mm to slabs (IS 456 Table 16), unless the structural engineer specifies otherwise.",
        "Lap lengths, development lengths, curtailment points and exact bar cutting/bending schedule (BBS) must be finalised by the structural engineer per IS 456 / SP 34, based on an actual analysis.",
        "See Sheet S-004B for the corresponding preliminary steel quantity estimate.",
    ], y=0.088)
    return fig
