import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import geometry as G
import numpy as np

def _rotate_site_plan(ax, south_wall_label):
    rotate_plan_cw90(ax)
    south_wall_label.set_rotation(90)

def make():
    fig, ax = new_sheet("01", "SITE DEVELOPMENT PLAN", "1\" = 10'-0\" (approx)", "A-001")

    poly = G.SITE_POLY
    ax.add_patch(mpatches.Polygon(poly, closed=True, fill=False, edgecolor='black', lw=2.0))
    for i in range(4):
        p0, p1 = poly[i], poly[(i+1) % 4]
        mx, my = (p0+p1)/2
        dx, dy = p1-p0
        L = np.hypot(dx, dy)
        nx, ny = dy/L, -dx/L
        ax.text(mx + nx*2.2, my + ny*2.2, f"{L:.1f}'", fontsize=8.5, ha='center', va='center', fontweight='bold', family='monospace', rotation=0)
    ax.text(*(poly[0] + [-1.5, -1.5]), "SW", fontsize=8, family='monospace')
    ax.text(*(poly[1] + [0.0, -1.5]), "SE", fontsize=8, family='monospace')
    ax.text(*(poly[2] + [1.0, 0.8]), "NE", fontsize=8, family='monospace')
    ax.text(*(poly[3] + [-1.5, 0.8]), "NW", fontsize=8, family='monospace')

    bx0, by0, bx1, by1 = G.BX0, G.BY0, G.BX1, G.BY1
    ax.add_patch(mpatches.Rectangle((bx0, by0), G.BW, G.BD, facecolor='0.85', edgecolor='black', lw=1.8))
    ax.text((bx0+bx1)/2, (by0+by1)/2, "MAIN BUILDING\nG+1+TERRACE\n28'-0\" x 38'-0\"\n(1,064 SFT COVERAGE)", fontsize=9, ha='center', va='center', fontweight='bold', family='monospace')

    bike_x0, bike_x1 = bx1, bx1 + 8.0
    ax.add_patch(mpatches.Rectangle((bike_x0, by0), 8.0, G.BD, facecolor='none', edgecolor='black', lw=1.0, linestyle='--'))
    ax.text((bike_x0+bike_x1)/2, by0 + G.BD*0.5, "BIKE PARKING\n8'-0\" WIDE", fontsize=8.5, ha='center', va='center', rotation=90, family='monospace')

    # canopy_x = bx0 + G.GX_CANOPY
    # ax.plot([canopy_x, canopy_x], [by0, by0 + G.GY_CANOPY[-1]], color='black', lw=0.8, linestyle=':')
    # ax.text(canopy_x + 1.3, by0 + 2, "COVERED WALKWAY / CANOPY LINE (P1-P5) OVER BIKE PARKING", fontsize=8.3, family='monospace')

    ax.add_patch(mpatches.Rectangle((0, by0), bx0, G.BD, facecolor='none', edgecolor='black', lw=1.0, linestyle='--'))
    ax.text(bx0*0.5, by0 + G.BD*0.5, "GARDEN / OPEN SPACE", fontsize=8.6, ha='center', va='center', rotation=90, family='monospace')

    park_y0, park_y1 = by1, by1 + G.NORTH_SETBACK_SHOWN
    ax.add_patch(mpatches.Rectangle((bx0, park_y0), G.BW, G.NORTH_SETBACK_SHOWN, facecolor='none', edgecolor='black', lw=1.0, linestyle='--'))
    ax.text((bx0+bx1)/2, (park_y0+park_y1)/2, "CAR PARKING\n(7'-10' WIDE)", fontsize=8.5, ha='center', va='center', family='monospace')

    ax.plot([bx0, bx1], [by0, by0], color='black', lw=3.2)
    south_wall_label = ax.text((bx0+bx1)/2, by0 - 1.0, "SOUTH: COMMON / PARTY WALL WITH NEIGHBOURING HOUSE - 0'-0\" SETBACK", fontsize=7.5, ha='center', va='center', family='monospace', fontweight='bold')

    dim_h(ax, 0, bx0, by0 - 3.2, text=f"{G.WEST_SETBACK_SHOWN:.1f}' (shown; target 6'-0\", see Note 1)", fontsize=6.6)
    dim_h(ax, bx1, bike_x1, by0 - 3.2, text="8'-0\" BIKE PARKING", fontsize=6.6)
    dim_v(ax, by1, park_y1, bike_x1 + 1.5, text="8'-0\" (target 7'-10')", fontsize=6.6)
    dim_v(ax, by0, by1, bx0 - 6.8, text="38'-0\" BUILDING (N-S)", fontsize=7)
    dim_h(ax, bx0, bx1, by1 + G.NORTH_SETBACK_SHOWN + 9.0, text="28'-0\" BUILDING (E-W)", fontsize=7)

    scale_bar_ft(ax, poly[:,0].min()+1, poly[:,1].max()+6, unit=10, n=4)
    set_view(ax, poly[:,0].min()-8, poly[:,0].max()+6, poly[:,1].min()-8, poly[:,1].max()+11)
    _rotate_site_plan(ax, south_wall_label)
    north_arrow(fig, 0.92, 0.90, angle=90)

    notes_block(fig, [
        "Plot boundary dimensions taken as given (irregular quadrilateral); corners computed geometrically from the 4 side lengths.",
        "Building oriented 28' E-W x 38' N-S -- see Sheet A-000 Note 1 for why this differs from a literal reading of the brief.",
        "South side has zero setback (shared party wall with existing neighbouring house).",
        "East side: 8'-0\" wide two-wheeler (bike) parking, covered by canopy over columns P1-P5.",
        "REVISION 5: the common staircase is external, sited within this bike-parking zone between columns P2 and P3 (the original 14' bay), flush with the canopy line -- see Sheet A-005.",
        "North side: 7'-0\" to 10'-0\" wide car parking / driveway (shown at a representative 8'-0\").",
        "West side: garden / open space, shown compressed to fit the surveyed plot width -- verify with surveyor.",
        "Existing structure to be fully demolished prior to site filling and excavation.",
    ], y=0.088)
    return fig
