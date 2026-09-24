import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import geometry as G
import numpy as np

# REVISION 8: staircase is EXTERNAL (open/covered), in the bike-parking
# zone between columns P2 and P3 -- the original 14' bay. Run is along y
# (G.STAIR_Y, 14' -- the P2-P3 bay); width is along x (G.STAIR_X, 3' --
# within the 8' bike-parking strip, flush with the canopy line). At only
# 3' wide there is no room for two side-by-side flights (the old 6'-wide
# dog-leg); this is now a SINGLE-LANE half-turn stair -- flight 2 shares
# the same 3' footprint as flight 1, running directly above it (shown
# dashed in plan, per the break-line convention below).

RISER = 7.0/12.0     # 7"
TREAD = 10.0/12.0    # 10"
N_RISERS_PER_FLIGHT = 9
N_TREADS_PER_FLIGHT = 8
FLIGHT_RUN = N_TREADS_PER_FLIGHT * TREAD   # 6'-8"
LANDING = 5.0
LOBBY = (G.STAIR_Y[1] - G.STAIR_Y[0]) - LANDING - FLIGHT_RUN  # remaining depth

FLW = G.STAIR_X[1] - G.STAIR_X[0]  # flight width, 3'-0" -- single shared lane


def draw_treads(ax, x0, w, y0, n, up=True):
    for i in range(n):
        yy = y0 + i * TREAD if up else y0 - i * TREAD
        ax.plot([x0, x0 + w], [yy, yy], color='black', lw=0.6)

def make():
    fig, ax = new_sheet("09", "STAIRCASE PLAN & SECTION (COMMON DOG-LEG STAIR - EXTERNAL)", "1:50", "A-005")

    x0, x1 = G.STAIR_X   # 30, 36 -- width direction
    y0, y1 = G.STAIR_Y   # 12, 26 -- run direction
    lobby_y1 = y0 + LOBBY
    f1_y0, f1_y1 = lobby_y1, lobby_y1 + FLIGHT_RUN
    land_y0, land_y1 = f1_y1, f1_y1 + LANDING

    ax.add_patch(mpatches.Rectangle((x0, y0), x1-x0, y1-y0, facecolor='none', edgecolor='black', lw=1.8))
    ax.plot([28, x0], [(y0+y1)/2, (y0+y1)/2], color='0.4', lw=1.0, linestyle=':')
    ax.text(25.5, (y0+y1)/2+0.6, "MAIN BUILDING\nEAST WALL", fontsize=5.6, ha='center', family='monospace')
    ax.plot([x1, x1+3], [(y0+y1)/2, (y0+y1)/2], color='0.4', lw=0.8, linestyle=':')
    ax.text(x1+3.5, (y0+y1)/2, "canopy\nline (P2/P3)", fontsize=5.2, va='center', family='monospace')

    # entry lobby (ground level, open from bike parking)
    ax.add_patch(mpatches.Rectangle((x0, y0), x1-x0, LOBBY, facecolor='0.95', edgecolor='black', lw=1.0))
    ax.text((x0+x1)/2, (y0+lobby_y1)/2, f"ENTRY\n{LOBBY:.1f}'", fontsize=6.0, ha='center', va='center', family='monospace')
    ax.text((x0+x1)/2, y0-0.9, "GROUND LEVEL - OPEN ENTRY FROM BIKE PARKING", fontsize=5.6, ha='center', family='monospace')

    # Flight 1 (up)
    ax.add_patch(mpatches.Rectangle((x0, f1_y0), FLW, FLIGHT_RUN, facecolor='none', edgecolor='black', lw=1.2))
    draw_treads(ax, x0, FLW, f1_y0, N_TREADS_PER_FLIGHT, up=True)
    ax.annotate('', xy=(x0+FLW/2, f1_y1-0.3), xytext=(x0+FLW/2, f1_y0+0.3),
                arrowprops=dict(arrowstyle='-|>', lw=1.3, color='black'))
    ax.text(x0+FLW/2, (f1_y0+f1_y1)/2, "UP", fontsize=8, ha='center', rotation=90, fontweight='bold', family='monospace')

    # Landing
    ax.add_patch(mpatches.Rectangle((x0, land_y0), x1-x0, LANDING, facecolor='0.88', edgecolor='black', lw=1.2))
    ax.text((x0+x1)/2, (land_y0+land_y1)/2, f"LANDING  {LANDING:.0f}'-0\" (MIN)", fontsize=6.6, ha='center', va='center', family='monospace')

    # Flight 2: REVISION 8 -- at only 3' wide there is no second lane beside
    # Flight 1, so Flight 2 climbs back over the SAME footprint, one level
    # higher (a single-lane half-turn/scissor stair) -- Flight 1's box above
    # ALSO represents Flight 2's plan position, cut by the break line below;
    # see the SECTION for its full vertical continuation.
    by = (f1_y0 + f1_y1)/2 + 0.3
    zig = [(x0, by-0.12), (x0+FLW*0.33, by+0.12), (x0+FLW*0.66, by-0.12), (x0+FLW, by+0.12)]
    ax.plot([p[0] for p in zig], [p[1] for p in zig], color='black', lw=1.0)
    ax.text(x1+5.2, by, "BREAK LINE -\nFLIGHT 2 CONTINUES\nABOVE HEAD HEIGHT,\nSAME 3' LANE AS\nFLIGHT 1 BELOW", fontsize=5.2, va='center', family='monospace')

    dim_v(ax, y0, y1, x1+2.4, text=f"{y1-y0:.0f}'-0\" RUN (P2-P3 BAY)", fontsize=6.4)
    dim_h(ax, x0, x1, y0-1.6, text="3'-0\" WIDTH (SINGLE FLIGHT, HALF-TURN)", fontsize=6.4)
    dim_v(ax, f1_y0, f1_y1, x0-1.0, text=f"FLIGHT RUN {ft_in(FLIGHT_RUN)}", fontsize=6.0, right=False)

    scale_bar_ft(ax, x0-5, y0-5.5, unit=5, n=3)

    # ---- SECTION (offset below/right) ----
    sx0 = x1 + 20
    sy0 = 0
    slab_t = 5.0/12.0

    def draw_flight_section(ax, xstart, ystart, nrisers, ntreads, direction=1):
        pts_x, pts_y = [xstart], [ystart]
        x, y = xstart, ystart
        for i in range(nrisers):
            y += RISER
            pts_x.append(x); pts_y.append(y)
            if i < ntreads:
                x += direction * TREAD
                pts_x.append(x); pts_y.append(y)
        ax.plot(pts_x, pts_y, color='black', lw=1.6)
        return x, y

    ax.add_patch(mpatches.Rectangle((sx0-1.5, sy0-slab_t), FLIGHT_RUN+LANDING+3, slab_t,
                                     facecolor='0.7', edgecolor='black', lw=1.0, hatch='///'))
    ax.text(sx0-0.5, sy0-slab_t-0.6, "GROUND LEVEL / FFL ±0'-0\"", fontsize=6.4, family='monospace')

    xe, ye = draw_flight_section(ax, sx0, sy0, N_RISERS_PER_FLIGHT, N_TREADS_PER_FLIGHT, direction=1)
    ax.add_patch(mpatches.Rectangle((xe-0.3, ye), LANDING, slab_t, facecolor='0.7', edgecolor='black', lw=1.0, hatch='///'))
    ax.text(xe+LANDING/2-0.3, ye+0.7, f"LANDING\nRL +{ye-sy0:.2f}'", fontsize=6.0, ha='center', family='monospace')
    xe2, ye2 = draw_flight_section(ax, xe+LANDING, ye+slab_t, N_RISERS_PER_FLIGHT, N_TREADS_PER_FLIGHT, direction=-1)

    ax.add_patch(mpatches.Rectangle((xe2-FLIGHT_RUN-1.5, ye2), FLIGHT_RUN+3, slab_t, facecolor='0.7',
                                     edgecolor='black', lw=1.0, hatch='///'))
    ax.text(xe2-2.0, ye2+0.7, f"1ST FLOOR GALLERY / FFL +{ye2-sy0:.2f}' ≈ +10'-6\"", fontsize=6.4, family='monospace')

    dim_v(ax, sy0, ye2, sx0-2.4, text=f"FLOOR TO FLOOR = {G.FLOOR_TO_FLOOR:.1f}'-0\"", fontsize=6.6, right=False)
    ax.text(sx0+2, sy0-3.2, f"18 RISERS @ 7\" = {18*RISER:.2f}'\n16 TREADS @ 10\"\nLANDING 5'-0\" MIN\nFLIGHT WIDTH 3'-0\" (SINGLE, SHARED LANE)",
            fontsize=6.6, family='monospace', va='top')
    ax.text(sx0+3, ye2+2.0, "OPEN/COVERED HEADROOM HOOD\nCONTINUES SIMILARLY\n1ST FLOOR → TERRACE\n(min 7'-0\" headroom)",
            fontsize=6.2, family='monospace')

    ax.text(sx0+FLIGHT_RUN/2, ye2+3.8, "SECTION THROUGH STAIRCASE (SCHEMATIC)", fontsize=8, fontweight='bold',
            ha='center', family='monospace')

    north_arrow(fig, 0.92, 0.90)
    set_view(ax, 20, sx0+FLIGHT_RUN+LANDING+8, sy0-8, y1+7)

    notes_block(fig, [
        "REVISION 5: Common staircase is EXTERNAL (open, or covered by an extension of the bike-parking canopy), sited between columns P2 and P3, the original 14' bay -- exactly as marked up by the client.",
        "REVISION 8: Single-lane half-turn (scissor) stair, 3'-0\" wide overall (was 6'-0\", 2 flights side by side), connected by a 5'-0\" half-space landing; Flight 2 climbs back over Flight 1's footprint, one level higher.",
        "Flight run + landing = 11'-8\"; the remaining 2'-4\" of the 14' bay is a small ground-level entry lobby, open to the bike parking.",
        "18 risers @ 7\" and 16 treads @ 10\" for the 10'-6\" floor-to-floor height (Ground to First Floor); the same scheme repeats First Floor to Terrace.",
        "Minimum headroom 7'-0\" maintained throughout the flight and at the landing; provide a light roof/canopy extension (tying into the P1-P5 canopy) over the stair for weather protection.",
        "Provide a 3'-6\" high handrail on the open side(s) of the flight and around the landing/lobby edge, plus a lockable gate at the ground-level entry for security.",
        "Being external, final position, guarding and the waist-slab/foundation design must be verified on site and by the structural engineer -- shown here schematically.",
    ], y=0.088)
    return fig
