#   초록 ≤180(5개 머리말), 본문 ≤3,500, 표+그림 ≤4, 참고문헌 ≤35 AMA(위첨자 번호), P값 이탤릭, 보충 ≤10쪽.
import os, re, json, subprocess, datetime, zipfile
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from jkms_engine import JKMS
import content_mspre as C
import labels_mspre as B
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out"); os.makedirs(OUT, exist_ok=True)
N = C.N; REFS = json.load(open(os.path.join(HERE, "refs_mspre.json"), encoding="utf-8")); th = C.th
_zf = os.path.join(OUT, "zenodo_doi.txt"); ZENODO = open(_zf).read().strip() if os.path.exists(_zf) else "[ZENODO DOI]"
REPO = "metabolic-caution-group-districts-korea"; GITHUB = f"https://github.com/Seongdae-Kim-Hongik/{REPO}"
TITLE = C.TITLE; ORCID = "0000-0002-1525-0091"; EMAIL = "kimsd@hongik.ac.kr"
AFF1 = "Department of Biohealth Convergence Open Sharing System, Hongik University, Seoul, Republic of Korea"
AFF2 = "Department of Preventive Medicine, Korea University College of Medicine, Seoul, Republic of Korea"
ADDRESS = "Department of Biohealth Convergence Open Sharing System, Hongik University, 94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea"
FUNDING = "This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors."
AI_STATEMENT = "Generative AI tools (Claude, Anthropic; ChatGPT, OpenAI) were used only for translation and English-language editing. The author reviewed and verified all edited text, confirms that all tables and figures were generated from the actual study data by the author's own code, that no synthetic data were used, and that all references were checked against PubMed or publisher records, and takes full responsibility for the content."
ETHICS = "The Institutional Review Board of Hongik University approved the study on November 4, 2025 (7002340-202511-HR-012; continuing review 7002340-202611-HR-040) and waived informed consent because only published aggregate statistics were used."
CONTRIB = "S. Kim conceptualized the study, curated and analyzed the data, produced the figures and tables, wrote the manuscript, and approved the final version."
ACK = "The author thanks the National Health Insurance Service, the Korea Disease Control and Prevention Agency, and Statistics Korea for making the aggregate statistics publicly available."
SUBDATE = datetime.date.today().strftime("%B %-d, %Y")

def cites(t): return re.sub(r"\s*\[(@[^\]]+)\]", lambda m: "{{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}}", t)
def all_keys():
    src = open(os.path.join(HERE, "content_mspre.py"), encoding="utf-8").read(); src = re.sub(r"(?m)^\s*#.*$", "", src)
    return sorted({k.strip().lstrip("@") for g in re.findall(r"\[(@[^\]]+)\]", src) for k in g.split(";")})
KEYS = all_keys(); _miss = [k for k in KEYS if k not in REFS]; assert not _miss, _miss
def ref(k):   # AMA 10판
    r = REFS[k]
    if r["type"] == "web":
        return f"{r['authors']}. {r['title']}. Published {str(r['year'])[:4]}. Accessed November 20, 2026. {r['url']}"
    au = r["authors"]; a = ", ".join(au) if len(au) <= 6 else ", ".join(au[:3]) + ", et al"
    s = f"{a}. {r['title'].rstrip('.')}. <i>{r['journal'].replace('.', '')}</i>. {str(r['year'])[:4]}"
    if r.get("vol"): s += f";{r['vol']}" + (f"({r['issue']})" if r.get("issue") else "")
    if r.get("pages"): s += f":{str(r['pages'])}"
    return s + "." + (f" doi:{r['doi']}" if r.get("doi") else "")

class TX(JKMS):
    raw = False; table_bold = True
    def _emit(self, p, text, sz=12, bold=False, italic=False):
        if not self.raw: text = re.sub(r"(^|[\s(])-(?=\d)", "\\1\u2212", text); text = re.sub(r"(\d)-(\d)", "\\1\u2013\\2", text)
        return super()._emit(p, text, sz, bold, italic)
def page_numbers(J, lines=True):
    s = J.doc.sections[0]
    if not lines:
        for e in s._sectPr.findall(qn("w:lnNumType")): s._sectPr.remove(e)
    fp = s.footer.paragraphs[0]; fp.text = ""; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER; r = fp.add_run(); r.font.size = Pt(10)
    for tag, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        if tag: e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), tag); r._r.append(e)
        else: e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt; r._r.append(e)

def f3(r): return f"{r[0]:.3f} ({r[1]:.3f}-{r[2]:.3f})"
def st(r): return f"{r[0]:.3f}" + ("<sup>e</sup>" if (r[1] > 1 or r[2] < 1) else "")
def table1():
    T = N["T1"]; W = ["2019-2021", "2022-2024", "2019-2024"]
    rows = [["__H__", "Early-risk group"],
            ["  District-years, no."] + [f"{T[w]['n']:,}" for w in W],
            ["  Examinees, millions"] + [f"{T[w]['exam']/1e6:.1f}" for w in W],
            ["  Early-risk examinees, millions"] + [f"{T[w]['cases']/1e6:.1f}" for w in W],
            ["  Early-risk group, % of examinees"] + [f"{100*T[w]['rate']:.1f}" for w in W],
            ["  Standardized ratio, median (P10-P90)"] + [f"{T[w]['sir_med']:.3f} ({T[w]['sir_p10']:.3f}-{T[w]['sir_p90']:.3f})" for w in W]]
    for g, vs in B.GROUPS:
        rows.append(["__H__", f"{g}, mean (SD)"])
        for v in vs: rows.append([f"  {B.LABEL[v]}, {B.UNIT[v]}"] + [f"{T[w]['cov'][v][0]:.1f} ({T[w]['cov'][v][1]:.1f})" for w in W])
    foot = ("Note. P10-P90 = 10th and 90th percentiles of district standardized ratios. Characteristics are means (SD) across district-years before standardization; survey items are age-standardized district estimates from the Community Health Survey. "
            "Early-risk group = examinees with 1 or 2 of 5 metabolic syndrome components.")
    return ("TABLE 1\u2014 Early Metabolic Risk Group and District Characteristics: South Korea, 2019-2024", ["Characteristic", "2019-2021", "2022-2024", "2019-2024"], rows, foot)
def table2():
    rows = []
    for g, vs in B.GROUPS:
        rows.append(["__H__", g])
        for v in vs:
            ctrl = g == "Fixed adjustments"
            rows.append([f"  {B.LABEL[v]}", "NA" if ctrl else B.EXPECT[v], f3(N["main"][v]) + ("<sup>e</sup>" if (N["main"][v][1] > 1 or N["main"][v][2] < 1) else ""),
                         "NA" if ctrl else f"{100*N['mv'][v][0]:.0f}", st(N["KH_typeII"][v]), st(N["KH_typeIV"][v]), st(N["D1_spatial_plus"][v]), st(N["RSR"][v])])
    foot = (f"Note. CrI = credible interval; KH = Knorr-Held space-time interaction; NA = not applicable (adjustments entered every model); RR = rate ratio; RSR = restricted spatial regression. RRs per 1 SD, principal Bayesian spatiotemporal negative binomial model (n = {N['n_rows']:,} district-years). "
            "<sup>a</sup>Expected direction recorded before modeling: + more, \u2212 fewer early-risk examinees. <sup>b</sup>Share of the 200 subset models containing the characteristic in which the 95% CrI excluded 1. "
            "<sup>c</sup>Point RRs from the type II and IV interaction models. <sup>d</sup>Point RRs from Spatial+ and RSR; intervals in Table S5. <sup>e</sup>95% CrI excludes 1.")
    return ("TABLE 2\u2014 District Characteristics and the Early Metabolic Risk Group: South Korea, 2019-2024",
            ["Characteristic", "Expected<sup>a</sup>", "RR (95% CrI)", "Credible, %<sup>b</sup>", "KH II<sup>c</sup>", "KH IV<sup>c</sup>", "Spatial+<sup>d</sup>", "RSR<sup>d</sup>"], rows, foot)
def foot_row(J, text, sz=9, ls=13):
    from docx.enum.text import WD_LINE_SPACING
    t = J.doc.tables[-1]; r = t.add_row(); m = r.cells[0].merge(r.cells[-1]); m.text = ""; p = m.paragraphs[0]
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(ls); p.paragraph_format.space_before = Pt(4)
    c = J.counting; J.counting = False; J._emit(p, text, sz); J.counting = c
def put_table(J, t, fs=9):
    c = J.counting; J.counting = False; J.table_fit(t[0], t[1], t[2], "", fs_max=fs, title_bold=True); foot_row(J, t[3]); J.counting = c

def abstract_paras(J):
    for h, t in C.ABSTRACT: J.para(f"<b>{h}.</b> {t}")
def build():
    J = TX(cite="sup"); page_numbers(J)
    J.para(f"<b>{TITLE}</b>"); J.head("Abstract", 1); abstract_paras(J)
    J.page_break(); J.counting = True
    J.head("Introduction", 1)
    for p in C.INTRO: J.para(cites(p), indent=True)
    for sec, blocks in (("Methods", C.METHODS), ("Results", C.RESULTS)):
        J.head(sec, 1)
        for x in blocks:
            J.head(x[0], 2)
            for p in x[1:]: J.para(cites(p), indent=True)
    J.head("Discussion", 1)
    for p in C.DISCUSSION:
        if isinstance(p, tuple): J.head(p[0][4:].strip(), 2); continue
        J.para(cites(p), indent=True)
    J.head("Public Health Implications", 1)
    for p in C.PHI: J.para(cites(p), indent=True)
    J.counting = False
    assert sorted(J.cites) == KEYS, (set(J.cites) ^ set(KEYS))
    J.page_break(); J.head("References", 1); J.raw = True; rl = []
    for n, k in enumerate(J.cites, 1): s = f"{n}. {ref(k)}"; rl.append(s); J.para(s)
    J.raw = False
    J.page_break(); put_table(J, table1()); J.page_break(); put_table(J, table2(), fs=8)
    J.page_break(); J.head("Figure Legends", 1)
    for k in sorted(C.FIGCAP): J.para(f"<b>FIGURE {k}\u2014</b>{C.FIGCAP[k]}")
    return J, rl

def body_words(path):   # 서론~공중보건 함의 끝(참고문헌 전), 머리말 포함
    from docx import Document
    t = "\n".join(x.text for x in Document(path).paragraphs)
    a = t.find("\nIntroduction\n"); b = t.find("\nReferences\n")
    return len(t[a:b].split())
def title_page(aw, mw):
    J = TX(cite="sup"); page_numbers(J, lines=False)
    J.para(f"<b>{TITLE}</b>")
    J.para("Seongdae Kim, PhD<sup>1,2</sup>", before=12)
    J.para(f"<sup>1</sup>{AFF1}"); J.para(f"<sup>2</sup>{AFF2}")
    J.para(f"<b>Corresponding author:</b> Seongdae Kim, PhD, {ADDRESS}. Email: {EMAIL}. ORCID: {ORCID}", before=12)
    J.para(f"<b>Article type:</b> Research Article")
    J.para(f"<b>Word count:</b> abstract {aw}; main text {th(mw)}; 2 tables; 2 figures; {len(KEYS)} references")
    J.head("Abstract", 1); abstract_paras(J)
    for hd, t in (("Contributors", CONTRIB), ("Acknowledgments", ACK), ("Funding", FUNDING), ("Conflicts of Interest", "The author has no conflicts of interest to disclose."),
                  ("Human Participant Protection", ETHICS), ("Data and Code Availability", f"All source data are publicly available aggregate statistics cited in the Methods. The analysis code that generates every number, table, and figure is openly available on Zenodo (https://doi.org/{ZENODO}) and GitHub ({GITHUB}) under the MIT License. The processed district-year analytic data are available from the author on reasonable request."),
                  ("Use of Generative Artificial Intelligence", AI_STATEMENT)):
        J.head(hd, 1); J.para(t)
    return J
def blind_props(p):
    from docx import Document
    d = Document(p); d.core_properties.author = ""; d.core_properties.last_modified_by = ""; d.save(p)
def to_pdf(p): subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_mspre", "--convert-to", "pdf", "--outdir", os.path.dirname(p), p], check=True, capture_output=True)

if __name__ == "__main__":
    aw = sum(len(t.split()) + len(h.split()) for h, t in C.ABSTRACT); assert aw <= 180, aw
    assert len(KEYS) <= 35, len(KEYS)
    p = os.path.join(OUT, "Manuscript.docx")
    J, rl = build(); J.doc_title = "Manuscript"; J.save(p); blind_props(p); mw = body_words(p); to_pdf(p)
    assert mw <= 3500, mw
    tp = os.path.join(OUT, "Title_Page.docx"); T = title_page(aw, mw); T.doc_title = "Title page"; T.save(tp); to_pdf(tp)
    x = zipfile.ZipFile(p).read("word/document.xml").decode() + zipfile.ZipFile(p).read("docProps/core.xml").decode()
    for bad in ("Hongik", "Seongdae", "7002340", "Korea University", "github.com", "zenodo", "kimsd", "Claude", "ChatGPT", "the author", "review board"): assert bad.lower() not in x.lower(), bad
    open(os.path.join(OUT, "wordcount.txt"), "w").write(f"body_words={mw}\nabstract_words={aw}\nrefs={len(KEYS)}\ntables=2\nfigures=2\n")
    open(os.path.join(OUT, "references.txt"), "w").write("\n".join(rl))
    print(f"body {mw} (≤3500) | abstract {aw} (≤180) | refs {len(KEYS)} (≤35)")
