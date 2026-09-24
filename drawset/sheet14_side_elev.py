import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import geometry as G
from elevation_lib import facade, level_line, LVL_GF_FFL, LVL_FF_FFL, LVL_TERRACE_FFL, LVL_PARAPET_TOP, LVL_MUMTY_TOP

def make():
    fig, ax = new_sheet("14", "SIDE ELEVATION (EAST)", "1:75", "A-008")

    facade(ax, 0, G.BD, n_win_gf=3, n_win_ff=4, door_x=G.BD*0.65)
    ax.add_patch(mpatches.Rectangle((-3.5, 7.2), 3.0, 0.3, facecolor='0.8', edgecolor='black', lw=1.0))
    ax.plot([-3.5, -3.5], [0, 7.2], color='black', lw=0.8, linestyle=':')
    ax.plot([-0.5, -0.5], [0, 7.2], color='black', lw=0.8, linestyle=':')
    ax.text(-2.0, 8.0, "BIKE-PARKING\nCANOPY BEYOND\n(P1-P5)", fontsize=5.6, ha='center', family='monospace')

    # first-floor gallery projects forward (toward viewer) beyond the GF wall,
    # shown here as a stepped outline over the canopy at FF/parapet level
    from elevation_lib import LVL_FF_FFL, LVL_TERRACE_FFL
    ax.add_patch(mpatches.Rectangle((0, LVL_FF_FFL), G.BD, LVL_TERRACE_FFL-LVL_FF_FFL, fill=False,
                                     edgecolor='black', lw=1.6, linestyle='--'))
    ax.text(G.BD*0.5, LVL_FF_FFL-0.9, "GALLERY PROJECTS FORWARD (EAST) OVER THE CANOPY BELOW - SEE SHEET A-003",
            fontsize=5.6, ha='center', family='monospace')

    # REVISION 5: external common staircase, visible on this face, between
    # P2 and P3 (y=12..26 maps directly to this elevation's horizontal axis)
    sy0, sy1 = G.STAIR_Y
    steps = 9
    step_h = LVL_FF_FFL / steps
    step_w = (sy1 - sy0) / steps
    xs, ys = [sy0], [0]
    for i in range(steps):
        xs += [sy0 + i*step_w, sy0 + (i+1)*step_w]
        ys += [ys[-1] + step_h, ys[-1] + step_h]
    ax.plot(xs, ys, color='black', lw=1.2)
    ax.plot([sy0, sy0], [0, LVL_FF_FFL], color='black', lw=1.0, linestyle=':')
    ax.plot([sy1, sy1], [0, LVL_FF_FFL + 7.0], color='black', lw=1.0, linestyle=':')
    ax.add_patch(mpatches.Rectangle((sy0, LVL_FF_FFL), sy1-sy0, 7.0, fill=False, edgecolor='black', lw=1.2))
    ax.text((sy0+sy1)/2, LVL_FF_FFL+7.6, "EXTERNAL\nSTAIR", fontsize=5.6, ha='center', family='monospace')

    for lvl, txt in ((LVL_GF_FFL, "±0'-0\" GF FFL"), (LVL_FF_FFL, "+10'-6\" FF FFL"),
                     (LVL_TERRACE_FFL, "+21'-0\" TERRACE FFL"), (LVL_PARAPET_TOP, "+24'-0\" PARAPET TOP")):
        level_line(ax, -5, G.BD+2, lvl, txt)
    dim_h(ax, 0, G.BD, -3.0, text="38'-0\"", fontsize=7)

    north_arrow(fig, 0.90, 0.90)
    scale_bar_ft(ax, -5, LVL_MUMTY_TOP+3, unit=5, n=4)
    set_view(ax, -10, G.BD+14, -6, LVL_MUMTY_TOP+5)

    notes_block(fig, [
        "East elevation faces the 8'-0\" bike-parking strip and its covered canopy (columns P1-P5, see Sheets A-001/S-001), shown here in outline for reference.",
        "Datum GF FFL taken as ±0'-0\" (matches Sheet A-006); floor-to-floor 10'-6\", parapet 3'-0\" high.",
        "A secondary unit entry door is shown on this face at ground level (see Sheet A-002 for its exact position on the Living Room wall).",
        "REVISION 5: the common staircase is external, sited on this face in the bike-parking zone between columns P2 and P3 (y=12'-26'), shown here schematically; see Sheet A-005 for the detailed plan/section.",
        "Window/door proportions indicative; exact sizes and positions per Ground/First Floor plans (Sheets A-002/A-003).",
        "Final architectural treatment (cladding, sun-shades, colour scheme) to be developed at the design-development stage; this is a massing/schematic elevation.",
    ], y=0.088)
    return fig
