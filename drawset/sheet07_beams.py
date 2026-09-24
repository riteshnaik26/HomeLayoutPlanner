import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import geometry as G

MAIN_T = 9.0/12.0   # main beam width shown in plan (9")
SEC_T = 9.0/12.0    # secondary beam width in plan also 9" (depth differs, not shown in plan)

def beamline(ax, x0, y0, x1, y1, kind, label=None):
    lw = 2.6 if kind == 'main' else 1.4
    ls = '-' if kind == 'main' else (0, (5, 2))
    ax.plot([x0, x1], [y0, y1], color='black', lw=lw, linestyle=ls, solid_capstyle='butt')
    if label:
        mx, my = (x0+x1)/2, (y0+y1)/2
        ax.text(mx, my+0.4, label, fontsize=5.6, ha='center', family='monospace',
                rotation=0 if abs(y1-y0) < 1e-6 else 90)

def make():
    fig, ax = new_sheet("07", "BEAM LAYOUT PLAN (OVER GROUND FLOOR COLUMNS)", "1:100", "S-003")

    ax.add_patch(mpatches.Rectangle((0, 0), G.BW, G.BD, fill=False, edgecolor='0.6', lw=0.8, linestyle=':'))

    GX = [G.GX_WEST, G.GX_MID, G.GX_EAST]
    GY = G.GY

    # MAIN BEAMS (9"x18") along every grid line
    for gx in GX:
        beamline(ax, gx, GY[0], gx, GY[-1], 'main', "MB 9\"x18\"")
    for gy in GY:
        beamline(ax, GX[0], gy, GX[-1], gy, 'main', "MB 9\"x18\"")
    # canopy line main beam
    beamline(ax, G.GX_CANOPY, G.GY_CANOPY[0], G.GX_CANOPY, G.GY_CANOPY[-1], 'main')
    beamline(ax, G.GX_EAST, GY[0], G.GX_CANOPY, GY[0], 'main')
    beamline(ax, G.GX_EAST, GY[-1], G.GX_CANOPY, GY[-1], 'main')

    # SECONDARY BEAM (9"x12"): mid-corridor partition (y=19), now a single
    # continuous run -- REVISION 5 removed the stair void from this corridor
    beamline(ax, 0, 19, G.BW, 19, 'sec', "SB 9\"x12\"")
    # cantilever support beams: P9-P10 and P10-P5, carrying the 1st-floor
    # gallery's extension out over the car-parking / canopy corner
    p9, p10, p5 = G.COLS["P9"], G.COLS["P10"], G.COLS["P5"]
    beamline(ax, p9[0], p9[1], p10[0], p10[1], 'sec', "CANTILEVER\nBEAM")
    beamline(ax, p10[0], p10[1], p5[0], p5[1], 'sec')

    for name, (x, y) in G.COLS.items():
        if 0 <= x <= G.BW and 0 <= y <= G.BD + 10:
            column(ax, x, y, *G.COL_SIZE, label=name, fontsize=6.6)

    ax.plot([], [], color='black', lw=2.6, label='MAIN BEAM 9"x18"')
    ax.plot([], [], color='black', lw=1.4, linestyle=(0, (5, 2)), label='SECONDARY BEAM 9"x12"')
    ax.legend(loc='lower left', bbox_to_anchor=(1.02, 0.0), fontsize=8, frameon=True)

    dim_h(ax, 0, G.BW, -3.4, text="28'-0\"", fontsize=7)
    dim_v(ax, 0, G.BD, -3.4, text="38'-0\"", fontsize=7, right=False)

    scale_bar_ft(ax, -3, -8, unit=10, n=4)
    set_view(ax, -6, G.BW + 16, -10, G.BD + 8)
    rotate_plan_cw90(ax)
    north_arrow(fig, 0.90, 0.90, angle=90)

    notes_block(fig, [
        "Main beams 9\" x 18\" (width x overall depth) run along every column grid line, both directions, connecting all columns directly.",
        "Secondary beams 9\" x 12\" support the mid-corridor partition (y=19, now a plain continuous wall), and the two cantilever beams P9-P10-P5 that carry the first-floor gallery's extension over the car-parking side.",
        "REVISION 5: the common staircase is now external (bike-parking zone between P2 and P3) and is NOT part of this grid -- it has its own independent waist-slab, stringer beams and foundation; see Sheet A-005.",
        "Beam depths are overall (including slab thickness); clear soffit depth to be confirmed by structural design.",
        "This layout is for the Ground Floor roof (First Floor slab) level. The First Floor roof (Terrace slab) differs -- it must also support the gallery's cantilever over the bike-parking canopy (P1-P5 line) and the mumty -- verify independently, see Sheet A-004.",
        "All beam sizes and reinforcement to be finalised by structural design/BBS; sizes shown are typical/preliminary for a G+1 RCC framed residence.",
    ], y=0.092)
    return fig
