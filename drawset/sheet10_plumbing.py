import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import geometry as G
from sheet04_groundfloor import ROOMS_A, ROOMS_B, EXT, INT

def pipe(ax, pts, kind='soil', lw=1.6):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    ls = '-' if kind == 'soil' else ((0, (1, 1)) if kind == 'supply' else (0, (6, 2)))
    ax.plot(xs, ys, color='black', lw=lw, linestyle=ls)

def make():
    fig, ax = new_sheet("10", "PLUMBING LAYOUT (WATER SUPPLY, SOIL & WASTE)", "1:75", "P-001")

    wall_band(ax, 0, 0, 28, 0, EXT); wall_band(ax, 0, 0, 0, 38, EXT)
    wall_band(ax, 28, 0, 28, 38, EXT); wall_band(ax, 0, 38, 28, 38, EXT)
    for name, (x, y, w, h) in {**ROOMS_A, **ROOMS_B}.items():
        ax.add_patch(mpatches.Rectangle((x, y), w, h, facecolor='none', edgecolor='0.55', lw=0.8))
        ax.text(x+w/2, y+h/2, name, fontsize=5.6, ha='center', va='center', color='0.45', family='monospace')
    # Common plumbing shaft: WC/Shower for both units already stack at x=0-11
    # in the central corridor, floor to floor -> use the WC/Shower boundary
    # (x~3.5-4.5) as the shared vertical shaft, full corridor depth.
    shaft = (3.0, G.CORRIDOR_Y[0], 2.0, G.CORRIDOR_Y[1]-G.CORRIDOR_Y[0])
    ax.add_patch(mpatches.Rectangle(shaft[:2], shaft[2], shaft[3], facecolor='0.85', edgecolor='black', lw=1.4, hatch='..'))
    ax.text(shaft[0]+shaft[2]/2, shaft[1]+shaft[3]/2, "SHAFT",
            fontsize=5.4, ha='center', va='center', rotation=90, family='monospace')

    for rooms in (ROOMS_A, ROOMS_B):
        wc, sh, k = rooms["WC"], rooms["SHOWER"], rooms["KITCHEN"]
        # soil pipe from WC to shaft
        pipe(ax, [(wc[0]+wc[2]/2, wc[1]+wc[3]/2), (shaft[0]+shaft[2]/2, wc[1]+wc[3]/2)], kind='soil')
        # waste from shower to shaft
        pipe(ax, [(sh[0]+sh[2]/2, sh[1]+sh[3]/2), (shaft[0]+shaft[2]/2, sh[1]+sh[3]/2)], kind='waste')
        # waste from kitchen sink, routed along the corridor to the shaft
        ky = k[1] + k[3] - 1.0
        pipe(ax, [(k[0]+1.0, ky), (shaft[0]+shaft[2]+1.0, ky), (shaft[0]+shaft[2], wc[1]+wc[3]/2)], kind='waste')
        # supply lines from shaft to each fixture
        for r in (wc, sh, k):
            pipe(ax, [(shaft[0]+shaft[2]/2, r[1]+r[3]/2), (r[0]+r[2]/2, r[1]+r[3]/2)], kind='supply')

    pipe(ax, [(shaft[0]+shaft[2]/2, shaft[1]), (shaft[0]+shaft[2]/2, -3.0)], kind='soil', lw=2.0)
    ax.text(shaft[0]+shaft[2]/2+0.4, -2.6, "SOIL/WASTE PIPE DOWN\nTO SEPTIC TANK / SEWER",
            fontsize=6.0, family='monospace')
    # FancyArrowPatch via add_patch (not ax.annotate) so rotate_plan_cw90 carries it correctly.
    ax.add_patch(mpatches.FancyArrowPatch((shaft[0]+shaft[2]/2, 38), (shaft[0]+shaft[2]/2, 33),
                 arrowstyle='-|>', mutation_scale=12, lw=1.2, color='black'))
    ax.text(shaft[0]+shaft[2]+1.0, 34, "OVERHEAD TANK\n(TERRACE) SUPPLY\nRISER DOWN SHAFT",
            fontsize=5.8, family='monospace')

    ax.plot([], [], color='black', lw=1.6, label='Soil pipe (WC)')
    ax.plot([], [], color='black', lw=1.6, linestyle=(0, (6, 2)), label='Waste pipe (shower/kitchen)')
    ax.plot([], [], color='black', lw=1.6, linestyle=(0, (1, 1)), label='Water supply line')
    ax.legend(loc='lower left', bbox_to_anchor=(1.02, 0.0), fontsize=8, frameon=True)

    scale_bar_ft(ax, -6, 40, unit=5, n=4)
    set_view(ax, -9, 34, -8, 42)
    rotate_plan_cw90(ax)
    north_arrow(fig, 0.90, 0.90, angle=90)

    notes_block(fig, [
        "Common plumbing shaft (2'x14') runs the full depth of the central corridor, aligning each unit's WC/Shower with the corresponding first-floor bath and the terrace overhead tank.",
        "Soil pipes (100mm dia. UPVC/CI) from each WC drop through the shaft to a common soil stack, terminating at a septic tank / soak pit or municipal sewer with vent pipe extended above roof level.",
        "Waste pipes (75mm dia.) from showers and kitchen sinks drop through the shaft to a waste stack, discharging to a gully trap and thence to the drainage system.",
        "Water supply: overhead tank on the terrace feeds a gravity riser down the shaft to all WC/Shower/Kitchen fixtures; provide isolation stop-cocks at each floor.",
        "Provide a separate cold-water rising main (with a ground-level sump + pump, if municipal pressure is insufficient) feeding the overhead tank.",
        "All pipe routes shown schematically; final sizing, gradients and inspection chamber locations to be finalised by the plumbing consultant.",
    ], y=0.088)
    return fig
