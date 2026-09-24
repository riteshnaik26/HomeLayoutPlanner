import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import lib
lib.TEXT_SCALE = 1.12    # notes text boost, A4 build only
lib.TITLE_SCALE = 1.2    # sheet title/scale/dwg-no/sheet-number boost, A4 build only

import sheet00_cover, sheet01_site, sheet02_columns, sheet03_foundation, sheet04_groundfloor
import sheet05_firstfloor, sheet06_terrace, sheet07_beams, sheet08_slab
import sheet08b_rebar, sheet08c_steelqty, sheet08d_materialcost, sheet09_stair
import sheet12_sections
import sheet13_front_elev, sheet14_side_elev, sheet15_master

mods = [sheet00_cover, sheet01_site, sheet02_columns, sheet03_foundation, sheet04_groundfloor,
        sheet05_firstfloor, sheet06_terrace, sheet07_beams, sheet08_slab,
        sheet08b_rebar, sheet08c_steelqty, sheet08d_materialcost, sheet09_stair,
        sheet12_sections,
        sheet13_front_elev, sheet14_side_elev, sheet15_master]

tmp = os.path.join(os.path.dirname(__file__), "_a4_source_tmp.pdf")
with PdfPages(tmp) as pdf:
    for m in mods:
        fig = m.make()
        pdf.savefig(fig)
        plt.close(fig)
        print("ok", m.__name__)
print("SOURCE ->", tmp)

# ---- Rescale every page to true A4 landscape ----
from pypdf import PdfReader, PdfWriter
A4_W = 297 * 72 / 25.4
A4_H = 210 * 72 / 25.4
reader = PdfReader(tmp)
writer = PdfWriter()
for page in reader.pages:
    page.scale_to(A4_W, A4_H)
    writer.add_page(page)
out = os.path.join(os.path.dirname(__file__), "GPlus1Terrace_Drawing_Set_A4.pdf")
with open(out, "wb") as f:
    writer.write(f)
os.remove(tmp)
print("DONE ->", out)
