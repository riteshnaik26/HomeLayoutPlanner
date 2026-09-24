import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import geometry as G
from sheet12_sections import (LVL_GF_FFL, LVL_FF_FFL, LVL_TERRACE_FFL, LVL_PARAPET_TOP,
                               LVL_MUMTY_TOP, LVL_FOOTING_BOT)

def level_line(ax, x0, x1, y, label):
    ax.plot([x0, x1], [y, y], color='black', lw=0.5, linestyle=(0, (6, 2)))
    ax.text(x1 + 0.6, y, f"EL {label}", fontsize=6.4, va='center', family='monospace')

def facade(ax, x0, width, n_win_gf, n_win_ff, door_x=None, canopy=False, mumty_x=None):
    x1 = x0 + width
    ax.add_patch(mpatches.Rectangle((x0, 0), width, LVL_TERRACE_FFL - 0, facecolor='0.97', edgecolor='black', lw=1.6))
    ax.plot([x0, x1], [LVL_GF_FFL, LVL_GF_FFL], color='black', lw=0.6)
    ax.plot([x0, x1], [LVL_FF_FFL, LVL_FF_FFL], color='black', lw=0.6)
    ax.plot([x0-0.6, x1+0.6], [0, 0], color='black', lw=1.2)
    ax.add_patch(mpatches.Rectangle((x0, LVL_TERRACE_FFL), width, LVL_PARAPET_TOP-LVL_TERRACE_FFL,
                                     facecolor='0.9', edgecolor='black', lw=1.3))
    if mumty_x:
        mx0, mw = mumty_x
        ax.add_patch(mpatches.Rectangle((mx0, LVL_PARAPET_TOP), mw, LVL_MUMTY_TOP-LVL_PARAPET_TOP,
                                         facecolor='0.85', edgecolor='black', lw=1.2))
        ax.add_patch(mpatches.Rectangle((mx0+mw*0.3, LVL_PARAPET_TOP+0.5), mw*0.4, 2.0, facecolor='white', edgecolor='black', lw=0.8))

    def windows_row(y_sill, n):
        seg = width / (n + 1)
        for i in range(n):
            wx = x0 + seg*(i+1) - 1.5
            ax.add_patch(mpatches.Rectangle((wx, y_sill), 3.0, 3.5, facecolor='white', edgecolor='black', lw=1.0))
            for k in (1, 2):
                ax.plot([wx, wx+3.0], [y_sill+3.5*k/3, y_sill+3.5*k/3], color='black', lw=0.4)
            ax.plot([wx+1.5, wx+1.5], [y_sill, y_sill+3.5], color='black', lw=0.4)

    windows_row(LVL_GF_FFL + 2.5, n_win_gf)
    windows_row(LVL_FF_FFL + 2.5, n_win_ff)

    if door_x is not None:
        dx = door_x
        ax.add_patch(mpatches.Rectangle((dx-1.5, 0), 3.0, 7.0, facecolor='0.75', edgecolor='black', lw=1.2))
        ax.plot([dx-1.5, dx+1.5], [3.5, 3.5], color='black', lw=0.4)
        if canopy:
            ax.add_patch(mpatches.Polygon([(dx-3.0, 7.4), (dx+3.0, 7.4), (dx+2.4, 8.2), (dx-2.4, 8.2)],
                                           closed=True, facecolor='0.8', edgecolor='black', lw=1.0))
            for cxp in (dx-3.0, dx, dx+3.0):
                ax.plot([cxp, cxp], [0, 7.4], color='black', lw=0.8, linestyle=':')

    for gx in np.linspace(x0-3, x1+3, 24):
        ax.plot([gx, gx-0.3], [-0.15, -0.5], color='black', lw=0.35)
    ax.plot([x0-3, x1+3], [-0.15, -0.15], color='black', lw=1.0)
