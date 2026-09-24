import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import geometry as G
from sheet04_groundfloor import ROOMS_A, ROOMS_B, EXT

def fan_symbol(ax, x, y, r=0.5):
    ax.add_patch(mpatches.Circle((x, y), r, facecolor='none', edgecolor='black', lw=0.9))
    ax.plot([x-r, x+r], [y, y], color='black', lw=0.6)
    ax.plot([x, x], [y-r, y+r], color='black', lw=0.6)

def light_symbol(ax, x, y, r=0.28):
    ax.add_patch(mpatches.Circle((x, y), r, facecolor='black', edgecolor='black', lw=0.6))

def socket_symbol(ax, x, y, s=0.35):
    ax.add_patch(mpatches.Rectangle((x-s/2, y-s/2), s, s, facecolor='none', edgecolor='black', lw=0.8))

def db_symbol(ax, x, y, s=0.7, label="DB"):
    ax.add_patch(mpatches.Rectangle((x-s/2, y-s/2), s, s, facecolor='0.3', edgecolor='black', lw=1.2))
    ax.text(x, y-s/2-0.35, label, fontsize=6.0, ha='center', family='monospace')

def wire(ax, pts):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    ax.plot(xs, ys, color='black', lw=0.5, linestyle=(0, (4, 2)))

def make():
    fig, ax = new_sheet("11", "ELECTRICAL LAYOUT PLAN (GROUND FLOOR, TYPICAL)", "1:75", "E-001")

    wall_band(ax, 0, 0, 28, 0, EXT); wall_band(ax, 0, 0, 0, 38, EXT)
    wall_band(ax, 28, 0, 28, 38, EXT); wall_band(ax, 0, 38, 28, 38, EXT)
    for name, (x, y, w, h) in {**ROOMS_A, **ROOMS_B}.items():
        ax.add_patch(mpatches.Rectangle((x, y), w, h, facecolor='none', edgecolor='0.6', lw=0.9))
    for rooms, db_x, db_y in ((ROOMS_A, 9.5, 1.0), (ROOMS_B, 9.5, 37.0)):
        r = rooms
        # Living: fan, light, TV point, sockets
        liv = r["LIVING"]
        fan_symbol(ax, liv[0]+liv[2]/2, liv[1]+liv[3]*0.55)
        light_symbol(ax, liv[0]+liv[2]/2, liv[1]+liv[3]*0.85)
        light_symbol(ax, liv[0]+liv[2]/2, liv[1]+liv[3]*0.2)
        socket_symbol(ax, liv[0]+0.6, liv[1]+liv[3]*0.15)
        ax.text(liv[0]+0.6, liv[1]+liv[3]*0.15-0.6, "TV\nPT", fontsize=5.0, ha='center', family='monospace')
        socket_symbol(ax, liv[0]+liv[2]-0.6, liv[1]+liv[3]*0.5)
        # Kitchen: exhaust, chimney, fridge point, RO point
        kit = r["KITCHEN"]
        light_symbol(ax, kit[0]+kit[2]/2, kit[1]+kit[3]/2)
        socket_symbol(ax, kit[0]+kit[2]-0.6, kit[1]+1.0)
        ax.text(kit[0]+kit[2]-0.6, kit[1]+0.4, "FRIDGE", fontsize=4.8, ha='center', family='monospace')
        socket_symbol(ax, kit[0]+kit[2]-0.6, kit[1]+kit[3]-1.0)
        ax.text(kit[0]+kit[2]-0.6, kit[1]+kit[3]-0.4, "RO PT", fontsize=4.8, ha='center', family='monospace')
        ax.add_patch(mpatches.Rectangle((kit[0]+0.4, kit[1]+kit[3]-1.2), 0.9, 0.5, facecolor='none', edgecolor='black', lw=0.7))
        ax.text(kit[0]+0.85, kit[1]+kit[3]-1.9, "EXHAUST +\nCHIMNEY PT", fontsize=4.6, ha='center', family='monospace')
        # Bedroom: fan, light, AC point, switchboard
        bed = r["BEDROOM"]
        fan_symbol(ax, bed[0]+bed[2]/2, bed[1]+bed[3]*0.5)
        light_symbol(ax, bed[0]+bed[2]/2, bed[1]+bed[3]*0.8)
        ax.add_patch(mpatches.Rectangle((bed[0]+bed[2]-1.0, bed[1]+bed[3]-0.8), 0.8, 0.5, facecolor='none', edgecolor='black', lw=0.7))
        ax.text(bed[0]+bed[2]-0.6, bed[1]+bed[3]-1.4, "AC PT", fontsize=4.8, ha='center', family='monospace')
        socket_symbol(ax, bed[0]+0.6, bed[1]+0.6)
        ax.text(bed[0]+1.5, bed[1]+0.6, "SB", fontsize=4.8, family='monospace')
        # Shower/WC: exhaust, geyser, light
        for key in ("SHOWER", "WC"):
            rr = r[key]
            light_symbol(ax, rr[0]+rr[2]/2, rr[1]+rr[3]/2)
        sh = r["SHOWER"]
        ax.add_patch(mpatches.Rectangle((sh[0]+0.3, sh[1]+sh[3]-0.7), 0.7, 0.4, facecolor='none', edgecolor='black', lw=0.6))
        ax.text(sh[0]+0.65, sh[1]+sh[3]-1.15, "GEYSER +\nEXHAUST", fontsize=4.2, ha='center', family='monospace')

        db_symbol(ax, db_x, db_y, label="DB (MCB)")
        for target in (liv, kit, bed, r["SHOWER"], r["WC"]):
            wire(ax, [(db_x, db_y), (target[0]+target[2]/2, target[1]+target[3]/2)])

    ax.plot([], [], marker='o', color='black', markerfacecolor='none', linestyle='None', markersize=9, label='Ceiling fan')
    ax.plot([], [], marker='o', color='black', markerfacecolor='black', linestyle='None', markersize=6, label='Light point')
    ax.plot([], [], marker='s', color='black', markerfacecolor='none', linestyle='None', markersize=7, label='Socket / plug point')
    ax.plot([], [], marker='s', color='black', markerfacecolor='0.3', linestyle='None', markersize=9, label='Distribution board (DB)')
    ax.legend(loc='lower left', bbox_to_anchor=(1.02, 0.0), fontsize=7.5, frameon=True)

    north_arrow(fig, 0.90, 0.90)
    scale_bar_ft(ax, -6, 20, unit=5, n=4)
    set_view(ax, -9, 32, -8, 42)

    notes_block(fig, [
        "One MCB distribution board (DB) per unit, located near the entry (Unit 1 near south wall, Unit 2 near north wall); first-floor DB(s) similarly near the common lobby.",
        "Living Room: ceiling fan, 2 light points, dedicated TV point with sockets, and general-purpose 6A/16A socket outlets as shown.",
        "Kitchen: light point, exhaust fan + chimney point above the hob, dedicated 16A points for fridge and RO/water purifier.",
        "Bedroom: ceiling fan, light point, dedicated 16A AC point (with separate MCB), and a switchboard with general sockets.",
        "Shower/WC: light point (moisture-proof fitting), exhaust fan, and a dedicated point for an instant/storage geyser.",
        "Wiring routes shown schematically (concealed conduit, radial from DB); final circuit design, wire gauge and MCB rating per electrical consultant/IS 732.",
        "Provide earthing per IS 3043 and ELCB/RCCB protection at each DB.",
    ], y=0.088)
    return fig
