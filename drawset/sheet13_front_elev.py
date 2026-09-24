import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import geometry as G
from elevation_lib import facade, level_line, LVL_GF_FFL, LVL_FF_FFL, LVL_TERRACE_FFL, LVL_PARAPET_TOP, LVL_MUMTY_TOP

def make():
    fig, ax = new_sheet("13", "FRONT ELEVATION (NORTH)", "1:75", "A-007")

    facade(ax, 0, G.BW, n_win_gf=2, n_win_ff=4, door_x=None)
    ax.text(G.BW+3.5, LVL_FF_FFL+5, "GALLERY (1ST FLOOR)\nEXTENDS TOWARD\nVIEWER OVER CAR\nPARKING - SEE A-003",
            fontsize=5.4, family='monospace')
    for lvl, txt in ((LVL_GF_FFL, "±0'-0\" GF FFL"), (LVL_FF_FFL, "+10'-6\" FF FFL"),
                     (LVL_TERRACE_FFL, "+21'-0\" TERRACE FFL"), (LVL_PARAPET_TOP, "+24'-0\" PARAPET TOP")):
        level_line(ax, -2, G.BW+2, lvl, txt)
    dim_h(ax, 0, G.BW, -3.0, text="28'-0\"", fontsize=7)

    north_arrow(fig, 0.90, 0.90)
    scale_bar_ft(ax, -2, LVL_MUMTY_TOP+3, unit=5, n=4)
    set_view(ax, -6, G.BW+14, -6, LVL_MUMTY_TOP+5)

    notes_block(fig, [
        "North elevation faces the car-parking side; datum GF FFL taken as ±0'-0\" (matches Sheet A-006). Unit entries are on the East face -- see Sheet A-008.",
        "REVISION 5: the common staircase and its headroom hood are external, on the East face (bike-parking side, between P2 and P3) -- not visible here, see Sheet A-008. The first-floor gallery extends toward the viewer over part of the car-parking setback (to column P10) -- see Sheet A-003.",
        "The continuous back balcony is on the opposite (West/garden) face and is not visible in this elevation.",
        "Window/door proportions indicative; exact sizes and positions per Ground/First Floor plans (Sheets A-002/A-003).",
        "All RCC surfaces to receive weatherproof exterior paint/texture finish over sand-faced plaster; parapet coping with weathering slope and drip.",
        "Final architectural treatment (cladding, sun-shades, colour scheme) to be developed at the design-development stage; this is a massing/schematic elevation.",
    ], y=0.088)
    return fig
