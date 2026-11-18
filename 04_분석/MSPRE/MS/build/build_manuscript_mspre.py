#  참고문헌 앞 Conflict of Interest·AI 사용 고지 절, CRediT, Data Availability, 표 각주 †‡§¶(*는 P값 전용), 그림 별도 파일·범례 목록.
#  단독 저자·홍익대 단독 소속. AI 고지 = 번역·영어 첨삭만. 제외 심사자·추천 심사자는 포털에서만.
import os, re, json, subprocess
from docx.oxml.ns import qn
from docx.shared import Pt
from docx.enum.text import WD_LINE_SPACING
from jkms_engine import JKMS
import content_mspre as C
import pandas as pd, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out"); os.makedirs(OUT, exist_ok=True)
AN = os.path.normpath(os.path.join(MS, "..")); ROOT = os.path.normpath(os.path.join(AN, "..", ".."))
N = C.N; REFS = json.load(open(os.path.join(HERE, "refs_mspre.json"), encoding="utf-8"))
rdf = lambda f, d: open(os.path.join(OUT, f)).read().strip() if os.path.exists(os.path.join(OUT, f)) else d
ZENODO = rdf("zenodo_doi.txt", "10.5281/zenodo.PENDING"); GITHUB = rdf("github_url.txt", "https://github.com/PENDING")
ORCID = "0000-0002-1525-0091"; TAG = "MSPRE"
ADDR = "Department of Biohealth Convergence Open Sharing System, Hongik University, 94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea"
AI_STATEMENT = "The author used Claude (Anthropic) and ChatGPT (OpenAI) only for translation and English-language editing. The author reviewed and verified all edited text for accuracy and integrity and takes full responsibility for the content of the manuscript."
FUNDING = "This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors."
CONTRIB = "Seongdae Kim: Conceptualization, Methodology, Software, Formal analysis, Data curation, Visualization, Writing – original draft, Writing – review & editing."
COI = "The author declares no conflicts of interest."
def data_statement():
    return ("All source data are publicly available aggregate statistics from the National Health Insurance Service, the Korea Disease Control and Prevention Agency, and Statistics Korea, as cited in the Materials and Methods. "
            f"The analysis code that generates every number, table, and figure is openly available on Zenodo (https://doi.org/{ZENODO}) and GitHub ({GITHUB}) under the MIT license. The processed district-year analytic data are available from the author on reasonable request.")
# ── APA ──
JFULL = {"PloS one": "PLOS ONE", "PLoS One": "PLOS ONE", "PLoS Med": "PLOS Medicine", "Polit Sci Res Methods": "Political Science Research and Methods", "Ann Inst Stat Math": "Annals of the Institute of Statistical Mathematics",
         "Diabetes Metab Syndr": "Diabetes & Metabolic Syndrome: Clinical Research & Reviews", "Stat Comput": "Statistics and Computing", "Geogr Anal": "Geographical Analysis", "Int J Epidemiol": "International Journal of Epidemiology",
         "Health Soc Care Community": "Health & Social Care in the Community", "Stat Med": "Statistics in Medicine", "Korean J Fam Med": "Korean Journal of Family Medicine",
         "Osong Public Health Res Perspect": "Osong Public Health and Research Perspectives", "Environ Health Prev Med": "Environmental Health and Preventive Medicine", "Obes Rev": "Obesity Reviews",
         "Obes Res Clin Pract": "Obesity Research & Clinical Practice", "Sci Rep": "Scientific Reports", "Diabetes Res Clin Pract": "Diabetes Research and Clinical Practice",
         "Annu Rev Public Health": "Annual Review of Public Health", "J Am Coll Cardiol": "Journal of the American College of Cardiology", "Stat Methods Med Res": "Statistical Methods in Medical Research",
         "J R Stat Soc Series B Stat Methodol": "Journal of the Royal Statistical Society Series B: Statistical Methodology", "BMJ Open": "BMJ Open", "Stat Sci": "Statistical Science",
         "Perspect Psychol Sci": "Perspectives on Psychological Science", "Clin Nutr": "Clinical Nutrition", "Ann Intern Med": "Annals of Internal Medicine", "J Korean Med Sci": "Journal of Korean Medical Science",
         "Diabet Med": "Diabetic Medicine", "Asia-Pacific Journal of Public Health": "Asia-Pacific Journal of Public Health", "Diabetes Care": "Diabetes Care", "Circulation": "Circulation", "Biometrics": "Biometrics", "Epidemiology": "Epidemiology"}
SMALL = {"of", "and", "in", "on", "for", "the", "a", "an", "to", "with", "at", "by"}
def jfull(r):
    j0 = r["journal"]
    if j0 in JFULL: return JFULL[j0]
    j = r.get("fulljournal") or j0
    if j in JFULL: return JFULL[j]
    j = re.sub(r"\s*\(.*?\)\s*$", "", j); j = re.sub(r"\s*:\s+.*$", "", j) if " : " in j else j
    w = j.split(" "); return " ".join(x if (x.isupper() and len(x) > 1) else (x if i and x.lower() in SMALL else x[:1].upper() + x[1:]) for i, x in enumerate(w))
def apa_au(a):
    if a == "Smith SC Jr": return "Smith, S. C., Jr."
    p = a.split(" ")
    if len(p) >= 2 and p[-1].isupper() and len(p[-1]) <= 3 and not a.startswith("GBD"): return " ".join(p[:-1]) + ", " + " ".join(c + "." for c in p[-1])
    return a
def surname(a): p = a.split(" "); return a if a.startswith("GBD") or not (len(p) >= 2 and p[-1].isupper() and len(p[-1]) <= 3) else " ".join(p[:-1])
def ref_apa(k):
    r = REFS[k]
    if r["type"] == "web": return f"{r['authors']}. ({r['year']}). {r['title']}. Retrieved {r['accessed']}, from {r['url']}"
    au = [apa_au(a) for a in r["authors"]]
    a = au[0] if len(au) == 1 else (", ".join(au[:-1]) + ", & " + au[-1] if len(au) <= 7 else ", ".join(au[:6]) + ", ... " + au[-1])
    t = r["title"].rstrip("."); end = "" if t.endswith(("?", "!")) else "."
    s = f"{a} ({r['year']}). {t}{end} <i>{jfull(r)}</i>"
    if r.get("vol"): s += f", <i>{r['vol']}</i>"   # journal: 권마다 1쪽부터가 아니면 호 번호 생략
    pg = str(r.get("pages", "")).strip()
    if pg:
        if "-" in pg:
            a_, b_ = pg.split("-", 1)
            if b_.isdigit() and a_.isdigit() and len(b_) < len(a_): b_ = a_[:len(a_) - len(b_)] + b_
            s += f", {a_}\u2013{b_}"
        else: s += f", {pg}"
    return s + "." + (f" https://doi.org/{r['doi']}" if r.get("doi") else "")
def _init(a): p = a.split(" "); return " ".join(c + "." for c in p[-1]) if len(p) >= 2 and p[-1].isupper() else ""
def cite_lab(k):
    r = REFS[k]
    if r["type"] == "web": return f"{r['authors']}, {r['year']}"
    s = [surname(a) for a in r["authors"]]
    nm = s[0] if len(s) == 1 else (f"{s[0]} & {s[1]}" if len(s) == 2 else f"{s[0]} et al.")
    if s[0] in _AMBIG: nm = _init(r["authors"][0]) + " " + nm   # APA 6: 같은 성·다른 첫 저자는 이니셜로 구분
    return f"{nm}, {r['year']}"
def all_paras(): return C.INTRO + [p for h, *ps in C.METHODS + C.RESULTS + C.DISCUSSION for p in ps]
def keys_in_order():
    ks = []
    for p in all_paras():
        for g in re.findall(r"\[(@[^\]]+)\]", p):
            for k in g.split(";"):
                k = k.strip().lstrip("@")
                if k not in ks: ks.append(k)
    return ks
KEYS = keys_in_order()
_fa = {}
for _k in KEYS:
    if REFS[_k]["type"] != "web": _fa.setdefault(surname(REFS[_k]["authors"][0]), set()).add(REFS[_k]["authors"][0])
_AMBIG = {k for k, v in _fa.items() if len(v) > 1}
assert all(k in REFS for k in KEYS), [k for k in KEYS if k not in REFS]
LAB = {k: cite_lab(k) for k in KEYS}
import unicodedata as _ud
def _nk(t): return "".join(c for c in _ud.normalize("NFKD", t) if not _ud.combining(c)).lower()
def _apa_key(k):
    r = REFS[k]
    au = [(_nk(r["authors"]), "")] if r["type"] == "web" else [(_nk(surname(a)), _nk(a[len(surname(a)):].strip())) for a in r["authors"]]
    return (au, str(r["year"]))
APA_ORDER = sorted(KEYS, key=_apa_key)
dup = {}
for k in KEYS: dup.setdefault(LAB[k], []).append(k)
for lab, ks in dup.items():
    if len(ks) > 1:
        for i, k in enumerate(sorted(ks, key=APA_ORDER.index)): LAB[k] = lab + "abcdefg"[i]; REFS[k] = dict(REFS[k], year=f"{REFS[k]['year']}{'abcdefg'[i]}")
def render(t):
    def rep(m):
        ks = sorted([k.strip().lstrip("@") for k in m.group(1).split(";")], key=lambda k: APA_ORDER.index(k))
        return " (" + "; ".join(LAB[k] for k in ks) + ")"
    return re.sub(r"\)\)", ")", re.sub(r"\s*\[(@[^\]]+)\]", rep, t))
def strip(t): return re.sub(r"<[^>]+>", "", re.sub(r"\s*\[@[^\]]+\]", "", t))

class TX(JKMS):
    raw = False
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        for s_ in self.doc.sections:
            ln = s_._sectPr.find(qn("w:lnNumType"))
            if ln is not None: s_._sectPr.remove(ln)
    def head(self, text, level=1):
        p = super().head(text, level)
        if p is not None: p.paragraph_format.keep_with_next = True
        return p
    def _emit(self, p, text, sz=12, bold=False, italic=False):
        if not self.raw: text = re.sub(r"(^|[\s(;])-(?=\d)", "\\1\u2212", text); text = re.sub(r"(\d)-(\d)", "\\1\u2013\\2", text)
        return super()._emit(p, text, sz, bold, italic)

def f3(r): return f"{r[0]:.3f} ({r[1]:.3f}-{r[2]:.3f})"
def st(r): return f"{r[0]:.3f}" + ("†" if (r[1] > 1 or r[2] < 1) else "")
def table1():
    T = N["T1"]; W = ["2019-2021", "2022-2024", "2019-2024"]
    rows = [["__H__", "Outcome"],
            ["  District-years (n)"] + [f"{T[w]['n']:,}" for w in W],
            ["  Examinees (millions)"] + [f"{T[w]['exam']/1e6:.1f}" for w in W],
            ["  Caution-group examinees (millions)"] + [f"{T[w]['cases']/1e6:.1f}" for w in W],
            ["  Caution group, % of examinees"] + [f"{100*T[w]['rate']:.1f}" for w in W],
            ["  Standardized ratio, median (P10-P90)"] + [f"{T[w]['sir_med']:.3f} ({T[w]['sir_p10']:.3f}-{T[w]['sir_p90']:.3f})" for w in W]]
    for g, vs in C.GROUPS:
        rows.append(["__H__", g])
        for v in vs:
            dg = 1
            rows.append([f"  {C.LABEL[v]}, {C.UNIT[v]}"] + [f"{T[w]['cov'][v][0]:.{dg}f} ({T[w]['cov'][v][1]:.{dg}f})" for w in W])
    foot = ("Characteristics are means (SD) across district-years before standardization. Survey items are age-standardized district estimates from the Community Health Survey. "
            "P10-P90, 10th to 90th percentile of district standardized ratios for the period. SD, standard deviation.")
    return ("Table 1. Metabolic syndrome caution group and district characteristics, 2019-2024", ["Characteristic", "2019-2021", "2022-2024", "2019-2024"], rows, foot)
def table2():
    rows = []
    for g, vs in C.GROUPS:
        rows.append(["__H__", g])
        for v in vs:
            ctrl = g == "Fixed adjustments"
            rows.append([f"  {C.LABEL[v]}", "NA" if ctrl else C.EXPECT[v], f3(N["main"][v]) + ("†" if (N["main"][v][1] > 1 or N["main"][v][2] < 1) else ""),
                         "NA" if ctrl else f"{100*N['mv'][v][0]:.0f}", st(N["KH_typeII"][v]), st(N["KH_typeIV"][v]), st(N["D1_spatial_plus"][v]), st(N["RSR"][v])])
    foot = (f"Rate ratios (RRs) of caution-group examinees per 1 SD with 95% credible intervals (CrIs), principal Bayesian spatio-temporal negative binomial model (n = {N['n_rows']:,} district-years). "
            "† 95% CrI excludes 1. NA, not applicable (adjustments entered every model). "
            "‡ Expected direction recorded before modeling: + more, − fewer caution-group examinees. "
            "§ Share of the 200 multiverse models containing the characteristic in which the 95% CrI excluded 1. "
            "¶ Point RRs from the Knorr-Held type II and IV space-time interaction models, Spatial+, and restricted spatial regression (RSR); intervals in Table S5. † marks were judged from limits rounded to 3 decimals.")
    return ("Table 2. District characteristics and the metabolic syndrome caution group, 2019-2024", ["Characteristic", "Expected‡", "RR (95% CrI)", "Credible, %§", "KH II¶", "KH IV¶", "Spatial+¶", "RSR¶"], rows, foot)
def add_table(J, fn, fs):
    J.page_break(); n0 = len(J.doc.paragraphs); t = fn(); J.table_fit(t[0], t[1], t[2], t[3], fs_max=fs, title_bold=True)
    for row in J.doc.tables[-1].rows:
        for c in row.cells:
            for p in c.paragraphs:
                sz = next((r.font.size.pt for r in p.runs if r.font.size), fs); p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(round(1.25 * sz, 1))
    for p in J.doc.paragraphs[n0:]:
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(13)
        if p.text.startswith(("Characteristics are", "Rate ratios")):
            for r in p.runs: r.font.size = Pt(9.5)

def build_main():
    J = TX(cite="bracket")
    J.para(f"<b>{C.TITLE}</b>")
    J.para("Seongdae Kim", before=12); J.para(ADDR)
    J.para(f"<b>Correspondence:</b> Seongdae Kim, {ADDR}. Email: kimsd@hongik.ac.kr. ORCID: {ORCID}")
    J.para(f"<b>Running title:</b> {C.RUNNING}")
    J.head("Acknowledgments", 1); J.para(C.ACK + " " + FUNDING)
    J.page_break(); J.head("Abstract", 1)
    for h, t in C.ABSTRACT.items(): J.para(f"<b>{h}:</b> {t}")
    J.para(f"<b>Keywords:</b> {'; '.join(C.KEYWORDS)}")
    J.page_break(); J.counting = True
    J.head("Introduction", 1)
    for p in C.INTRO: J.para(render(p), indent=True)
    J.head("Materials and Methods", 1)
    for h, *ps in C.METHODS:
        J.head(h, 2)
        for p in ps: J.para(render(p), indent=True)
    J.head("Results", 1)
    for h, *ps in C.RESULTS:
        J.head(h, 2)
        for p in ps: J.para(render(p), indent=True)
    J.head("Discussion", 1)
    for h, *ps in C.DISCUSSION:
        J.head(h, 2)
        for p in ps: J.para(render(p), indent=True)
    J.head("Conclusion", 1); J.para(C.CONCLUSION, indent=True)
    J.counting = False
    for h, t in (("Author Contributions", CONTRIB), ("Data Availability Statement", data_statement()), ("Conflicts of Interest", COI), ("Use of Artificial Intelligence", AI_STATEMENT)):
        J.head(h, 1); J.raw = h.startswith("Author"); J.para(t); J.raw = False
    J.page_break(); J.head("References", 1); J.raw = True
    for k in APA_ORDER: J.para(ref_apa(k))
    J.raw = False
    add_table(J, table1, 9); add_table(J, table2, 8)
    J.page_break(); J.head("Figure Legends", 1)
    for k in sorted(C.FIGCAP): J.para(f"<b>Figure {k}.</b> {C.FIGCAP[k]}")
    return J

def to_pdf(p):
    subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_mspre", "--convert-to", "pdf", "--outdir", OUT, p], check=True, capture_output=True)
def counts():
    aw = sum(len(strip(x).split()) for x in C.ABSTRACT.values()) + len(C.ABSTRACT)
    bw = sum(len(strip(render(p)).split()) for p in C.INTRO) + sum(len(h.split()) + sum(len(strip(render(p)).split()) for p in ps) for h, *ps in C.METHODS + C.RESULTS + C.DISCUSSION) + len(C.CONCLUSION.split()) + 6
    return aw, bw

if __name__ == "__main__":
    aw, bw = counts()
    assert aw <= 250, aw; assert 2500 <= bw <= 6000, bw; assert ":" not in C.TITLE and 3 <= len(C.KEYWORDS) <= 5
    J = build_main(); mp = os.path.join(OUT, f"Manuscript_{TAG}.docx"); J.doc_title = C.TITLE; J.save(mp); to_pdf(mp)
    open(os.path.join(OUT, "wordcount_ms.txt"), "w").write(f"abstract_words={aw}\nbody_words={bw}\nrefs={len(KEYS)}\ntables=2\nfigures=2\n")
    print(f"abstract {aw} | body {bw} | refs {len(KEYS)}")
