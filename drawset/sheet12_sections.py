import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import geometry as G

# Vertical datum: GF FFL = 0'-0"
LVL_FOOTING_BOT = -5.0
LVL_FOOTING_TOP = -3.5
LVL_PLINTH_BEAM = -0.75
LVL_GF_FFL = 0.0
LVL_FF_FFL = G.FLOOR_TO_FLOOR
LVL_TERRACE_FFL = 2 * G.FLOOR_TO_FLOOR
LVL_PARAPET_TOP = LVL_TERRACE_FFL + 3.0
LVL_MUMTY_TOP = LVL_TERRACE_FFL + 8.0
SLAB_T = 5.0/12.0
WALL_T = G.EXT_WALL_T


def level_line(ax, x0, x1, y, label):
    ax.plot([x0, x1], [y, y], color='black', lw=0.5, linestyle=(0, (6, 2)))
    ax.text(x1 + 0.6, y, f"EL {label}", fontsize=6.4, va='center', family='monospace')


def draw_section(ax, x0, span, title, opening_at=None):
    x1 = x0 + span
    # ground fill line
    ax.plot([x0-2, x1+2], [-1.5, -1.5], color='black', lw=1.0)
    hatch_ground = np.linspace(x0-2, x1+2, 30)
    for gx in hatch_ground:
        ax.plot([gx, gx-0.3], [-1.5, -1.9], color='black', lw=0.4)

    # footings at both ends (schematic, isolated footing in section)
    for fx in (x0, x1):
        hatch_section_cut(ax, fx-3.0, LVL_FOOTING_BOT, 6.0, LVL_FOOTING_TOP-LVL_FOOTING_BOT, spacing=0.3, lw=0.4)
        ax.add_patch(mpatches.Rectangle((fx-1.0, LVL_FOOTING_TOP), 2.0, LVL_PLINTH_BEAM-LVL_FOOTING_TOP,
                                         facecolor='0.75', edgecolor='black', lw=0.9))
        ax.add_patch(mpatches.Rectangle((fx-WALL_T/2-0.15, LVL_PLINTH_BEAM), WALL_T+0.3, -LVL_PLINTH_BEAM,
                                         facecolor='0.75', edgecolor='black', lw=0.9))

    # walls (both faces) GF and FF, with wall hatch band
    for lo, hi in ((LVL_GF_FFL, LVL_FF_FFL), (LVL_FF_FFL, LVL_TERRACE_FFL)):
        wall_h = hi - lo - SLAB_T
        ax.add_patch(mpatches.Rectangle((x0-WALL_T/2, lo), WALL_T, wall_h, facecolor='0.88', edgecolor='black', lw=1.0))
        ax.add_patch(mpatches.Rectangle((x1-WALL_T/2, lo), WALL_T, wall_h, facecolor='0.88', edgecolor='black', lw=1.0))
        # slab at top of this storey
        if opening_at and abs(hi - LVL_TERRACE_FFL) < 1e-6:
            # terrace slab has the mumty opening -- draw two segments
            ax.add_patch(mpatches.Rectangle((x0, hi-SLAB_T), opening_at[0]-x0, SLAB_T, facecolor='0.6', edgecolor='black', lw=0.8, hatch='///'))
            ax.add_patch(mpatches.Rectangle((opening_at[1], hi-SLAB_T), x1-opening_at[1], SLAB_T, facecolor='0.6', edgecolor='black', lw=0.8, hatch='///'))
        else:
            ax.add_patch(mpatches.Rectangle((x0, hi-SLAB_T), x1-x0, SLAB_T, facecolor='0.6', edgecolor='black', lw=0.8, hatch='///'))
        # window openings (schematic) at mid wall height, skip where stair opening is
        if opening_at:
            wx0, wx1 = opening_at
        else:
            wx0 = wx1 = None
        for wx in (x0 + span*0.22, x0 + span*0.78):
            if wx0 is None or not (wx0 < wx < wx1):
                ax.add_patch(mpatches.Rectangle((wx-1.5, lo+3.0), 3.0, 3.5, facecolor='white', edgecolor='black', lw=0.8))

    # mumty over stair opening
    if opening_at:
        mx0, mx1 = opening_at
        ax.add_patch(mpatches.Rectangle((mx0, LVL_TERRACE_FFL), mx1-mx0, LVL_MUMTY_TOP-LVL_TERRACE_FFL,
                                         facecolor='0.9', edgecolor='black', lw=1.0))
        ax.add_patch(mpatches.Rectangle((mx0, LVL_MUMTY_TOP), mx1-mx0, SLAB_T, facecolor='0.6', edgecolor='black', lw=0.8, hatch='///'))

    # parapet
    ax.add_patch(mpatches.Rectangle((x0-WALL_T/2, LVL_TERRACE_FFL), WALL_T, LVL_PARAPET_TOP-LVL_TERRACE_FFL,
                                     facecolor='0.88', edgecolor='black', lw=1.0))
    ax.add_patch(mpatches.Rectangle((x1-WALL_T/2, LVL_TERRACE_FFL), WALL_T, LVL_PARAPET_TOP-LVL_TERRACE_FFL,
                                     facecolor='0.88', edgecolor='black', lw=1.0))

    for lvl, txt in ((LVL_FOOTING_BOT, "-5'-0\" (FOOTING U/S, SCHEMATIC)"), (LVL_GF_FFL, "±0'-0\" (GF FFL)"),
                     (LVL_FF_FFL, "+10'-6\" (FF FFL)"), (LVL_TERRACE_FFL, "+21'-0\" (TERRACE FFL)"),
                     (LVL_PARAPET_TOP, "+24'-0\" (PARAPET TOP)")):
        level_line(ax, x0-4.5, x1+1.5, lvl, txt)

    ax.text((x0+x1)/2, LVL_MUMTY_TOP+1.6, title, fontsize=9, ha='center', fontweight='bold', family='monospace')


def make():
    fig, ax = new_sheet("12", "BUILDING SECTIONS A-A & B-B", "1:75", "A-006")

    draw_section(ax, 0, G.BD, "SECTION A-A (LOOKING EAST, THROUGH UNIT 2, N-S)")
    dim_h(ax, 0, G.BD, LVL_FOOTING_BOT-1.6, text="38'-0\" (BUILDING DEPTH)", fontsize=6.6)

    off = 55
    draw_section(ax, off, G.BW, "SECTION B-B (LOOKING NORTH, E-W)")
    dim_h(ax, off, off+G.BW, LVL_FOOTING_BOT-1.6, text="28'-0\" (BUILDING WIDTH)", fontsize=6.6)

    set_view(ax, -8, off+G.BW+14, LVL_FOOTING_BOT-4, LVL_MUMTY_TOP+4)

    notes_block(fig, [
        "Datum: Ground Floor finished floor level (FFL) taken as ±0'-0\". Founding/footing levels shown schematically; confirm actual founding depth on site (rocky strata) with the geotechnical/structural engineer.",
        "Floor-to-floor height 10'-6\" (Ground to First, and First to Terrace); slab thickness 5\" typical, beam depths per Sheet S-003.",
        "REVISION 5: the common staircase is now external (see Sheet A-005), in the bike-parking zone between P2 and P3 -- not shown in these two building sections, which cut through the main enclosed building only.",
        "External walls 9\" thick with plaster both sides; parapet wall 3'-0\" high at terrace level.",
        "Window head heights, sill levels and opening sizes shown schematically -- refer to Ground/First Floor plans for exact sizes and positions.",
    ], y=0.088)
    return fig
