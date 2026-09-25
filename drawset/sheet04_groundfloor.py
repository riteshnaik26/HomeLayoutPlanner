import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import geometry as G

EXT = G.EXT_WALL_T
INT = G.INT_WALL_T

def _unit_rooms(y_bed_bot, y_corr_bot, y_corr_top):
    """Build one unit's room dict. y_bed_bot..y_bed_bot+12 is the Bedroom/
    Living band; y_corr_bot..y_corr_top (7'-0") is this unit's half of the
    shared central corridor (WC/Shower/Kitchen). REVISION 4: the stair no
    longer sits in this corridor (moved outside, see Sheet A-005), so the
    Kitchen now runs the full remaining depth, x=11..28."""
    bed_y0 = y_bed_bot
    return {
        "BEDROOM": (0.0, bed_y0, 11.0, 12.0),
        "LIVING":  (11.0, bed_y0, 17.0, 12.0),
        "WC":      (0.0, y_corr_bot, 4.0, y_corr_top - y_corr_bot),
        "SHOWER":  (4.0, y_corr_bot, 7.0, y_corr_top - y_corr_bot),
        "KITCHEN": (11.0, y_corr_bot, 17.0, y_corr_top - y_corr_bot),
    }

ROOMS_A = _unit_rooms(G.UNIT_A_Y[0], G.CORRIDOR_Y[0], 19.0)
ROOMS_B = _unit_rooms(G.UNIT_B_Y[0], 19.0, G.CORRIDOR_Y[1])


def draw_unit(ax, rooms, unit_name, flip=False):
    for name, (x, y, w, h) in rooms.items():
        ax.add_patch(mpatches.Rectangle((x, y), w, h, facecolor='none', edgecolor='black', lw=1.3))

    b = rooms["BEDROOM"]
    room_label(ax, b[0]+b[2]/2, b[1]+b[3]-0.7, "BEDROOM", f"{b[2]:.0f}'-0\" x {b[3]:.0f}'-0\"", fontsize=7.5)
    bed_w, bed_h = 5.0, 6.0
    ax.add_patch(mpatches.Rectangle((b[0]+1.0, b[1]+1.0), bed_w, bed_h, facecolor='0.9', edgecolor='black', lw=0.8))
    ax.text(b[0]+1.0+bed_w/2, b[1]+1.0+bed_h/2, "BED", fontsize=6.3, ha='center', va='center', family='monospace')
    ax.add_patch(mpatches.Rectangle((b[0]+b[2]-2.2, b[1]+1.0), 1.8, 1.8, facecolor='0.9', edgecolor='black', lw=0.7))
    ax.text(b[0]+b[2]-1.3, b[1]+1.9, "WD", fontsize=5.6, ha='center', va='center', family='monospace')

    liv = rooms["LIVING"]
    room_label(ax, liv[0]+liv[2]/2, liv[1]+liv[3]-0.7, "LIVING ROOM", f"{liv[2]:.0f}'-0\" x {liv[3]:.0f}'-0\"", fontsize=7.5)
    ax.add_patch(mpatches.Rectangle((liv[0]+1.0, liv[1]+1.0), liv[2]-2.0, 1.8, facecolor='0.9', edgecolor='black', lw=0.7))
    ax.text(liv[0]+liv[2]/2, liv[1]+1.9, "SOFA", fontsize=6, ha='center', family='monospace')
    ax.add_patch(mpatches.Circle((liv[0]+liv[2]-2.5, liv[1]+liv[3]-2.5), 1.1, facecolor='none', edgecolor='black', lw=0.7))
    ax.text(liv[0]+liv[2]-2.5, liv[1]+liv[3]-2.5, "DINING", fontsize=5.2, ha='center', va='center', family='monospace')

    wc = rooms["WC"]
    room_label(ax, wc[0]+wc[2]/2, wc[1]+wc[3]/2, "WC", f"4'-0\"x{wc[3]:.0f}'-0\"", fontsize=6.4)
    sh = rooms["SHOWER"]
    room_label(ax, sh[0]+sh[2]/2, sh[1]+sh[3]/2, "SHOWER", f"7'-0\"x{sh[3]:.0f}'-0\"", fontsize=6.4)
    ax.plot([sh[0]+sh[2]/2], [sh[1]+sh[3]/2-1.2], marker='o', markersize=3, color='black')

    k = rooms["KITCHEN"]
    room_label(ax, k[0]+k[2]/2, k[1]+k[3]-0.6, "KITCHEN", f"{k[2]:.0f}'-0\"x{k[3]:.0f}'-0\"", fontsize=6.8)
    ax.add_patch(mpatches.Rectangle((k[0], k[1]), 2.0, k[3]-1.0, facecolor='0.85', edgecolor='black', lw=0.8))
    ax.text(k[0]+1.0, k[1]+(k[3]-1.0)/2, "PLATFORM\n+ SINK", fontsize=5.2, ha='center', va='center',
            rotation=90, family='monospace')


def draw_doors_windows(ax, rooms, flip=False, ext_x0=0.0, ext_x1=28.0):
    b, liv, wc, sh, k = (rooms["BEDROOM"], rooms["LIVING"], rooms["WC"], rooms["SHOWER"], rooms["KITCHEN"])
    door(ax, 11, b[1]+4.5, 2.5, wall='v', hinge='start', swing=1)          # bedroom <-> living
    door(ax, 4, wc[1]+wc[3]-2.5 if flip else wc[1], 2.5, wall='h', hinge='start', swing=1)   # wc<->shower
    door(ax, 11, sh[1]+sh[3]/2-1.25, 2.5, wall='v', hinge='start', swing=-1)  # shower <-> kitchen
    # REVISION 9: back door / 3'-0" passage, Bedroom <-> WC (washroom), so each
    # bedroom has direct ensuite-style access to its washroom without going
    # through the Living Room. Fully within the WC's 4'-0" wide wall (x=0-4),
    # swings into the Bedroom (clear of the WC fixtures).
    door(ax, 0.5, b[1]+b[3] if not flip else b[1], 3.0, wall='h', hinge='start', swing=-1 if not flip else 1)
    # REVISION 9: main entrance door, in the Living Room (hall), east wall
    door(ax, ext_x1, liv[1]+liv[3]-4.0, 3.0, wall='v', hinge='start', swing=-1)   # unit's own entry, east wall
    window(ax, ext_x0, b[1]+3.5, 4.0, wall='v')
    window(ax, ext_x1, liv[1]+2.0, 5.0, wall='v')
    ventilator(ax, ext_x0, wc[1]+wc[3]/2-0.75, 1.5, wall='v')
    ventilator(ax, ext_x0, sh[1]+sh[3]/2-0.75, 1.5, wall='v')


def make():
    fig, ax = new_sheet("04", "GROUND FLOOR PLAN (TWO RESIDENTIAL UNITS)", "1:75", "A-002")

    wall_band(ax, 0, 0, 28, 0, EXT)
    wall_band(ax, 0, 0, 0, 38, EXT)
    wall_band(ax, 28, 0, 28, 38, EXT)
    wall_band(ax, 0, 38, 28, 38, EXT)

    # unit / corridor dividing walls -- now continuous (no stair opening)
    for y in (12.0, 26.0):
        wall_band(ax, 0, y, 28, y, G.COMMON_WALL_T)
    wall_band(ax, 0, 19, 28, 19, INT)   # mid-corridor divider between the 2 units' WC/Shower/Kitchen

    for rooms in (ROOMS_A, ROOMS_B):
        b, liv, wc, sh, k = (rooms["BEDROOM"], rooms["LIVING"], rooms["WC"], rooms["SHOWER"], rooms["KITCHEN"])
        wall_band(ax, 11, b[1], 11, b[1]+b[3], INT)                 # bedroom | living
        wall_band(ax, 4, wc[1], 4, wc[1]+wc[3], INT)                # wc | shower
        wall_band(ax, 11, wc[1], 11, wc[1]+wc[3], INT)              # shower | kitchen

    draw_unit(ax, ROOMS_A, "UNIT 1", flip=False)
    draw_unit(ax, ROOMS_B, "UNIT 2", flip=True)
    draw_doors_windows(ax, ROOMS_A, flip=False)
    draw_doors_windows(ax, ROOMS_B, flip=True)

    ax.text(2, 1.0, "UNIT 1 (SOUTH)", fontsize=9.5, fontweight='bold', family='monospace')
    ax.text(2, 37.2, "UNIT 2 (NORTH)", fontsize=9.5, fontweight='bold', family='monospace')

    for name, (x, y) in G.COLS.items():
        if 0 <= x <= 28 and 0 <= y <= 38:
            column(ax, x, y, *G.COL_SIZE)

    # External common staircase -- reference outline only (see A-005 for detail)
    sx0, sx1 = G.STAIR_X
    sy0, sy1 = G.STAIR_Y
    ax.add_patch(mpatches.Rectangle((sx0, sy0), sx1-sx0, sy1-sy0, facecolor='0.93',
                                     edgecolor='black', lw=1.3, linestyle='--'))
    ax.text((sx0+sx1)/2, (sy0+sy1)/2, "COMMON\nSTAIRCASE\n(EXTERNAL,\nDOG-LEG)\n3'-0\" WIDE\nsee A-005",
            fontsize=6.2, ha='center', va='center', family='monospace')

    for name, (x, y) in G.COLS.items():
        if 28 <= x <= 42 and 0 <= y <= 47:
            column(ax, x, y, *G.COL_SIZE, label=name, fontsize=6.2)

    chain_dim_h(ax, [0, 4, 11, 17, 28], -2.4, fontsize=6.4)
    dim_h(ax, 0, 28, -4.8, text="28'-0\" (BUILDING WIDTH, E-W)", fontsize=7)
    chain_dim_v(ax, [0, 12, 19, 26, 38], 30.5, fontsize=6.4)
    dim_v(ax, 0, 38, 31.5, text="38'-0\" (BUILDING DEPTH, N-S)", fontsize=7)

    set_view(ax, 0, 40, -8, 44)
    rotate_plan_cw90(ax)
    north_arrow(fig, 0.92, 0.90, angle=90)

    notes_block(fig, [
        "REVISION 5: Common staircase moved OUTSIDE the building -- an external stair in the bike-parking zone between P2 and P3, the original 14' bay (see A-005). Central corridor is now a plain, unbroken spine.",
        "Layout matches the client's own ground-floor sketch: two 12'-deep end units (Bedroom+Living, South and North) flanking a full-depth 14' central corridor.",
        "The 14' central corridor carries each unit's own WC (4'x7'), Shower (7'x7') and Kitchen, now widened to 17'x7' after removing the internal stair void.",
        "External walls 9\" thick; internal partitions 4.5\" thick; corridor/unit dividing walls 9\" (load-bearing, carry the floors above).",
        "Each unit's MAIN ENTRANCE is on the Living Room (hall) East wall; the Kitchen has no external stair door.",
        "REVISION 9: Added a 3'-0\" back door/passage between each Bedroom and its WC (washroom), for direct ensuite-style access without passing through the Living Room; swings into the Bedroom, clear of the WC fixture.",
        "Door sizes: unit entry 3'-0\"x7'-0\", back door (Bedroom-WC) 3'-0\"x7'-0\", other internal 2'-6\"x7'-0\". Window sizes: bedroom 4'-0\"x4'-0\", living room 5'-0\"x4'-6\". Ventilators 1'-6\"x1'-6\" to WC/Shower.",
    ], y=0.088)
    return fig
