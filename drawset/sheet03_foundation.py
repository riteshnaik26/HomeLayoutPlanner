import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import geometry as G

FOOT = 6.0     # standard footing 6x6 ft
PED = 2.0      # pedestal 2x2 ft

def make():
    fig, ax = new_sheet("03", "FOUNDATION LAYOUT PLAN (ISOLATED FOOTINGS)", "1:100", "S-002")

    ax.add_patch(mpatches.Rectangle((0, 0), G.BW, G.BD, fill=False, edgecolor='black', lw=1.6, linestyle='--'))

    half_footing_cols = []
    for name, (x, y) in G.COLS.items():
        if name in G.FOOT_TRIM:
            fx0, fx1, fy0, fy1 = G.footing_extents(name)
            fw, fh = fx1-fx0, fy1-fy0
            half_footing_cols.append(name)
            ax.add_patch(mpatches.Rectangle((fx0, fy0), fw, fh, facecolor='0.80',
                                             edgecolor='black', lw=1.3, hatch='//'))
        else:
            ax.add_patch(mpatches.Rectangle((x-FOOT/2, y-FOOT/2), FOOT, FOOT,
                                             facecolor='0.88', edgecolor='black', lw=1.1))
        ax.add_patch(mpatches.Rectangle((x-PED/2, y-PED/2), PED, PED,
                                         facecolor='0.6', edgecolor='black', lw=0.9))
        column(ax, x, y, *G.COL_SIZE, fc='black')
        label_y_off = FOOT/2 + 0.5
        ax.text(x, y - label_y_off, name, fontsize=6.6, ha='center', va='top', family='monospace',
                fontweight='bold' if name in half_footing_cols else 'normal')

    # Plinth beam / tie beam grid (schematic, connecting footings -- these
    # also act as STRAP BEAMS resisting the eccentric-footing moment at the
    # 9 boundary columns listed below)
    for gy in G.GY:
        ax.plot([G.GX_WEST, G.GX_EAST], [gy, gy], color='black', lw=0.8)
    for gx in (G.GX_WEST, G.GX_MID, G.GX_EAST):
        ax.plot([gx, gx], [G.GY[0], G.GY[-1]], color='black', lw=0.8)
    ax.plot([G.GX_CANOPY, G.GX_CANOPY], [G.GY_CANOPY[0], G.GY_CANOPY[-1]], color='black', lw=0.8, linestyle=':')
    p9, p10, p5 = G.COLS["P9"], G.COLS["P10"], G.COLS["P5"]
    ax.plot([p9[0], p10[0]], [p9[1], p10[1]], color='black', lw=0.8, linestyle=':')
    ax.plot([p10[0], p5[0]], [p10[1], p5[1]], color='black', lw=0.8, linestyle=':')

    scale_bar_ft(ax, -3, -8, unit=10, n=4)
    set_view(ax, -6, G.BW + 26, -12, G.GY_CANOPY[-1] + 8)
    rotate_plan_cw90(ax)
    north_arrow(fig, 0.92, 0.90, angle=90)

    ax.text(5, 4.5, "PLINTH / BUILDING LINE ABOVE (FOR REFERENCE)", fontsize=6.8,
            ha='center', family='monospace')

    # typical FULL footing detail callout -- drawn AFTER rotation, directly in
    # the final (rotated) frame, so its own internal layout stacks correctly.
    dx0, dy0 = 50, -15
    ax.add_patch(mpatches.Rectangle((dx0, dy0), FOOT, FOOT, facecolor='0.88', edgecolor='black', lw=1.2))
    ax.add_patch(mpatches.Rectangle((dx0+2, dy0+2), PED, PED, facecolor='0.6', edgecolor='black', lw=1.0))
    column(ax, dx0+3, dy0+3, *G.COL_SIZE, fc='black')
    dim_h(ax, dx0, dx0+FOOT, dy0-1.4, text="6'-0\"", fontsize=7)
    dim_v(ax, dy0, dy0+FOOT, dx0-1.4, text="6'-0\"", fontsize=7, right=False)
    ax.text(dx0+3, dy0+FOOT+1.2, "TYPICAL INTERIOR FOOTING (9 No.)", fontsize=7, ha='center',
            fontweight='bold', family='monospace')
    ax.text(dx0+3, dy0-2.8, "18\" THK, PEDESTAL 2'x2' UPTO PLINTH, COLUMN 12\"x15\" ABOVE",
            fontsize=6.6, ha='center', family='monospace')
    ax.text(dx0+3, dy0-4.8, "See Sheet S-004A for the HALF (P2,P3,P4,\nP6,P10,P11,P15) and CORNER (P1,P5)\nfooting details.", fontsize=6.4,
            ha='center', family='monospace', style='italic')

    # Section callout through a standard footing
    sx0 = dx0 + 0
    sy0 = dy0 + 15
    sw, sh = FOOT, 1.5
    hatch_section_cut(ax, sx0, sy0, sw, sh, spacing=0.4, lw=0.5)
    ax.add_patch(mpatches.Rectangle((sx0+2, sy0+sh), 2.0, 2.3, facecolor='none', edgecolor='black', lw=1.0))
    ax.text(sx0+3, sy0-0.3, "SECTION AT FOOTING (SCHEMATIC)\nFilling 3'-0\" compacted above EGL, then\nP.C.C. bed 3\" + footing 18\" thick",
            fontsize=6.5, ha='center', va='top', family='monospace')
    dim_v(ax, sy0, sy0+sh, sx0-1.0, text="18\"", fontsize=6.5, right=False)

    notes_block(fig, [
        "Soil condition: rocky (assumed) -- founding level to be confirmed on site by geotechnical inspection.",
        "Existing house fully demolished; site filled with 3'-0\" compacted (mechanically consolidated) fill above existing ground level before excavation to founding strata.",
        "REVISION 7: 9 of the 18 footings sit at or very near a plot boundary (south party wall, east canopy line, or north corner near P10/P5) and are HALVED on the boundary side(s), per client instruction -- hatched in plan, detailed on Sheet S-004A.",
        "REVISION 8: P1 and P5 are true corners (halved BOTH ways, 9 sq.ft); P2, P3, P4, P6, P10, P11, P15 are halved on one side only (18 sq.ft) -- P15's west side has a full 6' garden setback so only its south side needs trimming.",
        "The remaining 9 footings (P7, P8, P9, P12, P13, P14, P16, P17, P18) are standard 6'x6' = 36 sq.ft.",
        "Plinth/tie beams schematically link all footings along grid lines; for the 9 boundary footings, these also act as STRAP BEAMS resisting the eccentric moment -- confirm sizing with the structural engineer.",
        "P.C.C. (1:4:8) levelling bed, minimum 75mm (3\"), below every footing. Pedestal 2'x2' RCC up to plinth level, same for all 18.",
        "Footing sizes shown are schematic/typical; final sizing (including the reduced boundary footings) must be checked against actual safe bearing capacity (SBC) from a soil test report, the total column loads, and the eccentricity/strap-beam design, by the structural engineer.",
    ], y=0.092)
    return fig
