import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import geometry as G

EXT = G.EXT_WALL_T

GAL_X0 = G.FF_GALLERY_X0                  # 18.0
GAL_X1_MAIN = G.FF_GALLERY_X1_MAIN        # 28.0
GAL_X1_CANT = G.FF_GALLERY_X1_CANTILEVER  # 36.0
GAL_NORTH = G.FF_GALLERY_NORTH_EXT        # 47.0 -- matches P10

def make():
    fig, ax = new_sheet("06", "TERRACE FLOOR PLAN", "1:75", "A-004")

    # Terrace slab outline: matches the first-floor footprint below it --
    # main building + gallery cantilever over the bike-parking canopy +
    # the north extension landing on column P10. REVISION 8: the north
    # extension covers only the CANTILEVER width (GAL_X1_MAIN..GAL_X1_CANT),
    # not the full gallery width back to GAL_X0/P11-P14 -- removes the extra
    # slab that had been shown between P10 and P14.
    outline = [(0, 0), (GAL_X1_CANT, 0), (GAL_X1_CANT, GAL_NORTH), (GAL_X1_MAIN, GAL_NORTH),
               (GAL_X1_MAIN, 38), (0, 38)]
    ax.add_patch(mpatches.Polygon(outline, closed=True, fill=False, edgecolor='black', lw=1.8))
    for (x0, y0), (x1, y1) in zip(outline, outline[1:] + outline[:1]):
        wall_band(ax, x0, y0, x1, y1, 0.5)
    ax.text((GAL_X1_CANT)/2, -1.6, "PARAPET WALL 3'-0\" HIGH", fontsize=6.8, ha='center', family='monospace')

    # REVISION 5: staircase relocated -- it is now EXTERNAL, in the bike-
    # parking zone between P2 and P3 (see A-005), arriving at the terrace's
    # East edge. A small headroom hood/enclosure over the top flight sits
    # right at that edge.
    sy0, sy1 = G.STAIR_Y
    stair_w = G.STAIR_X[1] - G.STAIR_X[0]
    mx0, my0, mw, mh = GAL_X1_CANT - stair_w, sy0, stair_w, sy1 - sy0
    ax.add_patch(mpatches.Rectangle((mx0, my0), mw, mh, facecolor='none', edgecolor='black', lw=1.6))
    for i in range(1, 4):
        ax.plot([mx0+i*mw/4, mx0+i*mw/4], [my0, my0+mh], color='black', lw=0.8)
    ax.text(mx0+mw/2, my0-1.0, "STAIRCASE ENTRANCE\n(EXTERNAL)", fontsize=6.2, ha='center', family='monospace', fontweight='bold')
    ax.text(mx0+mw/2, my0+mh+0.7, "min 7'-0\" headroom\nhood over top flight",
            fontsize=5.2, ha='center', va='bottom', family='monospace')

    # Twin overhead water tanks (circular, RCC/sectional), converging risers
    tank_r = 2.8
    t1c, t2c = (11.0, 33.0), (17.0, 33.0)
    for tc in (t1c, t2c):
        ax.add_patch(mpatches.Circle(tc, tank_r, facecolor='none', edgecolor='black', lw=1.6))
    riser = (14.0, 26.5)
    ax.plot([t1c[0], riser[0]], [t1c[1]-tank_r, riser[1]], color='black', lw=1.2)
    ax.plot([t2c[0], riser[0]], [t2c[1]-tank_r, riser[1]], color='black', lw=1.2)
    ax.text(14.0, 24.5, "OVERHEAD TANK\n(2 No.)", fontsize=6.8, ha='center', va='top', fontweight='bold', family='monospace')

    # Two solar panel zones flanking the tanks
    sp1 = (2.0, 30.0, 6.0, 6.0)
    sp2 = (20.0, 30.0, 6.0, 6.0)
    for sp in (sp1, sp2):
        ax.add_patch(mpatches.Rectangle(sp[:2], sp[2], sp[3], facecolor='none', edgecolor='black', lw=1.3))
        for i in range(1, 4):
            ax.plot([sp[0], sp[0]+sp[2]], [sp[1]+i*sp[3]/4, sp[1]+i*sp[3]/4], color='black', lw=0.35)
        ax.text(sp[0]+sp[2]/2, sp[1]+sp[3]/2, "SOLAR", fontsize=7.5, ha='center', va='center',
                fontweight='bold', family='monospace')

    ax.text((GAL_X0)/2, 8, "OPEN TERRACE /\nFUTURE UTILITY SPACE",
            fontsize=7.5, ha='center', va='center', family='monospace')

    for name, (x, y) in G.COLS.items():
        column(ax, x, y, *G.COL_SIZE, label=name, fontsize=6.0)

    dim_h(ax, 0, GAL_X1_CANT, -10.0, text=f"{GAL_X1_CANT:.0f}'-0\" (E-W)", fontsize=6.6)
    dim_v(ax, 0, 38, GAL_X1_CANT+6.5, text="38'-0\" (N-S, MAIN)", fontsize=6.6)
    dim_v(ax, 38, GAL_NORTH, GAL_X1_MAIN-2.0, text=f"{GAL_NORTH-38:.1f}' EXT.", fontsize=6.0, right=False)

    scale_bar_ft(ax, -6, GAL_NORTH+2, unit=5, n=4)
    set_view(ax, -9, GAL_X1_CANT+16, -11, GAL_NORTH+6)
    rotate_plan_cw90(ax)
    north_arrow(fig, 0.92, 0.90, angle=90)

    notes_block(fig, [
        "REVISION 8: Terrace slab matches the first floor below: main building + gallery cantilever over the bike-parking canopy, north extension covering only the cantilever width (P6/P9-P10 to canopy line), landing on P10.",
        "The extra slab previously shown extending the north extension back to the P11-P14 line (i.e. between P10 and P14) has been removed per client instruction.",
        "Parapet wall 3'-0\" high all around the terrace edge, coping on top.",
        "REVISION 8: Common staircase relocated OUTSIDE, in the bike-parking zone between columns P2 and P3 -- the original 14' bay (see Sheet A-005), now 3'-0\" wide -- arriving at the terrace's East edge through a small headroom hood (min 7'-0\" clear over the top flight), \n per the client's markup.",
        "Two overhead RCC/sectional water tanks (each sized for a typical 1000-2000L), fed by a common riser from the common plumbing shaft below; verify combined capacity vs. daily demand for all 4 first-floor rooms + 2 ground-floor units.",
        "Two Solar PV panel zones on raised MS mounting structures, tilted south-facing, flanking the tanks so neither shades the other; provide a hot-water line from either tank to a solar water heater if required.",
        "Remaining terrace kept as open/future utility space; slope terrace surface (1:100 min) toward a proper rainwater drainage outlet with down-take pipe.",
    ], y=0.088)
    return fig
