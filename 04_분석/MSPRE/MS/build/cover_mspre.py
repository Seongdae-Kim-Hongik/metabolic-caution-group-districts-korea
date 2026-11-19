import os, re, datetime, subprocess
from docx import Document
from docx.shared import Pt, Cm
import content_mspre as C
from build_manuscript_mspre import ZENODO, ADDR
TITLE = C.TITLE
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "out")
N = C.N; W = dict(l.split("=") for l in open(os.path.join(OUT, "wordcount_ms.txt")).read().split()); th = C.th; tc = C.tc
assert ZENODO.startswith("10.5281/zenodo.")
_d = datetime.date.today(); cl = [f"{_d:%B} {_d.day}, {_d.year}", "The Editor", "the target journal", "",
      "Dear Dr. Leonard,",
      f"Please find enclosed the manuscript entitled \"{TITLE}\" by Seongdae Kim, for consideration as an Original Research Article in the the target journal.",
      f"Nearly half of adults attending Korea's national general health screening have one or two metabolic syndrome components, an intermediate state between metabolic health and the full syndrome that has seldom been described at the population level. Using national screening statistics for all {N['n_districts']} Korean districts ({N['cases_total_m']:.1f} million caution-group judgements among {N['exam_total_m']:.1f} million examinees, 2019-2024), sex- and age-standardized expected counts, and Bayesian spatio-temporal models, the study shows that this intermediate state follows a small but persistent geography, modestly higher in rural districts of the southern provinces and lower in the capital region, and that it is inversely aligned with the share of adults holding a college or university degree. The study also documents how a national change in the lipid-testing interval altered the composition of the components, and it reports all sensitivity and spatial-confounding analyses.",
      "The work fits the journal's interest in population variation in human biology and health in its epidemiological and ecological context: it describes how an early metabolic phenotype is distributed within a population undergoing rapid economic and nutritional transition and how that distribution aligns with a social gradient.",
      "The manuscript is original research, has not been published previously, and is not under consideration for publication elsewhere; the author has approved its submission.",
      f"The main text contains {th(int(W['body_words']))} words, with an abstract of {int(W['abstract_words'])} words, two tables, two figures, and {W['refs']} references; supporting information is provided. The analysis code is openly available on Zenodo (https://doi.org/{ZENODO}).",
      "Thank you for considering this manuscript.", "", "Sincerely,", "",
      "Seongdae Kim, PhD", ADDR, "Email: kimsd@hongik.ac.kr"]
d = Document(); st = d.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11); st.paragraph_format.space_after = Pt(4); st.paragraph_format.line_spacing = 1.0
for s in d.sections: s.page_width, s.page_height = Cm(21), Cm(29.7); s.left_margin = s.right_margin = s.top_margin = s.bottom_margin = Cm(2.54)
gap = False
for t in cl:
    if t == "": gap = True; continue
    p = d.add_paragraph(t)
    if gap: p.paragraph_format.space_before = Pt(10); gap = False
d.core_properties.author = "Seongdae Kim"; d.core_properties.last_modified_by = "Seongdae Kim"; d.core_properties.title = "Cover Letter"; d.core_properties.comments = ""
fp = os.path.join(OUT, "Cover_Letter.docx"); d.save(fp)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_mspre_cl", "--convert-to", "pdf", "--outdir", OUT, fp], capture_output=True)
txt = subprocess.run(["pdftotext", fp.replace(".docx", ".pdf"), "-"], capture_output=True, text=True).stdout
assert not re.search(r"\b(we|our|us|I)\b", txt) and "—" not in txt and not re.search(r"(?i)funding|competing|overlap|previously submitted|Chun|reviewer", txt), "문체·금지 항목"
pages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", fp.replace(".docx", ".pdf")], capture_output=True, text=True).stdout).group(1)); assert pages == 1, pages
open(os.path.join(OUT, "Cover_Letter_paste.txt"), "w").write("\n\n".join(t for t in cl if t))
print("saved", fp)
