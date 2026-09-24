import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from matplotlib.backends.backend_pdf import PdfPages
import sheet00_cover, sheet01_site, sheet02_columns, sheet03_foundation, sheet04_groundfloor
import sheet05_firstfloor, sheet06_terrace, sheet07_beams, sheet08_slab
import sheet08b_rebar, sheet08c_steelqty, sheet08d_materialcost, sheet09_stair
import sheet10_plumbing, sheet12_sections
import sheet13_front_elev, sheet14_side_elev, sheet15_master

mods = [sheet00_cover, sheet01_site, sheet02_columns, sheet03_foundation, sheet04_groundfloor,
        sheet05_firstfloor, sheet06_terrace, sheet07_beams, sheet08_slab,
        sheet08b_rebar, sheet08c_steelqty, sheet08d_materialcost, sheet09_stair,
        sheet10_plumbing, sheet12_sections,
        sheet13_front_elev, sheet14_side_elev, sheet15_master]

out = os.path.join(os.path.dirname(__file__), "GPlus1Terrace_Drawing_Set.pdf")
with PdfPages(out) as pdf:
    d = pdf.infodict()
    d['Title'] = 'G+1+Terrace RCC Residential Building - Schematic Drawing Set'
    d['Author'] = 'Prepared with Claude'
    for m in mods:
        fig = m.make()
        pdf.savefig(fig)
        import matplotlib.pyplot as plt
        plt.close(fig)
        print("ok", m.__name__)
print("DONE ->", out)
