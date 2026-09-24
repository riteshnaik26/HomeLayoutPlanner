"""
Locked geometric design basis for the drawing set (Revision 2 -- updated to
match the client's own ground-floor PDF and first-floor sketch: corridor-
style ground floor with a central WC/Shower/Kitchen spine either side of the
stair, and a first floor with 4 rooms + ensuite + continuous back balcony +
a gallery that cantilevers over the parking).
All values in feet. See DESIGN_NOTES at bottom (also printed on Sheet 00).
"""
import numpy as np

# ---- SITE (irregular quadrilateral, corners solved from given side lengths)
SITE_SOUTH = 41.5   # SW-SE
SITE_WEST  = 48.0   # SW-NW
SITE_NORTH = 43.0   # NW-NE
SITE_EAST  = 51.0   # SE-NE

SW = np.array([0.0, 0.0])
SE = np.array([SITE_SOUTH, 0.0])
NW = np.array([0.0, SITE_WEST])

def _solve_NE(a, b, p0, p1):
    """Solve NE such that |NE-p0|=a (north side) and |NE-p1|=b (east side)."""
    x0, y0 = p0; x1, y1 = p1
    A = 2 * (x1 - x0)
    B = 2 * (y1 - y0)
    C = (a*a - b*b) - (x0*x0 + y0*y0) + (x1*x1 + y1*y1)
    if abs(B) > 1e-9:
        m = -A / B
        c = C / B - y0
        aa = 1 + m*m
        bb = -2*x0 + 2*m*c
        cc = x0*x0 + c*c - a*a
        disc = bb*bb - 4*aa*cc
        x_sol = (-bb + np.sqrt(disc)) / (2*aa)
        y_sol = m * x_sol + c + y0
        return np.array([x_sol, y_sol])
    raise ValueError("degenerate site geometry")

NE = _solve_NE(SITE_NORTH, SITE_EAST, NW, SE)
SITE_POLY = np.array([SW, SE, NE, NW])

# ---- COMPASS (matches the client's own sketches: North = car-parking side,
# East = main entry / bike-parking side, South = party wall, West = garden)
# Building-local coords: x = 0..28 depth EAST-WEST, y = 0..38 width NORTH-SOUTH
BW = 28.0   # East-West extent (main enclosed footprint)
BD = 38.0   # North-South extent
GROUND_COVERAGE = BW * BD   # 1,064 sq.ft. main footprint (unchanged)

BX0 = 2.0
BY0 = 0.0
BX1 = BX0 + BW
BY1 = BY0 + BD

WEST_SETBACK_SHOWN  = BX0 - 0.0
EAST_SETBACK_SOUTH  = SITE_SOUTH - BX1
NORTH_SETBACK_SHOWN = 8.0
SOUTH_SETBACK = 0.0

# ---- FIRST FLOOR room depth (defined here, early, because the mid column
# line GX_MID below is deliberately positioned to land exactly on the
# Room/Gallery wall this produces -- see REVISION 3 note).
# REVISION 8: bath 5'x6', total room (bath+room) 12'x9'-6" per client
# instruction -- this re-sets GX_MID to 12' (was 18'), which is also what
# now gives P11-P15/P12-P16/P13-P17/P14-P18 = 12' and P6-P11/P7-P12/
# P8-P13/P9-P14 = 16' (28-12), both requested explicitly.
FF_BATH_DEPTH = 5.0
FF_ROOM_DEPTH = 7.0   # room-only depth (excl. bath); bath+room = 12' total

# ---- COLUMN GRID (building-local coordinates)
GY = [0.0, 12.0, 26.0, 38.0]           # shared N-S spacing, all 4 main lines
GX_WEST = 0.0     # P15-P18 line (west face)
GX_MID  = FF_BATH_DEPTH + FF_ROOM_DEPTH  # 12.0 -- P11-P14 line: lands on the
                  # Room/Gallery wall upstairs (bath 5' + room 7'), per
                  # REVISION 8.
GX_EAST = 28.0    # P6-P9 line (east face, main entry side)
GX_CANOPY = 36.0  # P1-P5 line (8 ft east of building, over bike-parking canopy)
GY_CANOPY = [0.0, 12.0, 26.0, 38.0, 47.0]   # spacing 12-14-12-9

# P10 repositioned per client feedback: sits directly above P9 (same grid
# line, x=GX_EAST) and directly left of P5 (same canopy row, y=47) -- the
# missing corner column completing the canopy's rectangle, carrying the
# first-floor gallery's extension over the car-parking side.
P10_POS = (GX_EAST, GY_CANOPY[-1])   # (28.0, 47.0)

COLS = {
    "P1": (GX_CANOPY, GY_CANOPY[0]), "P2": (GX_CANOPY, GY_CANOPY[1]),
    "P3": (GX_CANOPY, GY_CANOPY[2]), "P4": (GX_CANOPY, GY_CANOPY[3]),
    "P5": (GX_CANOPY, GY_CANOPY[4]),
    "P6": (GX_EAST, GY[0]), "P7": (GX_EAST, GY[1]),
    "P8": (GX_EAST, GY[2]), "P9": (GX_EAST, GY[3]),
    "P10": P10_POS,
    "P11": (GX_MID, GY[0]), "P12": (GX_MID, GY[1]),
    "P13": (GX_MID, GY[2]), "P14": (GX_MID, GY[3]),
    "P15": (GX_WEST, GY[0]), "P16": (GX_WEST, GY[1]),
    "P17": (GX_WEST, GY[2]), "P18": (GX_WEST, GY[3]),
}
COL_SIZE = (1.0, 1.25)  # 12in x 15in

# ---- FOOTINGS (REVISION 7): per client feedback, 9 columns sit at or very
# near a plot boundary -- the south party wall (y=0, zero setback), the east
# canopy line (x=36, near the east boundary), or the far north corner (y=47,
# near the north setback line) -- and cannot take a normal, symmetric 6'x6'
# footing centred on the column without crossing the boundary. For these,
# the footing is HALVED on the boundary side(s): it extends the full 3' only
# on the safe/interior side, and 0' beyond the column on the boundary side,
# giving an 18 sq.ft "half footing" (6'x3' or 3'x6'), or a 9 sq.ft "quarter"
# footing at the two true corners (P1, P5 -- see REVISION 8) where two
# boundaries meet.
# FOOT_TRIM[col] = (x_trim, y_trim); x_trim/y_trim in {None, 'lo', 'hi'} means
# don't extend the footing below/above the column's own x or y coordinate.
FOOT_SIZE_FULL = 6.0   # normal isolated footing, 6'x6'
FOOT_HALF = 3.0         # halved dimension on a trimmed side
# x_trim: 'lo' = extend footing toward -x (west) only, i.e. trim the east
#         side; 'hi' = extend toward +x (east) only, trim the west side.
# y_trim: 'lo' = extend toward -y (south) only, trim the north side;
#         'hi' = extend toward +y (north) only, trim the south side.
# REVISION 8: P5 reclassified as a true corner (east canopy boundary AND
# the north setback line both run close by it, same as P1) -- footing kept
# fully inside both boundary lines, quarter-size like P1. P15 reclassified
# the OTHER way: its west side has a full 6' garden setback to the property
# line (2' shown to the building face, 6' total per the brief), so a
# full-width footing there does not cross the boundary -- only its south
# side (the zero-setback party wall) needs trimming, same as P11.
FOOT_TRIM = {
    "P1":  ('lo', 'hi'),   # canopy line, south end -- east boundary + south wall (corner)
    "P2":  ('lo', None),   # canopy line -- east boundary
    "P3":  ('lo', None),
    "P4":  ('lo', None),
    "P5":  ('lo', 'lo'),   # canopy line, north end -- east boundary + north setback (corner)
    "P6":  (None, 'hi'),   # south party wall -- extend north (interior) only
    "P10": (None, 'lo'),   # far north corner -- extend south (interior) only
    "P11": (None, 'hi'),   # south party wall
    "P15": (None, 'hi'),   # south party wall only -- west side has 6' garden clearance
}

def footing_extents(col_name):
    """Return (x0, x1, y0, y1) for the footing at column `col_name`, applying
    the half/quarter trim above where applicable; a normal centred 6'x6'
    footing otherwise."""
    cx, cy = COLS[col_name]
    xt, yt = FOOT_TRIM.get(col_name, (None, None))
    if xt is None:
        x0, x1 = cx - FOOT_SIZE_FULL/2, cx + FOOT_SIZE_FULL/2
    elif xt == 'lo':
        x0, x1 = cx - FOOT_HALF, cx
    else:
        x0, x1 = cx, cx + FOOT_HALF
    if yt is None:
        y0, y1 = cy - FOOT_SIZE_FULL/2, cy + FOOT_SIZE_FULL/2
    elif yt == 'lo':
        y0, y1 = cy - FOOT_HALF, cy
    else:
        y0, y1 = cy, cy + FOOT_HALF
    return x0, x1, y0, y1

# ---- WALLS
EXT_WALL_T = 9.0 / 12.0
INT_WALL_T = 4.5 / 12.0
COMMON_WALL_T = 9.0 / 12.0

# ---- GROUND FLOOR: two units (S and N) separated by a full-depth central
# corridor (Y band) housing each unit's own WC + Shower + Kitchen, matching
# the client's ground-floor PDF. (REVISION 4: no longer holds the stair --
# see EXT_STAIR below -- so the corridor is now a plain, unbroken spine.)
UNIT_A_Y = (0.0, 12.0)    # south unit (Bedroom + Living only)
CORRIDOR_Y = (12.0, 26.0)  # 14'-0" -- the "P2-P3" bay, shared by both units
UNIT_B_Y = (26.0, 38.0)   # north unit (Bedroom + Living only)

FLOOR_TO_FLOOR = 10.5

# ---- COMMON STAIRCASE (REVISION 5): OPEN/COVERED EXTERNAL staircase in the
# bike-parking zone (x=28..36, the 8' strip between the main east wall and
# the canopy line), between columns P2 and P3 -- the original "P2-P3" bay,
# y=12..26, 14' available -- exactly as marked up by the client. Width
# (x-direction) sits within the bike-parking strip; run (y-direction) is
# the full 14' P2-P3 bay.
# REVISION 8: overall width reduced 6' -> 3' per client instruction. A
# single 3'-wide flight is no longer wide enough for two side-by-side
# flights (the old "two 3' flights" dog-leg); see Sheet A-005 for the
# revised single-lane, half-turn stair this now uses.
STAIR_X = (33.0, 36.0)     # 3'-0" wide, flush with the canopy line (P2/P3)
STAIR_Y = (12.0, 26.0)     # 14' run -- the P2-P3 bay

# ---- FIRST FLOOR: 4 independent rooms along the West/garden side, each with
# an ensuite bath and opening onto a continuous back balcony; a gallery/
# lounge runs along the East side and cantilevers over the parking.
FF_ROOM_Y_BOUNDS = [0.0, 9.5, 19.0, 28.5, 38.0]   # 4 rooms x 9.5' wide
FF_BALCONY_DEPTH = 6.0                             # projects into the 6' west setback
# FF_BATH_DEPTH / FF_ROOM_DEPTH are defined above, near GX_MID
# room occupies x = FF_BATH_DEPTH .. FF_BATH_DEPTH+FF_ROOM_DEPTH = 6..18
FF_GALLERY_X0 = FF_BATH_DEPTH + FF_ROOM_DEPTH       # 18.0 -- coincides with GX_MID
FF_GALLERY_X1_MAIN = BW                             # 28.0 (within main footprint)
FF_GALLERY_X1_CANTILEVER = GX_CANOPY                # 36.0 (over full bike-parking width)
FF_GALLERY_NORTH_EXT = P10_POS[1]                   # 47.0 -- extends to and lands squarely on column P10

# ---- REINFORCEMENT (preliminary / thumb-rule sizing -- see Sheets S-004A/B)
# Bar unit weights, kg/m, by nominal diameter (mm): w = d^2 / 162 (IS 1786)
BAR_WT = {8: 0.395, 10: 0.617, 12: 0.888, 16: 1.578, 20: 2.466}
FE_GRADE = "Fe500"
CONCRETE_GRADE = "M20"

REBAR = {
    "footing": dict(desc="Isolated footing (6'x6'x1'-6\")", bottom_bar=12, bottom_spacing=150,
                     note="Two-way mesh, bottom only; top steel not normally required for isolated footings of this size."),
    "pedestal": dict(desc="Pedestal (2'x2')", main_bar=12, main_count=6, tie_bar=8, tie_spacing=150),
    "column": dict(desc="Column (12\"x15\")", main_bar=16, main_count=6, tie_bar=8, tie_spacing=150,
                    tie_spacing_joint=100, note="Tie spacing reduced to 100mm within 1x column-width of every beam-column joint."),
    "main_beam": dict(desc="Main beam (9\"x18\")", top_bar=16, top_count=3, bottom_bar=16, bottom_count=3,
                        stirrup_bar=8, stirrup_spacing=150, stirrup_spacing_support=100),
    "secondary_beam": dict(desc="Secondary beam (9\"x12\")", top_bar=12, top_count=2, bottom_bar=12, bottom_count=2,
                             stirrup_bar=8, stirrup_spacing=150, stirrup_spacing_support=100),
    "plinth_beam": dict(desc="Plinth/tie beam (9\"x12\", typ. same as secondary beam)", top_bar=12, top_count=2,
                          bottom_bar=12, bottom_count=2, stirrup_bar=8, stirrup_spacing=150),
    "slab": dict(desc="Slab (5\"-6\" thick)", main_bar=10, main_spacing=150, dist_bar=8, dist_spacing=200,
                  note="Extra top steel (same bar/spacing as main) over all continuous supports, 0.3x span from face of support."),
    "stair_waist": dict(desc="Staircase waist slab", main_bar=10, main_spacing=125, dist_bar=8, dist_spacing=200),
}

# ---- DESIGN NOTES (also rendered on Sheet 00) ----------------------------
DESIGN_NOTES = [
 "The brief's site boundary lengths (E 51', W 48', N 43', S 41.5') and the "
 "requested building (38'x28') + setbacks (E 8' bike, W 6' garden) do not "
 "reconcile if the building's 38' side is read East-West: 38+8+6=52' would "
 "exceed the ~42' plot width on that axis. Reconciliation: the building is "
 "oriented with its 28' side East-West and 38' side North-South (28+8+6="
 "42', matching the plot width almost exactly). Total main footprint "
 "unchanged at 28x38=1,064 sq.ft. Re-verify against the actual survey "
 "before construction.",
 "REVISION 2: Ground floor rebuilt to match the client's own layout PDF -- "
 "two 12'-deep end units (Bedroom + Living Room, South and North) flank a "
 "full-depth 14' wide central corridor (the 'P2-P3' grid bay) that houses "
 "the common stair plus each unit's own WC, Shower and Kitchen.",
 "18 columns P1-P18. P1-P5 (canopy line, spacing 12-14-12-9) sit 8' east of "
 "the main east face, over the bike-parking walkway. P6-P9/P11-P14/P15-P18 "
 "are the three main N-S lines (spacing 12-14-12). P10 -- not part of any "
 "stated bay -- is the corner column between P9 and P5 that carries the "
 "first-floor gallery's extension over the car-parking side.",
 "REVISION 4/5: Common staircase relocated OUTSIDE the main building, per "
 "client feedback -- an open/covered external dog-leg stair in the bike-"
 "parking zone (x=28-36, between the main wall and the canopy line), "
 "positioned between columns P2 and P3 -- the original 'P2-P3' bay, "
 "y=12-26, 14' available, exactly as marked up by the client. 6' wide, "
 "two 3' flights side by side, 18 risers @ 7\" / 16 treads @ 10.5\" for "
 "the 10'-6\" floor height, 5' landing. The former internal stair void is "
 "removed from the central corridor, which is now a plain spine (Kitchen "
 "widened to fill the freed space) -- see Sheets A-002, A-003, A-004 and "
 "A-005.",
 "REVISION 2: First floor rebuilt to match the client's sketch -- 4 rooms "
 "(14'x9'-6\" each, per the original brief) along the West/garden side, "
 "each with a 6'-deep ensuite bath and opening onto a CONTINUOUS 6' deep "
 "back balcony spanning the full West side. A gallery/lounge along the "
 "East side cantilevers out to fully cover the 8' bike-parking width "
 "below, and extends north along it to land squarely on column P10 "
 "(directly above P9, in line with P5), covering the North car-parking "
 "setback in the same reach.",
 "REVISION 3: The P11-P14 column line moved from x=12' to x=18' (and "
 "first-floor room depth reduced 14'->12') after the client noticed a "
 "column landing inside the first-floor rooms. x=18' is exactly the "
 "Room/Gallery wall on the first floor AND the Kitchen's west wall on the "
 "ground floor -- as a bonus this also fixes a pre-existing problem where "
 "x=12' sat inside the stair void itself. See Sheets S-001 and A-003.",
 "REVISION 6: Electrical layout REMOVED from this set at the client's "
 "request (to be supplied separately). Added Sheets S-004A (typical "
 "reinforcement details -- bar sizes/spacing for every footing, column, "
 "beam, slab and stair) and S-004B (a preliminary steel quantity "
 "estimate). Both are THUMB-RULE / preliminary sizing for budgeting and "
 "coordination only -- not a substitute for a full structural analysis "
 "and bar bending schedule (BBS), which remains required before "
 "construction.",
 "REVISION 7: 9 of the 18 footings (P1, P2, P3, P4, P5, P6, P10, P11, P15) "
 "sit at or very near a plot boundary and are HALVED on the boundary "
 "side(s), per client instruction, trimmed to either a 9 sq.ft quarter or "
 "an 18 sq.ft half footing (see REVISION 8 below for the final split "
 "between the two). See G.FOOT_TRIM / G.footing_extents() in this file "
 "(the single source of truth used by Sheets S-002 and S-004A), and "
 "Sheet S-004A for the reinforcement detail. Plinth/tie beams at these 9 "
 "columns also act as STRAP BEAMS resisting the eccentric loading -- to "
 "be confirmed by the structural engineer. Sheet S-004B's steel quantity "
 "estimate reflects the reduced footing sizes.",
 "REVISION 8: Per further client instruction: (1) bath resized to 5'x6', "
 "total first-floor room (bath+room) resized to 12'x9'-6\", which moves "
 "the P11-P14 column line to x=12' (was 18') -- giving P11-P15/P12-P16/"
 "P13-P17/P14-P18 = 12' and P6-P11/P7-P12/P8-P13/P9-P14 = 16', both as "
 "requested. (2) P5 reclassified as a true corner footing (quarter-size, "
 "kept inside both the east and north boundary lines), and P15 "
 "reclassified as a half footing like P11 (its west side has a full 6' "
 "garden setback, so only the south/party-wall side needs trimming) -- "
 "see G.FOOT_TRIM. (3) External staircase width reduced 6'->3'; the "
 "dog-leg (two parallel 3' flights) is replaced by a single 3'-wide "
 "half-turn flight sharing one lane, see Sheet A-005. (4) Terrace slab's "
 "north extension corrected to cover only the gallery CANTILEVER width "
 "(x=28-36, landing on P10), not the full width back to the P11-P14 "
 "line -- removes the extra slab area that had been shown between P10 "
 "and P14 on both the First Floor and Terrace plans.",
 "REVISION 9: Ground Floor doors reviewed against the client's own layout "
 "reference (LAYOUT 26). Added a 3'-0\" back door between each Bedroom and "
 "its WC (washroom), giving direct ensuite-style access without passing "
 "through the Living Room; swings into the Bedroom, clear of the WC "
 "fixture. Confirmed each unit's MAIN ENTRANCE remains on the Living Room "
 "(hall) East wall, per client instruction. See Sheet A-002.",
 "REVISION 10: Added Sheet S-004C, a preliminary MATERIAL & COST ESTIMATE "
 "(steel, cement, sand, aggregate/khadi, bricks, binding wire) covering "
 "the whole building, derived from this same geometry and from Sheet "
 "S-004B's steel BBS. Rates used are INDICATIVE ONLY (approx. national-"
 "average India) and exclude labour, shuttering, doors/windows, finishes "
 "and site overheads -- see S-004C for the full basis and exclusions.",
 "REVISION 11: Added LABOUR to Sheet S-004C, using client-supplied rates: "
 "RCC labour Rs 220/sqft (x total RCC/slab area cast) and general labour "
 "Rs 1100/labour-day. The number of general-labour-days is this set's own "
 "estimate (CPWD-type productivity: ~1.0 cum/day brickwork, ~16 sqm/day "
 "plastering, applied to the brickwork/plaster quantities already on "
 "S-004C) -- NOT a client-supplied figure, verify with the actual "
 "contractor. New grand total = material + labour, still excluding "
 "shuttering, finishes, other trades and site overheads.",
 "REVISION 12: Added a third labour line to Sheet S-004C: a material "
 "transformation/slab-filling crew (4 labour @ Rs1100/day + 4 labour @ "
 "Rs400/day = Rs6000/day), per client instruction. Day count estimated "
 "from the 96 cum RCC concrete volume at a thumb-rule 4 cum/day placement "
 "rate for this crew -- NOT a client-supplied figure. NOTE: this may "
 "overlap with the existing RCC labour line (Rs220/sqft), which already "
 "covers concreting; confirm with the contractor whether both are "
 "genuinely separate cost pools before totalling the budget.",
 "This package is a coordinated SCHEMATIC / design-development set for "
 "planning and client review. Final footing sizes, reinforcement, bar "
 "bending schedules and the cantilever design at the gallery must be "
 "verified and stamped by a licensed structural engineer before "
 "construction, notwithstanding the 'rocky soil' assumption used here.",
]
