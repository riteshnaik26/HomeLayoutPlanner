import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import geometry as G

def make():
    fig, ax = new_sheet("02", "COLUMN LAYOUT PLAN (P1-P18)", "1:100", "S-001")

    # building outline
    ax.add_patch(mpatches.Rectangle((0, 0), G.BW, G.BD, fill=False, edgecolor='black', lw=1.8))
    # canopy outline
    ax.add_patch(mpatches.Rectangle((G.BW, 0), 8.0, G.GY_CANOPY[-1], fill=False,
                                     edgecolor='black', lw=1.0, linestyle='--'))
    ax.text(G.BW + 4, G.GY_CANOPY[-1] + 6.5, "CANOPY / COVERED WALKWAY OVER BIKE PARKING",
            fontsize=6.8, ha='center', family='monospace')

    # grid lines
    for gy in G.GY:
        ax.plot([-2, G.BW + 2], [gy, gy], color='0.5', lw=0.5, linestyle='-.')
    for gx in (G.GX_WEST, G.GX_MID, G.GX_EAST):
        ax.plot([gx, gx], [-2, G.BD + 10], color='0.5', lw=0.5, linestyle='-.')
    ax.plot([G.GX_CANOPY, G.GX_CANOPY], [-2, G.GY_CANOPY[-1] + 1], color='0.5', lw=0.5, linestyle='-.')

    grid_labels_x = {G.GX_WEST: "1", G.GX_MID: "2", G.GX_EAST: "3", G.GX_CANOPY: "4"}
    for gx, lab in grid_labels_x.items():
        ax.add_patch(mpatches.Circle((gx, G.BD + 3.2), 0.7, fill=False, lw=0.9))
        ax.text(gx, G.BD + 3.2, lab, ha='center', va='center', fontsize=8, fontweight='bold')
    for i, gy in enumerate(G.GY):
        ax.add_patch(mpatches.Circle((-3.2, gy), 0.7, fill=False, lw=0.9))
        ax.text(-3.2, gy, chr(65+i), ha='center', va='center', fontsize=8, fontweight='bold')

    for name, (x, y) in G.COLS.items():
        column(ax, x, y, *G.COL_SIZE, label=name, fontsize=7.2)

    # stair opening for reference
    ax.add_patch(mpatches.Rectangle((G.STAIR_X[0], G.STAIR_Y[0]),
                                     G.STAIR_X[1]-G.STAIR_X[0], G.STAIR_Y[1]-G.STAIR_Y[0],
                                     fill=False, edgecolor='black', lw=0.8, linestyle=':'))
    ax.text((G.STAIR_X[0]+G.STAIR_X[1])/2, (G.STAIR_Y[0]+G.STAIR_Y[1])/2, "STAIR\nOPENING",
            fontsize=6.5, ha='center', va='center', family='monospace')

    # dimensions - E-W chain (canopy row, ground level shown offset below)
    xs_canopy = [0, G.GX_CANOPY]
    chain_dim_h(ax, [G.GX_EAST, G.GX_CANOPY], -3.2, fontsize=7)
    chain_dim_h(ax, [G.GX_WEST, G.GX_MID, G.GX_EAST], -5.6, fontsize=7)
    dim_h(ax, G.GX_WEST, G.GX_EAST, -8.0, text="28'-0\" (P6/P11/P15 to P8/P13/P17 line... = building width)", fontsize=6.5)

    # N-S chain
    chain_dim_v(ax, G.GY, G.BW + 10.5, fontsize=7)
    chain_dim_v(ax, G.GY_CANOPY, G.BW + 13.5, fontsize=7)
    dim_v(ax, 0, G.BD, G.BW + 16.5, text="38'-0\" BUILDING DEPTH (N-S)", fontsize=7)

    p10x, p10y = G.P10_POS
    ax.plot([G.COLS["P9"][0], p10x, G.COLS["P5"][0]], [G.COLS["P9"][1], p10y, G.COLS["P5"][1]],
            color='0.4', lw=0.7, linestyle=':')
    ax.text(p10x - 1.0, p10y + 2.4,
            "P10: directly above P9,\nin line with P5 -- carries the\n1st-floor gallery's extension\nover the car-parking side\n(18th column, not in a stated bay)",
            fontsize=6.0, family='monospace', ha='left')

    scale_bar_ft(ax, -3, -11, unit=10, n=4)
    set_view(ax, -8, G.BW + 24, -13, p10y + 12)
    rotate_plan_cw90(ax)
    for label in ax.texts:
        if label.get_text() == "28'-0\" (P6/P11/P15 to P8/P13/P17 line... = building width)":
            label.set_rotation(90)
            break
    north_arrow(fig, 0.92, 0.90, angle=90)

    notes_block(fig, [
        "18 RCC columns, P1-P18, size 12\" x 15\" (0.3m x 0.38m) throughout, unless noted.",
        "Grid line 4 (P1-P5) is the canopy line over the east bike-parking/entrance walkway, 8'-0\" east of grid line 3.",
        f"Grid spacing: {ft_in(G.GX_MID-G.GX_WEST)} / {ft_in(G.GX_EAST-G.GX_MID)} (E-W, all rows); 12'-0\" / 14'-0\" / 12'-0\" (N-S, rows A-D); canopy row adds a 9'-0\" bay (P4-P5).",
        "P10 is a supplementary corner column between P9 and P5, carrying the first-floor gallery's cantilevered extension over the car-parking side; see Sheet A-000.",
        "All columns to be centred on grid lines shown; verify against structural design/BBS before construction.",
    ], y=0.088)
    return fig
