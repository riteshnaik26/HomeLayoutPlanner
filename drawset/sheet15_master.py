import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import geometry as G
from sheet04_groundfloor import ROOMS_A, ROOMS_B, draw_unit, draw_doors_windows, EXT, INT

def make():
    fig, ax = new_sheet("15", "DIMENSIONED GROUND-FLOOR BLUEPRINT (MASTER SHEET)", "1:75 (AutoCAD-style)", "A-009")

    wall_band(ax, 0, 0, 28, 0, EXT)
    wall_band(ax, 0, 0, 0, 38, EXT)
    wall_band(ax, 28, 0, 28, 38, EXT)
    wall_band(ax, 0, 38, 28, 38, EXT)
    for y in (12.0, 26.0):
        wall_band(ax, 0, y, 28, y, G.COMMON_WALL_T)
    wall_band(ax, 0, 19, 28, 19, INT)

    for rooms in (ROOMS_A, ROOMS_B):
        b, liv, wc, sh, k = (rooms["BEDROOM"], rooms["LIVING"], rooms["WC"], rooms["SHOWER"], rooms["KITCHEN"])
        wall_band(ax, 11, b[1], 11, b[1]+b[3], INT)
        wall_band(ax, 4, wc[1], 4, wc[1]+wc[3], INT)
        wall_band(ax, 11, wc[1], 11, wc[1]+wc[3], INT)

    draw_unit(ax, ROOMS_A, "UNIT 1", flip=False)
    draw_unit(ax, ROOMS_B, "UNIT 2", flip=True)
    draw_doors_windows(ax, ROOMS_A, flip=False)
    draw_doors_windows(ax, ROOMS_B, flip=True)

    # External common staircase -- reference outline only (see A-005)
    sx0, sx1 = G.STAIR_X
    sy0, sy1 = G.STAIR_Y
    ax.add_patch(mpatches.Rectangle((sx0, sy0), sx1-sx0, sy1-sy0, facecolor='0.93',
                                     edgecolor='black', lw=1.3, linestyle='--'))
    ax.text((sx0+sx1)/2, (sy0+sy1)/2, "STAIR\n(EXTERNAL)\nsee A-005",
            fontsize=6.0, ha='center', va='center', family='monospace')

    for name, (x, y) in G.COLS.items():
        if (0 <= x <= 28 and 0 <= y <= 38) or (28 <= x <= 42 and 0 <= y <= 47):
            column(ax, x, y, *G.COL_SIZE, label=name, fontsize=6.4)

    # FULL chain dimensioning, multiple offset rows (classic AutoCAD "dim style")
    chain_dim_h(ax, [0, 4, 11, 17, 28], -2.2, fontsize=6.2)
    chain_dim_h(ax, [0, G.GX_MID, 28], -4.2, fontsize=6.2)
    dim_h(ax, 0, 28, -6.4, text="28'-0\" (E-W)", fontsize=7.2)

    chain_dim_v(ax, [0, 12, 19, 26, 38], 29.5, fontsize=6.0)
    dim_v(ax, 0, 38, 37.4, text="38'-0\" OVERALL (N-S)", fontsize=7.2)

    chain_dim_h(ax, [0, G.GX_MID, 28], -8.6, fontsize=6.2)
    ax.text(14, -13.0, "COLUMN GRID C/C (E-W)", fontsize=6.0, ha='center', family='monospace')

    ax.text(2, 1.0, "UNIT 1", fontsize=9.5, fontweight='bold', family='monospace')
    ax.text(2, 37.2, "UNIT 2", fontsize=9.5, fontweight='bold', family='monospace')

    scale_bar_ft(ax, 30.5, 2, unit=5, n=4)
    set_view(ax, -9, 52, -13, 44)
    rotate_plan_cw90(ax)
    north_arrow(fig, 0.90, 0.92, angle=90)

    # ---- Schedules -- drawn AFTER rotation, directly in the final (rotated)
    # frame (a schedule/table has no "north" orientation and must read
    # top-to-bottom regardless of the plan's rotation). Positioned clear of
    # the rotated plan + canopy columns (new_x up to ~47).
    sx = 50
    ax.text(sx, 5.5, "DOOR SCHEDULE", fontsize=8, fontweight='bold', family='monospace')
    rows = [("D1", "Unit Entry (E)", "3'-0\" x 7'-0\"", "1"), ("D2", "Unit 2 -> Ext. Stair", "3'-0\" x 7'-0\"", "1"),
            ("D3", "Internal", "2'-6\" x 7'-0\"", "6"), ("D4", "WC/Shower", "2'-3\" x 7'-0\"", "8"),
            ("D5", "Bedroom -> WC (back)", "3'-0\" x 7'-0\"", "2")]
    yy = 4.7
    for r in rows:
        ax.text(sx, yy, f"{r[0]:<3} {r[1]:<14} {r[2]:<14} Qty:{r[3]}", fontsize=6.4, family='monospace')
        yy -= 0.9

    ax.text(sx, yy-0.6, "WINDOW SCHEDULE", fontsize=8, fontweight='bold', family='monospace')
    yy -= 1.4
    rows2 = [("W1", "Living Rm", "5'-0\" x 4'-6\"", "2"), ("W2", "Bedroom", "4'-0\" x 4'-0\"", "2"),
             ("V1", "WC/Shower Ventilator", "1'-6\" x 1'-6\"", "4")]
    for r in rows2:
        ax.text(sx, yy, f"{r[0]:<3} {r[1]:<20} {r[2]:<14} Qty:{r[3]}", fontsize=6.4, family='monospace')
        yy -= 0.9

    ax.text(sx, yy-0.6, "COLUMN & FOOTING SCHEDULE", fontsize=8, fontweight='bold', family='monospace')
    yy -= 1.4
    for r in ["Columns: P1-P18, 18 No., 12\"x15\" RCC",
              "P10: corner column, carries 1st-floor",
              "  gallery extension over car parking",
              "Footings: 18 No. isolated, 1'-6\" thk. 9 full",
              "  6'x6'; 7 HALF (3'x6'/6'x3') + 2 CORNER",
              "  (3'x3') at boundary -- see Sht S-004A",
              "Pedestals: 2'x2' RCC up to plinth",
              "Main beams: 9\"x18\" | Secondary: 9\"x12\"",
              "Slab: 5\"-6\" thk RCC, M20/Fe500 (typ.)"]:
        ax.text(sx, yy, r, fontsize=6.2, family='monospace')
        yy -= 0.85

    ax.text(sx, yy-0.8, "WALL LEGEND", fontsize=8, fontweight='bold', family='monospace')
    yy -= 1.6
    wall_band(ax, sx, yy, sx+1.6, yy, EXT)
    ax.text(sx+2.0, yy, "External wall - 9\"", fontsize=6.2, va='center', family='monospace')
    yy -= 0.8
    wall_band(ax, sx, yy, sx+1.6, yy, INT)
    ax.text(sx+2.0, yy, "Internal partition - 4.5\"", fontsize=6.2, va='center', family='monospace')
    yy -= 0.8
    wall_band(ax, sx, yy, sx+1.6, yy, G.COMMON_WALL_T)
    ax.text(sx+2.0, yy, "Common / party wall - 9\"", fontsize=6.2, va='center', family='monospace')

    notes_block(fig, [
        "This master sheet consolidates the Ground Floor Plan (Sheet A-002) with complete centre-to-centre and clear dimensions, plus door/window/column schedules, in a single AutoCAD-style dimensioned blueprint.",
        "All dimensions in feet-inches unless noted; read in conjunction with Sheets A-001 through A-008 and S-001 through S-004 for full coordination.",
        "Refer to Sheet A-000 for the design-basis reconciliation notes -- several brief dimensions were adjusted marginally to produce a consistent, buildable set.",
    ], y=0.088)
    return fig
