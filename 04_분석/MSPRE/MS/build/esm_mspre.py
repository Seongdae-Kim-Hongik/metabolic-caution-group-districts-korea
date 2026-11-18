import os, re
import pandas as pd
from build_manuscript_mspre import TX, OUT, N, to_pdf
import content_mspre as C
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.abspath(os.path.join(HERE, "..", "..")); RS = lambda v="main": os.path.join(B, f"results_{v}")
VARS = {"nutrition_label": "ext__nutrition_label_use_rate", "weight_control": "ext__weight_control_rate", "stress": "ext__perceived_stress_rate", "depressive_mood": "ext__depressive_mood_rate",
        "obesity": "obesity_rate", "high_risk_drinking": "ext__high_risk_drinking", "smoking": "ext__smoking_rate", "tertiary": "tertiary_educated_share", "basic_livelihood": "basic_livelihood_rate",
        "single_household": "ext__single_person_household_share", "screening_uptake": "ext__screening_uptake",
        "urban": "urban_population_share", "physicians": "physicians_per_1000", "sex_ratio": "sex_ratio", "fiscal": "fiscal_independence", "pop80": "pop80_share"}
en = lambda t: re.sub(r"(\d)-(\d)", "\\1\u2013\\2", t)
def f3(r): return f"{r[0]:.3f} ({r[1]:.3f}-{r[2]:.3f})" if r else "–"
def row(d, c):
    x = d[d["cov"].astype(str) == c]
    return f3([float(x.IRR.iloc[0]), float(x.lo.iloc[0]), float(x.hi.iloc[0])]) if len(x) else "–"
def put(J, t, fs=8):
    J.table_fit(t[0], t[1], t[2], t[3], fs_max=fs, title_bold=True)
def s1():
    G = pd.read_csv(os.path.join(B, "gate", "MSPRE_gate_national.csv"), encoding="utf-8-sig")
    rows = [[str(int(r.year)), f"{r.examinees/1e6:.1f}", f"{r.n0_pct:.1f}", f"{r.mspre_pct:.1f}", f"{r.mets_pct:.1f}", f"{r.waist_pct:.1f}", f"{r.bp_pct:.1f}", f"{r.glu_pct:.1f}", f"{r.tg_pct:.1f}", f"{r.hdl_pct:.1f}",
             "Excluded" if r.year == 2018 else ("Main" if r.year >= 2019 else "Auxiliary")] for r in G.itertuples()]
    return ("Table S2. National composition of metabolic syndrome components among screening examinees, 2013-2024",
            ["Year", "Examinees (millions)", "No component", "Caution group (1-2)", "Syndrome (3-5)", "Waist", "Blood pressure", "Glucose", "Triglycerides", "HDL cholesterol", "Analysis"], rows,
            en("Percentages of examinees assessed for metabolic risk components (national tables DT_35007_N136 and DT_35007_N139). The 2018 table covered about one third of the examinees of adjacent years with every component higher and was excluded. From 2019, after the 2018 change of the lipid-testing interval from every 2 years for all adults to every 4 years for men aged 24 years or older and women aged 40 years or older, the two lipid components fell by about half while the other components changed by less than 3 percentage points. HDL, high-density lipoprotein."))
def s2():
    rows = [["Panel", f"{N['n_rows']:,} district-years = {N['n_districts']} districts \u00d7 6 years (2019-2024); unique keys; no missing outcome, expected count, or covariate"],
            ["Outcome", "Examinees with one or two of five metabolic syndrome components (DT_35007_N135, caution group), by district and year"],
            ["Denominator", "Examinees assessed for metabolic risk components in the same district and year"],
            ["Source check", "1,368 overlapping district-year cells of the fixed analytic database identical to the source table; Sejong 2013-2024 filled from its provincial row; Bucheon 2016 as the sum of its three former districts; district totals equal national totals in every year"],
            ["Expected counts", "2 sexes \u00d7 15 age groups; national caution-group rates by year (DT_35007_N136); district examinee age structure approximated by resident population \u00d7 national examinee proportions, rescaled to observed examinees by sex; yearly national sum of expected = observed"],
            ["Covariate audit", "No year with all districts zero; true zeros (urban population share of Ongjin, internal medicine specialists in small counties) kept; Gunwi (transferred to Daegu in 2023) kept as one district; no national mean jump above 30%"],
            ["Imputation", "Obesity not surveyed in 2019 (filled with the 2020-2024 district mean); Sejong nutrition label use and single-person household share filled with the yearly median (6 district-years each in 2019-2024)"],
            ["Covariate sets", "Written to a file and hashed (SHA-256) before any covariate model was fitted; an earlier physical-activity set was replaced under the prespecified rule before this set was fixed"],
            ["Comparison outcomes", "Metabolic syndrome (three to five components) and untreated dyslipidemia, same districts and years"],
            ["Software", "R 4.6.0; INLA 25.10.19; one thread; principal model fitted twice with identical results"]]
    return ("Table S1. Data checks before modeling", ["Item", "Result"], [[a, en(b)] for a, b in rows], "")
S3 = [("Nutrition label use", "Diet and weight management", "Adults who read nutrition labels when buying processed food, %", "Community Health Survey", "\u2212"),
      ("Weight control attempts", "Diet and weight management", "Adults who tried to control weight in the past year, %", "Community Health Survey", "\u2212"),
      ("Perceived stress", "Psychosocial strain", "Adults reporting much or very much stress in daily life, %", "Community Health Survey", "+"),
      ("Depressive mood", "Psychosocial strain", "Adults reporting depressive mood for 2 weeks or more in the past year, %", "Community Health Survey", "+"),
      ("Self-reported obesity", "Metabolic risk behaviors", "Adults with self-reported body mass index of 25 kg/m\u00b2 or more, %", "Community Health Survey", "+"),
      ("High-risk drinking", "Metabolic risk behaviors", "Adults drinking 7 or more standard drinks (women 5) at least twice a week, %", "Community Health Survey", "+"),
      ("Current smoking", "Metabolic risk behaviors", "Adults currently smoking cigarettes, %", "Community Health Survey", "+"),
      ("Tertiary-educated share", "Socioeconomic position and screening reach", "Adults with a college or university degree, %", "Population and housing census", "\u2212"),
      ("Public assistance recipients", "Socioeconomic position and screening reach", "Basic livelihood security recipients per 100 residents", "Ministry of Health and Welfare", "+"),
      ("Single-person households", "Socioeconomic position and screening reach", "Single-person households, % of households", "Population and housing census", "+"),
      ("Screening uptake", "Socioeconomic position and screening reach", "General health screening attendees as a share of those invited, %", "National Health Insurance Service", "\u2212"),
      ("Urban population share", "Fixed adjustment", "Residents in urban zones, % of population", "Ministry of Land, Infrastructure and Transport", "-"),
      ("Physicians per 1,000", "Fixed adjustment", "Physicians working in medical institutions per 1,000 residents", "Statistics Korea", "-"),
      ("Sex ratio", "Fixed adjustment", "Men per 100 women", "Resident registration", "-"),
      ("Fiscal autonomy", "Fixed adjustment", "Fiscal autonomy ratio of the local government, %", "Ministry of the Interior and Safety", "-"),
      ("Aged 80 years or older", "Fixed adjustment", "Residents aged 80 years or older, % of population", "Resident registration", "-"),
      ("Hit-and-run crashes", "Negative control", "Hit-and-run crashes per 100 traffic crashes", "Statistics Korea", "none"),
      ("Traffic culture index", "Negative control", "Traffic culture index score", "Korea Transportation Safety Authority", "none"),
      ("Fires", "Negative control", "Fires per 10,000 residents", "National Fire Agency", "none")]
def s3():
    return ("Table S3. District characteristics, definitions, sources, and expected direction", ["Characteristic", "Group", "Definition", "Source", "Expected"], [[a, b, en(c), d, e] for a, b, c, d, e in S3],
            "Expected direction for caution-group examinees, set before modeling. Survey items are age-standardized district estimates. All characteristics were standardized to 1 SD of district-years.")
def s4():
    MV = pd.read_csv(os.path.join(RS(), "S7_multiverse_summary.csv")); MV["cov"] = MV["cov"].astype(str)
    sp = [("Principal", "S3_main_IRR.csv"), ("KH II", "S43_part_KH_typeII.csv"), ("KH III", "S43_part_KH_typeIII.csv"), ("KH IV", "S43_part_KH_typeIV.csv"), ("Spatial+", "S41_part_D1_spatial_plus.csv"), ("RSR", "S43_part_RSR.csv")]
    D = {l: pd.read_csv(os.path.join(RS(), f)) for l, f in sp}
    rows = []
    for k, c in VARS.items():
        m = MV[MV["cov"] == c]; mv = f"{100*float(m.cred_frac.iloc[0]):.0f} ({int(m.n_specs.iloc[0])})" if len(m) else "NA"
        rows.append([C.LABEL[k], mv] + [row(D[l], c) for l, _ in sp])
    w = [f"{float(D[l].WAIC.iloc[0]):,.1f}" if "WAIC" in D[l] else f"{N['waic_main']:,.1f}" for l, _ in sp]
    rows.append(["WAIC", ""] + w)
    return ("Table S5. Multiverse and spatial models, rate ratios per 1 SD (95% CrI)", ["Characteristic", "Credible, % (models)", "Principal", "KH II", "KH III", "KH IV", "Spatial+", "RSR"], rows,
            "Credible, %: share of the 200 multiverse models containing the characteristic in which the 95% CrI excluded 1 (number of such models). KH, Knorr-Held space-time interaction; the type III and IV models failed with default starting values and with an initial interaction log precision of 4, and completed with an initial value of 9. RSR, restricted spatial regression, which can understate uncertainty. The type II interaction model had the lowest WAIC; the principal model, without interaction, was fixed before fitting. CrI, credible interval; WAIC, widely applicable information criterion.")
def s5():
    d = pd.read_csv(os.path.join(RS(), "S50_resid_moran_by_spec.csv")); s8 = pd.read_csv(os.path.join(RS(), "S8_residual_moran.csv"))
    lab = {"principal": "Principal set, BYM2 (refit)", "forced_only": "Adjustments only, BYM2 (refit)", "parsimonious": "Tertiary education and adjustments, BYM2", "no_spatial": "No district effect", "iid_district": "Independent district effect",
           "icar_district": "ICAR district effect", "typeI_interaction": "Knorr-Held type I interaction"}
    rows = [[lab[r.spec], f"{r.WAIC:,.1f}" if r.WAIC == r.WAIC else "Not converged", f"{r.resid_moran_I:.3f}" if r.resid_moran_I == r.resid_moran_I else "–", f"{r.expected_I:.4f}", ("<.001" if r.p_perm < 0.001 else f"{r.p_perm:.3f}".lstrip("0")) if r.p_perm == r.p_perm else "–"] for r in d.itertuples()]
    for r in s8.itertuples():
        rows.append([{"observed_logSIR_pooled": "Observed log standardized ratio, 2019-2024", "pearson_residual_area_mean": "Principal model, district mean Pearson residual across years"}[r.quantity], "-", f"{r.moran_I:.3f}", f"{r.expected_I:.4f}", f"{r.p_perm:.3f}".lstrip("0") + (" (one-sided)" if r.alternative == "greater" else "")])
    return ("Table S6. Spatial autocorrelation of observed ratios and model residuals", ["Specification", "WAIC", "Moran's I", "Expected I", "P"], rows,
            "Permutation tests with 999 permutations on the contiguity graph with island links; two-sided unless stated. The first rows are residuals of model-specific refits in the diagnostic run, whose WAICs differ slightly from the principal fit (19,310.0); the last row is the principal fit. Residual I below its expectation with P < .05 indicates possible overfitting of local spatial structure by the district effect. ICAR, intrinsic conditional autoregressive; WAIC, widely applicable information criterion.")
def s6():
    sp = [("Province-by-year effects", "S41_part_C4_sido_year_iid.csv", "main"), ("Lag 1 year", "S41_part_E1_lag1.csv", "main"), ("Lag 2 years", "S41_part_E2_lag2.csv", "main"),
          ("Population-based E", "S3_main_IRR.csv", "sp"), ("Crude E", "S3_main_IRR.csv", "sc"), ("2013-2017", "S3_main_IRR.csv", "aux")]
    D = {l: pd.read_csv(os.path.join(RS(v), f)) for l, f, v in sp}
    rows = [[C.LABEL[k]] + [row(D[l], c) for l, _, _ in sp] for k, c in VARS.items()]
    return ("Table S4. Other sensitivity analyses, rate ratios per 1 SD (95% CrI)", ["Characteristic"] + [l for l, _, _ in sp], rows,
            f"Lagged models use 2020-2024 (lag 1) and 2021-2024 (lag 2). Population-based expected counts (E) use residents rather than examinees and remove conditioning on attendance; crude E multiplies examinees by the national rate without age-sex standardization. The 2013-2017 model used the earlier lipid-testing schedule ({N['aux_fit']['n']:,} district-years). CrI, credible interval.")
if __name__ == "__main__":
    J = TX(cite="bracket"); J.para("<b>Supporting Information</b>"); J.para(C.TITLE); J.para("Seongdae Kim")
    for t, o in ((s2(), "portrait"), (s1(), "landscape"), (s3(), "portrait"), (s6(), "landscape"), (s4(), "landscape"), (s5(), "portrait")):
        J.new_page(o); put(J, t, fs=8)
    from docx.oxml.ns import qn as _qn
    for s_ in J.doc.sections:
        ln = s_._sectPr.find(_qn("w:lnNumType"))
        if ln is not None: s_._sectPr.remove(ln)
    J.doc_title = "Supporting Information"; p = os.path.join(OUT, "Supporting_Information_MSPRE.docx"); J.save(p); to_pdf(p); print("supporting information ok")
