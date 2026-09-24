import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import geometry as G

FT_TO_M = 0.3048
R = G.REBAR
WT = G.BAR_WT


def bar_len_wt(dia, count, length_m):
    """Return (total length m, total weight kg) for `count` bars of `dia` mm, each `length_m` long."""
    L = count * length_m
    return L, L * WT[dia]


def compute():
    rows = []  # (member, qty_desc, bar_note, total_len_m, weight_kg)

    # ---- Footings: 18 No., mixed sizes -- 9 full 6'x6', 7 half (6'x3' or 3'x6', boundary
    #      columns), 2 corner 3'x3' (P1, P5) -- see G.FOOT_TRIM / G.footing_extents() ----
    dia = R["footing"]["bottom_bar"]
    spacing = R["footing"]["bottom_spacing"]
    n_bars_total = 0
    len_total_m = 0.0
    n_full = n_half = n_corner = 0
    for name in G.COLS:
        if name in G.FOOT_TRIM:
            fx0, fx1, fy0, fy1 = G.footing_extents(name)
            fw_ft, fh_ft = fx1 - fx0, fy1 - fy0
            if fw_ft < G.FOOT_SIZE_FULL and fh_ft < G.FOOT_SIZE_FULL:
                n_corner += 1
            else:
                n_half += 1
        else:
            fw_ft, fh_ft = G.FOOT_SIZE_FULL, G.FOOT_SIZE_FULL
            n_full += 1
        fw_m, fh_m = fw_ft * FT_TO_M, fh_ft * FT_TO_M
        bars_along_y = int(fw_m * 1000 / spacing) + 1   # bars running N-S, spaced across the width (fw)
        bars_along_x = int(fh_m * 1000 / spacing) + 1   # bars running E-W, spaced across the depth (fh)
        n_bars_total += bars_along_y + bars_along_x
        len_total_m += bars_along_y * (fh_m - 0.1) + bars_along_x * (fw_m - 0.1)  # minus ~50mm cover each end
    Wt = len_total_m * WT[dia]
    rows.append((f"Footings (18 No.: {n_full} full, {n_half} half, {n_corner} corner)",
                  f"{n_bars_total} bars, mixed lengths, {len_total_m:.0f}m total",
                  f"{dia}mm dia", len_total_m, Wt))

    # ---- Pedestals: 18 No., 2'x2', height ~3'-0" (footing top to plinth) ----
    ped_h = 3.0 * FT_TO_M
    L1, Wt1 = bar_len_wt(R["pedestal"]["main_bar"], R["pedestal"]["main_count"] * 18, ped_h + 0.3)
    ped_perim = 2 * (2.0 + 2.0) * FT_TO_M - 0.2
    n_ties = int(ped_h * 1000 / R["pedestal"]["tie_spacing"]) + 1
    L2, Wt2 = bar_len_wt(R["pedestal"]["tie_bar"], n_ties * 18, ped_perim)
    rows.append(("Pedestals (18 No.)", f"main {R['pedestal']['main_count']}x{18} + ties {n_ties}x{18}",
                  f"{R['pedestal']['main_bar']}mm main / {R['pedestal']['tie_bar']}mm ties", L1+L2, Wt1+Wt2))

    # ---- Columns: 18 No., 12"x15", height = 2 x floor-to-floor ----
    col_h = 2 * G.FLOOR_TO_FLOOR * FT_TO_M
    lap = 0.8  # one splice per column, ~50d for 16mm
    L1, Wt1 = bar_len_wt(R["column"]["main_bar"], R["column"]["main_count"] * 18, col_h + lap)
    col_perim = 2 * (12 + 15) * 0.0254 - 0.15
    n_ties = int(col_h * 1000 / R["column"]["tie_spacing"]) + 1
    L2, Wt2 = bar_len_wt(R["column"]["tie_bar"], n_ties * 18, col_perim)
    rows.append(("Columns (18 No., P1-P18)", f"main {R['column']['main_count']}x18, ties {n_ties}x18, ht {col_h:.1f}m",
                  f"{R['column']['main_bar']}mm main / {R['column']['tie_bar']}mm ties", L1+L2, Wt1+Wt2))

    # ---- Main beams: grid lines both directions, 2 levels (FF + Terrace) ----
    x_line_len = G.BD  # ft, one grid line's length (N-S)
    y_line_len = G.BW  # ft, one grid line's length (E-W)
    n_x_lines = 3       # GX_WEST, GX_MID, GX_EAST
    n_y_lines = 4        # GY has 4 rows
    canopy_len = G.GY_CANOPY[-1]
    connector_len = (G.GX_CANOPY - G.GX_EAST) * 2  # two short connectors to the canopy line
    total_ft_per_level = n_x_lines*x_line_len + n_y_lines*y_line_len + canopy_len + connector_len
    total_m = total_ft_per_level * FT_TO_M * 2  # x2 levels
    n_bars = R["main_beam"]["top_count"] + R["main_beam"]["bottom_count"]
    L1 = n_bars * total_m
    Wt1 = L1 * WT[R["main_beam"]["top_bar"]]
    beam_perim = 2*(9+18)*0.0254 - 0.1
    n_stirrups = int(total_m*1000 / R["main_beam"]["stirrup_spacing"])
    L2, Wt2 = bar_len_wt(R["main_beam"]["stirrup_bar"], n_stirrups, beam_perim)
    rows.append(("Main beams (9\"x18\"), 2 levels", f"{total_ft_per_level:.0f} ft/level x 2 levels = {total_m:.0f}m run",
                  f"{R['main_beam']['top_bar']}mm long. / {R['main_beam']['stirrup_bar']}mm stirrups", L1+L2, Wt1+Wt2))

    # ---- Secondary beams: mid-corridor partition + cantilever (P9-P10-P5), 2 levels ----
    partition_len = G.BW
    p9, p10, p5 = G.COLS["P9"], G.COLS["P10"], G.COLS["P5"]
    cant_len = (abs(p10[1]-p9[1]) + abs(p5[0]-p10[0]))
    total_ft = (partition_len + cant_len) * 2  # x2 levels
    total_m = total_ft * FT_TO_M
    n_bars = R["secondary_beam"]["top_count"] + R["secondary_beam"]["bottom_count"]
    L1 = n_bars * total_m
    Wt1 = L1 * WT[R["secondary_beam"]["top_bar"]]
    sb_perim = 2*(9+12)*0.0254 - 0.1
    n_stirrups = int(total_m*1000 / R["secondary_beam"]["stirrup_spacing"])
    L2, Wt2 = bar_len_wt(R["secondary_beam"]["stirrup_bar"], n_stirrups, sb_perim)
    rows.append(("Secondary beams, 2 levels", f"{total_ft:.0f} ft run = {total_m:.0f}m",
                  f"{R['secondary_beam']['top_bar']}mm long. / {R['secondary_beam']['stirrup_bar']}mm stirrups", L1+L2, Wt1+Wt2))

    # ---- Plinth/tie beams: same grid as main beams, 1 level (foundation) ----
    total_ft = n_x_lines*x_line_len + n_y_lines*y_line_len
    total_m = total_ft * FT_TO_M
    n_bars = R["plinth_beam"]["top_count"] + R["plinth_beam"]["bottom_count"]
    L1 = n_bars * total_m
    Wt1 = L1 * WT[R["plinth_beam"]["top_bar"]]
    n_stirrups = int(total_m*1000 / R["plinth_beam"]["stirrup_spacing"])
    L2, Wt2 = bar_len_wt(R["plinth_beam"]["stirrup_bar"], n_stirrups, sb_perim)
    rows.append(("Plinth/tie beams, 1 level", f"{total_ft:.0f} ft run = {total_m:.0f}m",
                  f"{R['plinth_beam']['top_bar']}mm long. / {R['plinth_beam']['stirrup_bar']}mm stirrups", L1+L2, Wt1+Wt2))

    # ---- Slabs: main 28x38 + gallery extensions, 2 levels (FF + Terrace) ----
    main_area = G.BW * G.BD
    gallery_area = (G.FF_GALLERY_X1_CANTILEVER - G.FF_GALLERY_X0) * (G.FF_GALLERY_NORTH_EXT - 38)
    total_sqft = (main_area) * 2  # main slab both levels (gallery already within BW for most of it; extension small)
    total_sqft += gallery_area  # north extension corner, terrace level only (approx)
    area_m2 = total_sqft * FT_TO_M**2
    kg_per_m2 = 3.75  # thumb-rule average for a 5-6in two-way slab incl. main+dist+top steel
    Wt = area_m2 * kg_per_m2
    rows.append(("Slabs (FF + Terrace, incl. gallery)", f"{total_sqft:.0f} sqft = {area_m2:.0f} m² @ {kg_per_m2}kg/m²",
                  f"{R['slab']['main_bar']}mm/{R['slab']['dist_bar']}mm (see S-004A)", None, Wt))

    # ---- Staircase waist slab: 2 flights (GF-FF, FF-Terrace) ----
    stair_area_sqft = (G.STAIR_X[1]-G.STAIR_X[0]) * (G.STAIR_Y[1]-G.STAIR_Y[0]) * 2 * 0.75  # x2 flights, x0.75 (inclined vs plan area factor)
    area_m2 = stair_area_sqft * FT_TO_M**2
    kg_per_m2 = 5.0
    Wt = area_m2 * kg_per_m2
    rows.append(("Staircase waist slab, 2 flights", f"{stair_area_sqft:.0f} sqft = {area_m2:.0f} m² @ {kg_per_m2}kg/m²",
                  f"{R['stair_waist']['main_bar']}mm/{R['stair_waist']['dist_bar']}mm (see S-004A)", None, Wt))

    return rows


def make():
    fig, ax = new_sheet("08B", "STEEL QUANTITY ESTIMATE (PRELIMINARY BBS SUMMARY)", "N/A (table)", "S-004B")
    ax.axis('off')
    ax.set_aspect('auto')
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)

    rows = compute()
    grand_total_kg = sum(r[4] for r in rows)

    ax.text(5, 9.5, "PRELIMINARY STEEL QUANTITY ESTIMATE", fontsize=18, fontweight='bold', ha='center', family='monospace')
    ax.text(5, 9.1, "(thumb-rule quantities for budgeting/coordination -- NOT a substitute for a structural engineer's BBS)",
            fontsize=12, ha='center', family='monospace', style='italic')

    col_x = [0.3, 3.5, 6.5, 8.6]
    headers = ["MEMBER", "QUANTITY / BASIS", "BAR SIZE(S)", "WEIGHT (kg)"]
    y = 8.6
    for cx, h in zip(col_x, headers):
        ax.text(cx, y, h, fontsize=12, fontweight='bold', family='monospace')
    y -= 0.18
    ax.plot([0.2, 9.8], [y, y], color='black', lw=0.8)
    y -= 0.28

    for member, basis, bar_note, _len, wt in rows:
        ax.text(col_x[0], y, member, fontsize=12, family='monospace')
        ax.text(col_x[1], y, basis, fontsize=12, family='monospace')
        ax.text(col_x[2], y, bar_note, fontsize=12, family='monospace')
        ax.text(col_x[3], y, f"{wt:,.0f}", fontsize=12, family='monospace')
        y -= 0.34

    y -= 0.1
    ax.plot([0.2, 9.8], [y, y], color='black', lw=0.8)
    y -= 0.32
    ax.text(col_x[0], y, "GRAND TOTAL", fontsize=12, fontweight='bold', family='monospace')
    ax.text(col_x[3], y, f"{grand_total_kg:,.0f} kg", fontsize=12, fontweight='bold', family='monospace')
    y -= 0.3
    ax.text(col_x[0], y, "", fontsize=12, family='monospace')
    ax.text(col_x[3], y, f"≈ {grand_total_kg/1000:.2f} tonnes", fontsize=12, family='monospace')

    y -= 0.55
    built_up_sqft = G.GROUND_COVERAGE * 2  # GF + FF, roughly (excl. gallery/terrace extras, for a simple ratio check)
    ratio = grand_total_kg / built_up_sqft
    ax.text(0.3, y, f"Cross-check: {grand_total_kg:,.0f} kg / ~{built_up_sqft:.0f} sqft built-up (GF+FF) "
            f"≈ {ratio:.2f} kg/sqft", fontsize=12, family='monospace')
    y -= 0.26
    ax.text(0.3, y, "Typical Indian practice for a G+1 RCC-framed residence: 3.5-4.5 kg/sqft including footing, "
            "column, beam & slab steel.", fontsize=12, family='monospace')
    y -= 0.24
    ax.text(0.3, y, "This estimate runs somewhat below that range because it uses minimum/typical bar counts and "
            "spacings appropriate to a light, low-rise structure on ROCKY soil (as assumed) -- a structural", fontsize=12, family='monospace')
    y -= 0.20
    ax.text(0.3, y, "engineer's actual design, once wind/seismic zone and real loads are checked, commonly lands "
            "within or somewhat above the typical range. Budget with a margin.", fontsize=12, family='monospace')

    notes_block(fig, [
        f"Steel grade {G.FE_GRADE}, concrete grade {G.CONCRETE_GRADE} (assumed). Unit weights per IS 1786: w(kg/m) = dia²(mm)/162.",
        "Quantities are derived directly from this drawing set's own grid/geometry (column count & height, beam/slab lengths & areas, footing/stair sizes) using the typical bar sizes and spacings shown on Sheet S-004A.",
        "EXCLUDED: laps/development length beyond the single splice/joint per member, wastage (add 3-5%), chairs/spacers, and extra steel for the terrace mumty/parapet or the cantilever (once finalised, it will likely need more top steel than this allows).",
        "This is a PRELIMINARY quantity for budgeting and material planning only. The actual bar bending schedule (BBS), covering every individual bar's exact cut length, bend points and count, must be produced by the structural engineer from a full structural \n analysis before ordering steel or starting construction.",
    ], y=0.088)
    return fig
