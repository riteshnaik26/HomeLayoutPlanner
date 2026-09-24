import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import geometry as G

EXT = G.EXT_WALL_T
INT = G.INT_WALL_T

RY = G.FF_ROOM_Y_BOUNDS          # [0, 9.5, 19, 28.5, 38]
BAL_X0 = -G.FF_BALCONY_DEPTH     # -6.0
BATH_X1 = G.FF_BATH_DEPTH        # 6.0
ROOM_X1 = BATH_X1 + G.FF_ROOM_DEPTH   # 20.0
GAL_X0 = G.FF_GALLERY_X0          # 20.0
GAL_X1_MAIN = G.FF_GALLERY_X1_MAIN        # 28.0
GAL_X1_CANT = G.FF_GALLERY_X1_CANTILEVER  # 36.0
GAL_NORTH = G.FF_GALLERY_NORTH_EXT         # 42.5


def make():
    fig, ax = new_sheet("05", "FIRST FLOOR PLAN (4 ROOMS + GALLERY + BACK BALCONY)", "1:75", "A-003")

    # main enclosed walls
    wall_band(ax, 0, 0, 28, 0, EXT)
    wall_band(ax, ROOM_X1, 0, ROOM_X1, 38, EXT)   # west face of the gallery / east face of rooms zone -- internal, shown light
    wall_band(ax, 0, 0, 0, 38, EXT)
    wall_band(ax, 28, 0, 28, 38, EXT)
    wall_band(ax, 0, 38, 28, 38, EXT)

    # room / bath partitions per room row
    for i in range(4):
        y0, y1 = RY[i], RY[i+1]
        wall_band(ax, BATH_X1, y0, BATH_X1, y1, INT)   # bath | room
        if i > 0:
            wall_band(ax, 0, y0, ROOM_X1, y0, INT)      # between rooms (full depth incl. bath)

    # back balcony (continuous, projects into the 6' west setback)
    ax.add_patch(mpatches.Rectangle((BAL_X0, 0), G.FF_BALCONY_DEPTH, 38, facecolor='0.95', edgecolor='black', lw=1.4))
    ax.text(BAL_X0 + G.FF_BALCONY_DEPTH/2, 19, "CONTINUOUS BACK BALCONY - 6'-0\" DEEP\n(PROJECTS OVER WEST GARDEN SETBACK)",
            fontsize=6.4, ha='center', va='center', rotation=90, family='monospace')
    for i in range(1, 4):
        ax.plot([BAL_X0, BAL_X0+G.FF_BALCONY_DEPTH], [RY[i], RY[i]], color='0.5', lw=0.5, linestyle=':')
    for railx in (BAL_X0,):
        ax.plot([railx, railx], [0, 38], color='black', lw=1.8)

    # rooms + baths
    for i in range(4):
        y0, y1 = RY[i], RY[i+1]
        w = y1 - y0
        ax.add_patch(mpatches.Rectangle((0, y0), BATH_X1, w, facecolor='none', edgecolor='black', lw=1.3))
        ax.add_patch(mpatches.Rectangle((BATH_X1, y0), G.FF_ROOM_DEPTH, w, facecolor='none', edgecolor='black', lw=1.3))
        room_label(ax, (BATH_X1+ROOM_X1)/2, y0 + w - 1.0, f"ROOM {i+1}", f"{ft_in(G.FF_ROOM_DEPTH)} x {ft_in(w)}", fontsize=7.2)
        bed_w = min(4.0, G.FF_ROOM_DEPTH - 1.5)
        bed_h = min(5.5, w - 2.0)
        bed_x, bed_y = BATH_X1 + 0.75, y0 + w/2 - bed_h/2
        ax.add_patch(mpatches.Rectangle((bed_x, bed_y), bed_w, bed_h, facecolor='0.9', edgecolor='black', lw=0.8))
        ax.text(bed_x+bed_w/2, y0+w/2, "BED", fontsize=6.0, ha='center', va='center', family='monospace')
        ax.text(BATH_X1*0.5, y0+w/2, "BATH", fontsize=6.0, ha='center', va='center', rotation=90, family='monospace')
        ventilator(ax, 0, y0+w/2-0.75, 1.5, wall='v')

        n = i + 1
        # C: bath <-> room (washroom entrance)
        door(ax, BATH_X1, y0+w*0.55, 2.3, wall='h', hinge='start', swing=1)
        ax.text(BATH_X1+0.3, y0+w*0.55+2.6, f"C{n}", fontsize=6.5, color='#006600', fontweight='bold', family='monospace')
        # H: room <-> gallery (room main entrance)
        door(ax, ROOM_X1, y0+w*0.35, 2.6, wall='h', hinge='start', swing=-1)
        ax.text(ROOM_X1-1.0, y0+w*0.15, f"H{n}", fontsize=6.5, color='#8B0000', fontweight='bold', family='monospace')
        # B: bath <-> balcony (balcony door)
        door(ax, 0.0, y0+w/2-1.25, 2.5, wall='v', hinge='start', swing=1)
        ax.text(0.3, y0+w/2+1.6, f"B{n}", fontsize=6.5, color='#8B0000', fontweight='bold', family='monospace')

    # gallery (internal portion + cantilever over bike-parking + north extension)
    # REVISION 8: north extension covers only the CANTILEVER width (GAL_X1_MAIN..
    # GAL_X1_CANT, i.e. P6/P9-P10 line to the canopy line), landing on P10 --
    # not the full gallery width back to GAL_X0/P11-P14, which was extra slab.
    ax.add_patch(mpatches.Rectangle((GAL_X0, 0), GAL_X1_MAIN-GAL_X0, 38, facecolor='0.97', edgecolor='black', lw=1.3))
    ax.add_patch(mpatches.Rectangle((GAL_X1_MAIN, 0), GAL_X1_CANT-GAL_X1_MAIN, 38, facecolor='0.9', edgecolor='black', lw=1.2, linestyle='--'))
    ax.add_patch(mpatches.Rectangle((GAL_X1_MAIN, 38), GAL_X1_CANT-GAL_X1_MAIN, GAL_NORTH-38, facecolor='0.9', edgecolor='black', lw=1.2, linestyle='--'))
    ax.text((GAL_X0+GAL_X1_CANT)/2, 19, f"GALLERY / LOUNGE\n{GAL_X1_CANT-GAL_X0:.0f}'-0\" x 38'-0\"\n(cantilevers over bike parking,\nextends N to land on P10)",
            fontsize=7.0, ha='center', va='center', family='monospace')
    ax.plot([GAL_X1_MAIN, GAL_X1_MAIN], [0, 38], color='0.4', lw=0.7, linestyle=':')
    ax.text(GAL_X1_MAIN-0.3, 2, "main wall\nbelow", fontsize=5.0, ha='right', family='monospace', color='0.4')

    # External common staircase lands at the gallery's edge, between P2 & P3
    sx0, sx1 = G.STAIR_X
    sy0, sy1 = G.STAIR_Y
    ax.add_patch(mpatches.Rectangle((sx0, sy0), sx1-sx0, sy1-sy0, facecolor='none',
                                     edgecolor='black', lw=1.4, linestyle='--'))
    ax.text((sx0+sx1)/2, (sy0+sy1)/2, "EXTERNAL\nSTAIR\nsee A-005", fontsize=6.0, ha='center', va='center', family='monospace')
    ax.plot([GAL_X1_CANT, GAL_X1_CANT], [sy0, sy1], color='black', lw=2.2)
    ax.text(GAL_X1_CANT+0.3, (sy0+sy1)/2, "GATE", fontsize=5.4, va='center', family='monospace')

    # columns (main grid + canopy line + P10, all relevant to this floor)
    for name, (x, y) in G.COLS.items():
        column(ax, x, y, *G.COL_SIZE, label=name, fontsize=6.4)

    dim_h(ax, 0, BATH_X1, -2.2, text=ft_in(G.FF_BATH_DEPTH), fontsize=6.2)
    dim_h(ax, BATH_X1, ROOM_X1, -2.2, text=ft_in(G.FF_ROOM_DEPTH), fontsize=6.2)
    dim_h(ax, ROOM_X1, GAL_X1_MAIN, -2.2, text=ft_in(GAL_X1_MAIN-ROOM_X1), fontsize=6.2)
    dim_h(ax, GAL_X1_MAIN, GAL_X1_CANT, -2.2, text="8'-0\" CANTILEVER", fontsize=6.2)
    chain_dim_v(ax, RY, -6.5, fontsize=6.4, right=False)
    dim_v(ax, 0, 38, -9.0, text="38'-0\" OVERALL (N-S)", fontsize=7, right=False)

    scale_bar_ft(ax, -6, 44, unit=5, n=4)
    set_view(ax, -12, 44, -11, 48)
    rotate_plan_cw90(ax)
    north_arrow(fig, 0.92, 0.90, angle=90)

    notes_block(fig, [
        f"REVISION 8: Room resized to {ft_in(G.FF_BATH_DEPTH+G.FF_ROOM_DEPTH)} x 9'-6\" total (bath {ft_in(G.FF_BATH_DEPTH)} + room {ft_in(G.FF_ROOM_DEPTH)}), so the P11-P14 column line (x={ft_in(G.GX_MID)}) lands on the Room/Gallery wall, not inside the floor.",
        f"4 independent rooms along the West/garden side, each with a {ft_in(G.FF_BATH_DEPTH)} x 6'-0\" ensuite bath. Door labels: H = room entrance (from gallery), C = washroom entrance (from room), B = balcony door (from bath).",
        "A continuous 6'-0\" deep back balcony runs the full 38' West side, projecting over the West garden setback below; each room's bath opens onto it.",
        f"Gallery/lounge along the East side: {GAL_X1_MAIN-ROOM_X1:.0f}' within the main footprint, cantilevering a further 8' to fully cover the bike-parking width below, and extending north to land squarely on the repositioned column P10.",
        "REVISION 8: The common staircase (see Sheet A-005) is now 3'-0\" wide (was 6'-0\"), a single half-turn flight in the bike-parking zone between P2 and P3; it lands at the gallery's edge through a gated opening at x=36'.",
        "Cantilever design (gallery beyond the main east wall, and the north extension to P10) must be checked and detailed by the structural engineer -- shown here schematically.",
        "Wall thickness: external/load-bearing 9\", internal partitions 4.5\". Room doors 2'-6\"x7'-0\"; bath doors 2'-3\"x7'-0\"; balcony doors 2'-6\"x7'-0\".",
    ], y=0.088)
    return fig
