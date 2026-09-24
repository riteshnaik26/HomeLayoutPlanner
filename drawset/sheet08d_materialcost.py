import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import geometry as G
import sheet08c_steelqty as steelqty

FT_TO_M = 0.3048
FT3_TO_M3 = 1.0 / 35.3147

# ---- Indicative material rates (INR) -- see disclaimer on the sheet ----
RATES = {
    "steel": 62.0,        # Rs/kg, Fe500 TMT
    "cement": 400.0,       # Rs/50kg bag
    "sand": 2200.0,         # Rs/cum
    "aggregate": 1600.0,     # Rs/cum (20mm crushed stone / khadi)
    "brick": 8.0,             # Rs/each
    "wire": 75.0,              # Rs/kg, binding wire
}

OPENING_DEDUCT = 0.12   # doors/windows deduction from gross wall/plaster area, thumb-rule

# ---- Labour rates (client-supplied, 2026-09) -- see disclaimer on the sheet ----
RCC_LABOUR_RATE = 220.0        # Rs/sqft of RCC (slab) area -- shuttering+steel-fixing+concreting labour
GENERAL_LABOUR_RATE = 1100.0    # Rs/labour-day (crew of mason+helper)
BRICKWORK_PRODUCTIVITY = 1.0      # cum/labour-day (mason+helper crew, CPWD-type norm)
PLASTER_PRODUCTIVITY = 16.0        # sqm/labour-day (mason+helper crew, 12mm single coat)

# Material-transformation / slab-filling crew (client-supplied, 2026-09):
# 4 labour @ Rs1100/day (skilled) + 4 labour @ Rs400/day (unskilled), deployed
# on RCC concreting days (material handling + placing/filling). Separate from
# (additional to) the RCC labour and general labour lines above.
MT_CREW_SKILLED, MT_CREW_SKILLED_RATE = 4, 1100.0
MT_CREW_UNSKILLED, MT_CREW_UNSKILLED_RATE = 4, 400.0
MT_CREW_DAY_RATE = MT_CREW_SKILLED*MT_CREW_SKILLED_RATE + MT_CREW_UNSKILLED*MT_CREW_UNSKILLED_RATE   # Rs6000/day
MT_PRODUCTIVITY = 4.0   # cum/day RCC concrete placed by this 8-person crew, thumb-rule


def compute():
    """Returns (material_rows, labour_rows, basis).
    material_rows/labour_rows: list of (item, qty, unit, rate, cost)."""

    # ---- RCC concrete volume (reuses the same geometry as Sheet S-004B) ----
    foot_area_total = 0.0
    for name in G.COLS:
        if name in G.FOOT_TRIM:
            x0, x1, y0, y1 = G.footing_extents(name)
            foot_area_total += (x1 - x0) * (y1 - y0)
        else:
            foot_area_total += G.FOOT_SIZE_FULL ** 2
    foot_vol = foot_area_total * 1.5   # 18in thick

    ped_vol = 18 * 2 * 2 * 3
    col_h = 2 * G.FLOOR_TO_FLOOR
    col_vol = 18 * 1.0 * 1.25 * col_h

    x_line_len, y_line_len = G.BD, G.BW
    n_x_lines, n_y_lines = 3, 4
    canopy_len = G.GY_CANOPY[-1]
    connector_len = (G.GX_CANOPY - G.GX_EAST) * 2
    total_ft_per_level = n_x_lines * x_line_len + n_y_lines * y_line_len + canopy_len + connector_len
    main_beam_vol = (total_ft_per_level * 2) * 0.75 * 1.5

    p9, p10, p5 = G.COLS["P9"], G.COLS["P10"], G.COLS["P5"]
    cant_len = abs(p10[1] - p9[1]) + abs(p5[0] - p10[0])
    sec_total_ft = (G.BW + cant_len) * 2
    sec_vol = sec_total_ft * 0.75 * 1.0

    plinth_total_ft = n_x_lines * x_line_len + n_y_lines * y_line_len
    plinth_vol = plinth_total_ft * 0.75 * 1.0

    main_area = G.BW * G.BD
    gallery_area = (G.FF_GALLERY_X1_CANTILEVER - G.FF_GALLERY_X0) * (G.FF_GALLERY_NORTH_EXT - 38)
    slab_area_sqft = main_area * 2 + gallery_area
    slab_vol = slab_area_sqft * (5.5 / 12)

    stair_area_sqft = (G.STAIR_X[1] - G.STAIR_X[0]) * (G.STAIR_Y[1] - G.STAIR_Y[0]) * 2 * 0.75
    stair_vol = stair_area_sqft * (5.0 / 12)

    rcc_cuft = foot_vol + ped_vol + col_vol + main_beam_vol + sec_vol + plinth_vol + slab_vol + stair_vol
    rcc_cum = rcc_cuft * FT3_TO_M3

    # ---- Brickwork volume (external + common + internal walls, both floors, + parapet) ----
    F2F = G.FLOOR_TO_FLOOR
    gf_ext_len = 28 + 38 + 38 + 28
    gf_common_len = 2 * 28
    gf_int_len = 28 + 2 * (12 + 7 + 7)

    ROOM_X1 = G.FF_BATH_DEPTH + G.FF_ROOM_DEPTH
    RY = G.FF_ROOM_Y_BOUNDS
    ff_ext_len = 28 + 38 + 38 + 38 + 28
    ff_int_len = sum(RY[i+1]-RY[i] for i in range(4)) + 3 * ROOM_X1

    len_9in = gf_ext_len + gf_common_len + ff_ext_len
    vol_9in = len_9in * F2F * 0.75
    len_45in = gf_int_len + ff_int_len
    vol_45in = len_45in * F2F * 0.375

    GAL_X1_CANT, GAL_X1_MAIN, GAL_NORTH = G.FF_GALLERY_X1_CANTILEVER, G.FF_GALLERY_X1_MAIN, G.FF_GALLERY_NORTH_EXT
    outline = [(0, 0), (GAL_X1_CANT, 0), (GAL_X1_CANT, GAL_NORTH), (GAL_X1_MAIN, GAL_NORTH), (GAL_X1_MAIN, 38), (0, 38)]
    parapet_perim = sum(abs(x1-x0)+abs(y1-y0) for (x0, y0), (x1, y1) in zip(outline, outline[1:]+outline[:1]))
    parapet_vol = parapet_perim * 3.0 * 0.5

    brick_gross_cum = (vol_9in + vol_45in + parapet_vol) * FT3_TO_M3
    brick_net_cum = brick_gross_cum * (1 - OPENING_DEDUCT)

    # ---- Plaster area (both faces, all walls + parapet) ----
    plaster_area_sqft = (len_9in + len_45in) * F2F * 2 + parapet_perim * 3.0 * 2
    plaster_net_sqm = plaster_area_sqft * 0.092903 * (1 - OPENING_DEDUCT)

    # ---- Steel (reuses Sheet S-004B's own computation) ----
    steel_kg = sum(r[4] for r in steelqty.compute())

    # ---- Cement / sand / aggregate: RCC (M20, 1:1.5:3) ----
    dry_concrete, ratio_concrete = 1.54, (1 + 1.5 + 3)
    rcc_cement_cum = rcc_cum * (1/ratio_concrete) * dry_concrete
    rcc_cement_bags = rcc_cement_cum * 1440 / 50
    rcc_sand_cum = rcc_cum * (1.5/ratio_concrete) * dry_concrete
    rcc_agg_cum = rcc_cum * (3/ratio_concrete) * dry_concrete

    # ---- Cement / sand / bricks: brickwork (1:6 CM) ----
    bricks_per_cum = 500
    n_bricks = brick_net_cum * bricks_per_cum
    brick_each_vol = 0.19 * 0.09 * 0.09
    mortar_vol_per_cum = 1 - bricks_per_cum * brick_each_vol
    mortar_dry = mortar_vol_per_cum * 1.33
    brick_cement_cum = brick_net_cum * mortar_dry / 7
    brick_cement_bags = brick_cement_cum * 1440 / 50
    brick_sand_cum = brick_net_cum * mortar_dry * 6 / 7

    # ---- Cement / sand: plaster (12mm, 1:6) ----
    plaster_wet_vol = plaster_net_sqm * 0.012
    plaster_dry_vol = plaster_wet_vol * 1.27
    plaster_cement_cum = plaster_dry_vol / 7
    plaster_cement_bags = plaster_cement_cum * 1440 / 50
    plaster_sand_cum = plaster_dry_vol * 6 / 7

    total_cement_bags = rcc_cement_bags + brick_cement_bags + plaster_cement_bags
    total_sand_cum = rcc_sand_cum + brick_sand_cum + plaster_sand_cum
    total_agg_cum = rcc_agg_cum
    binding_wire_kg = steel_kg * 0.01

    rows = [
        ("Steel reinforcement (Fe500 TMT)", steel_kg, "kg", RATES["steel"]),
        ("Cement (OPC/PPC, 50kg bags)", total_cement_bags, "bags", RATES["cement"]),
        ("Sand (fine aggregate)", total_sand_cum, "cum", RATES["sand"]),
        ("Aggregate / Khadi (20mm crushed stone)", total_agg_cum, "cum", RATES["aggregate"]),
        ("Bricks (common/clay, 19x9x9cm modular)", n_bricks, "nos", RATES["brick"]),
        ("Binding wire", binding_wire_kg, "kg", RATES["wire"]),
    ]
    rows = [(item, qty, unit, rate, qty*rate) for item, qty, unit, rate in rows]

    # ---- Labour (client-supplied rates) ----
    rcc_labour_cost = slab_area_sqft * RCC_LABOUR_RATE
    brick_labour_days = brick_net_cum / BRICKWORK_PRODUCTIVITY
    plaster_labour_days = plaster_net_sqm / PLASTER_PRODUCTIVITY
    general_labour_days = brick_labour_days + plaster_labour_days
    general_labour_cost = general_labour_days * GENERAL_LABOUR_RATE

    mt_days = rcc_cum / MT_PRODUCTIVITY
    mt_cost = mt_days * MT_CREW_DAY_RATE

    labour_rows = [
        ("RCC labour (shuttering+steel-fixing+concreting)", slab_area_sqft, "sqft", RCC_LABOUR_RATE, rcc_labour_cost),
        ("General labour (brickwork+plastering)", general_labour_days, "days", GENERAL_LABOUR_RATE, general_labour_cost),
        (f"Material transformation & slab-filling crew ({MT_CREW_SKILLED}x Rs{MT_CREW_SKILLED_RATE:.0f} + {MT_CREW_UNSKILLED}x Rs{MT_CREW_UNSKILLED_RATE:.0f})",
         mt_days, "days", MT_CREW_DAY_RATE, mt_cost),
    ]

    basis = dict(rcc_cum=rcc_cum, brick_net_cum=brick_net_cum, plaster_net_sqm=plaster_net_sqm,
                 rcc_cement_bags=rcc_cement_bags, brick_cement_bags=brick_cement_bags,
                 plaster_cement_bags=plaster_cement_bags, rcc_sand_cum=rcc_sand_cum,
                 brick_sand_cum=brick_sand_cum, plaster_sand_cum=plaster_sand_cum,
                 slab_area_sqft=slab_area_sqft, brick_labour_days=brick_labour_days,
                 plaster_labour_days=plaster_labour_days, general_labour_days=general_labour_days,
                 mt_days=mt_days)
    return rows, labour_rows, basis


def make():
    fig, ax = new_sheet("08C", "PRELIMINARY MATERIAL & COST ESTIMATE", "N/A (table)", "S-004C")
    ax.axis('off')
    ax.set_aspect('auto')
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)

    rows, labour_rows, basis = compute()
    material_total = sum(r[4] for r in rows)
    labour_total = sum(r[4] for r in labour_rows)
    grand_total = material_total + labour_total

    ax.text(5, 9.55, "PRELIMINARY MATERIAL & COST ESTIMATE", fontsize=18, fontweight='bold', ha='center', family='monospace')
    ax.text(5, 9.16, "(thumb-rule quantities for budgeting only -- rates are INDICATIVE, verify current local rates before use)",
            fontsize=12, ha='center', family='monospace', style='italic')

    col_x = [0.3, 4.55, 5.75, 6.85, 8.05]
    headers = ["MATERIAL", "QUANTITY", "UNIT", "RATE (Rs)", "COST (Rs)"]
    y = 8.72
    for cx, h in zip(col_x, headers):
        ax.text(cx, y, h, fontsize=12, fontweight='bold', family='monospace')
    y -= 0.18
    ax.plot([0.2, 9.8], [y, y], color='black', lw=0.8)
    y -= 0.30

    for item, qty, unit, rate, cost in rows:
        ax.text(col_x[0], y, item, fontsize=12, family='monospace')
        ax.text(col_x[1], y, f"{qty:,.0f}", fontsize=12, family='monospace', ha='right')
        ax.text(col_x[2], y, unit, fontsize=12, family='monospace')
        ax.text(col_x[3], y, f"{rate:,.0f}", fontsize=12, family='monospace', ha='right')
        ax.text(col_x[4]+0.9, y, f"{cost:,.0f}", fontsize=12, family='monospace', ha='right')
        y -= 0.34

    y -= 0.04
    ax.plot([col_x[0], 9.8], [y, y], color='black', lw=0.5, linestyle=':')
    y -= 0.28
    ax.text(col_x[0], y, "Material subtotal", fontsize=12, fontweight='bold', family='monospace')
    ax.text(col_x[4]+0.9, y, f"{material_total:,.0f}", fontsize=12, fontweight='bold', family='monospace', ha='right')

    y -= 0.40
    ax.text(col_x[0], y, "LABOUR", fontsize=12, fontweight='bold', family='monospace')
    y -= 0.30
    for item, qty, unit, rate, cost in labour_rows:
        ax.text(col_x[0], y, item, fontsize=12, family='monospace')
        ax.text(col_x[1], y, f"{qty:,.0f}", fontsize=12, family='monospace', ha='right')
        ax.text(col_x[2], y, unit, fontsize=12, family='monospace')
        ax.text(col_x[3], y, f"{rate:,.0f}", fontsize=12, family='monospace', ha='right')
        ax.text(col_x[4]+0.9, y, f"{cost:,.0f}", fontsize=12, family='monospace', ha='right')
        y -= 0.34

    y -= 0.04
    ax.plot([col_x[0], 9.8], [y, y], color='black', lw=0.5, linestyle=':')
    y -= 0.28
    ax.text(col_x[0], y, "Labour subtotal", fontsize=12, fontweight='bold', family='monospace')
    ax.text(col_x[4]+0.9, y, f"{labour_total:,.0f}", fontsize=12, fontweight='bold', family='monospace', ha='right')

    y -= 0.10
    ax.plot([0.2, 9.8], [y, y], color='black', lw=0.8)
    y -= 0.32
    ax.text(col_x[0], y, "GRAND TOTAL (material + labour, excl. finishes)", fontsize=12, fontweight='bold', family='monospace')
    ax.text(col_x[4]+0.9, y, f"Rs {grand_total:,.0f}", fontsize=12, fontweight='bold', family='monospace', ha='right')

    y -= 0.5
    built_up_sqft = G.GROUND_COVERAGE * 2
    ax.text(0.3, y, f"Material basis: RCC concrete {basis['rcc_cum']:.0f} cum (M20, 1:1.5:3) | Brickwork {basis['brick_net_cum']:.0f} cum net "
            f"(1:6 CM, {int(OPENING_DEDUCT*100)}% opening deduction) | Plaster {basis['plaster_net_sqm']:.0f} sqm net (12mm, 1:6)",
            fontsize=10, family='monospace')
    y -= 0.20
    ax.text(0.3, y, f"Cement split: RCC {basis['rcc_cement_bags']:.0f} + brickwork {basis['brick_cement_bags']:.0f} + plaster "
            f"{basis['plaster_cement_bags']:.0f} bags. Sand split: RCC {basis['rcc_sand_cum']:.1f} + brickwork {basis['brick_sand_cum']:.1f} "
            f"+ plaster {basis['plaster_sand_cum']:.1f} cum.", fontsize=10, family='monospace')
    y -= 0.20
    ax.text(0.3, y, f"Labour basis (client-supplied rates, 2026-09): RCC labour = Rs {RCC_LABOUR_RATE:.0f}/sqft x {basis['slab_area_sqft']:.0f} sqft "
            f"RCC (slab) area cast.", fontsize=10, family='monospace')
    y -= 0.20
    ax.text(0.3, y, f"General labour = Rs {GENERAL_LABOUR_RATE:.0f}/day x {basis['general_labour_days']:.0f} labour-days, estimated from "
            f"brickwork ({basis['brick_labour_days']:.0f} days @ {BRICKWORK_PRODUCTIVITY:.1f} cum/day) + plastering "
            f"({basis['plaster_labour_days']:.0f} days @ {PLASTER_PRODUCTIVITY:.0f} sqm/day).", fontsize=10, family='monospace')
    y -= 0.20
    ax.text(0.3, y, f"Material transformation/slab-filling crew = Rs {MT_CREW_DAY_RATE:.0f}/day ({MT_CREW_SKILLED} x Rs{MT_CREW_SKILLED_RATE:.0f} + "
            f"{MT_CREW_UNSKILLED} x Rs{MT_CREW_UNSKILLED_RATE:.0f}) x {basis['mt_days']:.0f} days, estimated from the {basis['rcc_cum']:.0f} cum "
            f"RCC concrete @ {MT_PRODUCTIVITY:.0f} cum/day placement rate for this crew.", fontsize=10, family='monospace')

    north_arrow(fig, 0.92, 0.90)

    notes_block(fig, [
        "MATERIAL rates are INDICATIVE ONLY (approx. national-average India, 2025) and WILL vary significantly by city, season, supplier and quantity ordered -- obtain current local quotations before budgeting; do not use for tendering.",
        "LABOUR rates (Rs220/sqft RCC, Rs1100/day general, Rs1100+Rs400/day MT crew) are CLIENT-SUPPLIED (2026-09); all labour-DAY counts are this set's own estimate (CPWD-type norms), not client-supplied -- verify with your contractor.",
        "POSSIBLE OVERLAP: the RCC labour line (covers shuttering+steel-fixing+CONCRETING) and the material-transformation/slab-filling crew (also covers concrete placement) may both price the same concreting work.",
        "Confirm with your contractor whether these two are genuinely separate cost pools before totalling; if not, drop one of the two.",
        "Steel quantity is carried directly from Sheet S-004B's preliminary BBS summary (same 18 footings/columns, beam/slab geometry). See S-004B for the member-by-member breakdown.",
        "Concrete grade M20 (1:1.5:3 nominal mix) assumed for all RCC (footings, pedestals, columns, beams, slabs, waist slab); dry-volume factor 1.54 used for cement/sand/aggregate proportioning.",
        "Brickwork assumed 1:6 cement:sand mortar, standard 19x9x9cm bricks (500/cum), covering external/common/internal walls (both floors) + parapet; a flat 12% deduction applied for openings -- a thumb-rule, not a door/window takeoff.",
        "Plaster assumed 12mm thick, 1:6 cement:sand, both faces of every wall and the parapet, same 12% opening deduction.",
        "EXCLUDED: shuttering/formwork, scaffolding, doors/windows, electrical, plumbing fixtures, sanitary ware, paint, flooring/tiling, water tank, skirting, waterproofing, site supervision, contractor margin/GST.",
        "This is a PRELIMINARY budgeting estimate only. Final quantities and labour rates must be verified from the structural engineer's BBS (Sheet S-004B), your actual labour contractor, and a detailed architect's/contractor's BOQ before finalising a construction budget.",
    ], y=0.088)
    return fig
