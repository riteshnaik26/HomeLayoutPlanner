import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import geometry as G

def two_way_arrows(ax, x, y, w, h):
    # FancyArrowPatch added via add_patch (NOT ax.annotate) so a post-hoc
    # plan rotation (rotate_plan_cw90, which transforms ax.patches) carries
    # these correctly -- an annotate()-based arrow is stored under ax.texts
    # and its arrow geometry is NOT reliably re-transformed by that pass.
    m = 0.18
    ax.add_patch(mpatches.FancyArrowPatch((x+w*m, y+h/2), (x+w*(1-m), y+h/2),
                 arrowstyle='<->', mutation_scale=8, lw=0.8, color='black'))
    ax.add_patch(mpatches.FancyArrowPatch((x+w/2, y+h*m), (x+w/2, y+h*(1-m)),
                 arrowstyle='<->', mutation_scale=8, lw=0.8, color='black'))

def make():
    fig, ax = new_sheet("08", "SLAB LAYOUT & REINFORCEMENT DIRECTION PLAN", "1:100", "S-004")

    GX = [G.GX_WEST, G.GX_MID, G.GX_EAST]
    GY = G.GY
    panels = []
    for i in range(len(GX)-1):
        for j in range(len(GY)-1):
            panels.append((GX[i], GY[j], GX[i+1]-GX[i], GY[j+1]-GY[j]))

    for (x, y, w, h) in panels:
        ax.add_patch(mpatches.Rectangle((x, y), w, h, facecolor='0.96', edgecolor='black', lw=1.2))
        two_way_arrows(ax, x, y, w, h)
        ax.text(x+w/2, y+h+0.5, f"{w:.0f}'-0\" x {h:.0f}'-0\"\nSLAB {5 if w*h<180 else 6}\" THK",
                fontsize=6.0, ha='center', family='monospace')

    # External common staircase (REVISION 5) -- reference only, not part of this slab
    sx0, sx1 = G.STAIR_X
    sy0, sy1 = G.STAIR_Y
    ax.add_patch(mpatches.Rectangle((sx0, sy0), sx1-sx0, sy1-sy0, facecolor='none',
                                     edgecolor='black', lw=1.2, linestyle='--'))
    ax.text((sx0+sx1)/2, (sy0+sy1)/2, "EXTERNAL\nSTAIR\n(own waist slab,\nsee A-005)",
            fontsize=6.0, ha='center', va='center', family='monospace')

    for name, (x, y) in G.COLS.items():
        if 0 <= x <= G.BW and 0 <= y <= G.BD:
            column(ax, x, y, *G.COL_SIZE)

    dim_h(ax, 0, G.BW, -3.4, text="28'-0\"", fontsize=7)
    dim_v(ax, 0, G.BD, -3.4, text="38'-0\"", fontsize=7, right=False)

    scale_bar_ft(ax, -3, -8, unit=10, n=4)
    set_view(ax, -6, sx1 + 6, -10, G.BD + 6)
    rotate_plan_cw90(ax)
    north_arrow(fig, 0.90, 0.90, angle=90)

    notes_block(fig, [
        "RCC slab thickness 5\" (125mm) for panels under 180 sq.ft, 6\" (150mm) for larger panels -- typical for a domestic two-way slab, confirm by design.",
        "Double-headed arrows indicate the two principal reinforcement (bottom steel) directions for each two-way slab panel; provide torsion steel at all discontinuous corners.",
        "Slab panels are bounded by the main/secondary beam grid shown on Sheet S-003. REVISION 5: the former internal stair opening is removed -- the corridor is now fully slabbed.",
        "The common staircase is now external (bike-parking zone, between P2 and P3) with its own independent waist slab -- see Sheet A-005; not part of this main-building slab.",
        "Provide extra top steel over all beam supports (negative moment zone), typically 0.3 x span length from the face of support, per structural design.",
        "M20 grade concrete, Fe500 grade reinforcement assumed typical; nominal cover 20mm (bottom) / 15mm (top) unless noted otherwise by the structural engineer.",
    ], y=0.088)
    return fig
