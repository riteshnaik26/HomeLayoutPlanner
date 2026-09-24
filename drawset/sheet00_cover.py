import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import geometry as G

def make():
    fig, ax = new_sheet("00", "COVER / INDEX / DESIGN BASIS NOTES", "NTS", "A-000")
    ax.axis('off')
    ax.set_aspect('auto')
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)

    ax.text(5, 9.4, "G+1+TERRACE RCC RESIDENTIAL BUILDING", fontsize=22, ha='center',
            fontweight='bold', family='monospace')
    ax.text(5, 8.9, "TWO-UNIT DUPLEX  —  SCHEMATIC ARCHITECTURAL & STRUCTURAL DRAWING SET",
            fontsize=12, ha='center', family='monospace')
    ax.plot([0.5, 9.5], [8.6, 8.6], color='black', lw=1.2)

    sheets = [
        ("A-000", "Cover / Index / Design Basis Notes"),
        ("A-001", "Site Development Plan"),
        ("S-001", "Column Layout Plan"),
        ("S-002", "Foundation Layout Plan"),
        ("A-002", "Ground Floor Plan"),
        ("A-003", "First Floor Plan"),
        ("A-004", "Terrace Floor Plan"),
        ("S-003", "Beam Layout Plan (GF Roof / FF Slab)"),
        ("S-004", "Slab Layout & Reinforcement Direction Plan"),
        ("S-004A", "Typical Reinforcement Details (Rebar Sizes)"),
        ("S-004B", "Steel Quantity Estimate (Preliminary BBS Summary)"),
        ("S-004C", "Preliminary Material & Cost Estimate"),
        ("A-005", "Staircase Plan & Section"),
        ("P-001", "Plumbing Layout (Water Supply, Soil & Waste)"),
        ("A-006", "Building Sections A-A & B-B"),
        ("A-007", "Front Elevation (North)"),
        ("A-008", "Side Elevation (East)"),
        ("A-009", "Dimensioned Ground-Floor Blueprint (Master Sheet)"),
    ]
    y0 = 8.2
    col_x = [(0.5, 1.35), (5.1, 5.95)]
    half = (len(sheets) + 1) // 2
    for ci, chunk in enumerate((sheets[:half], sheets[half:])):
        cx0, cx1 = col_x[ci]
        yy = y0
        ax.text(cx0, yy, "SHEET", fontsize=9.5, fontweight='bold', family='monospace')
        ax.text(cx1, yy, "TITLE", fontsize=9.5, fontweight='bold', family='monospace')
        yy -= 0.22
        ax.plot([cx0-0.1, cx1+3.7], [yy+0.12, yy+0.12], color='black', lw=0.6)
        for no, title in chunk:
            ax.text(cx0, yy, no, fontsize=8.3, family='monospace')
            ax.text(cx1, yy, title, fontsize=8.0, family='monospace')
            yy -= 0.235
    y = y0 - 0.22 - 0.235 * half

    ax.text(0.5, y - 0.15, "PROJECT DATA", fontsize=10, fontweight='bold', family='monospace')
    y -= 0.40
    data = [
        f"Plot (as surveyed): East {G.SITE_EAST}' | West {G.SITE_WEST}' | North {G.SITE_NORTH}' | South {G.SITE_SOUTH}' (irregular quadrilateral)",
        f"Building footprint: {G.BW:.0f}' (E-W) x {G.BD:.0f}' (N-S) = {G.GROUND_COVERAGE:.0f} sq.ft. ground coverage",
        "Structure: RCC framed, isolated footings, 18 columns 12\"x15\", RCC beams & slab, brick/block infill walls",
        "Floors: Ground Floor (2 residential units) + First Floor (4 bedrooms + common facilities) + Terrace",
        "Soil: assumed rocky, existing structure demolished, 3'-0\" compacted filling above existing ground level",
        "Electrical layout: EXCLUDED from this set -- to be provided separately by the client.",
    ]
    for d in data:
        ax.text(0.5, y, "- " + d, fontsize=10, family='monospace')
        y -= 0.24

    y -= 0.18
    ax.text(0.5, y, "DESIGN BASIS / RECONCILIATION NOTES (read before use):", fontsize=9,
            fontweight='bold', family='monospace')
    y -= 0.22
    import textwrap
    for i, note in enumerate(G.DESIGN_NOTES):
        wrapped = textwrap.wrap(note, width=250)
        ax.text(0.5, y, f"{i+1}. " + wrapped[0], fontsize=9, family='monospace')
        y -= 0.085
        for line in wrapped[1:]:
            ax.text(0.5, y, line, fontsize=9, family='monospace')
            y -= 0.085
        y -= 0.016
    return fig
