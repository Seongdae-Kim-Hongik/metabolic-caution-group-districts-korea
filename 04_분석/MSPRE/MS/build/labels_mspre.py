# labels_mspre.py — numbers, formatting helpers and covariate labels shared by the manuscript, table and supplement builders.
import os, json
HERE = os.path.dirname(os.path.abspath(__file__)); N = json.load(open(os.path.join(HERE, "numbers_mspre.json")))
def th(x, d=0): return f"{x:,.{d}f}"
def ci(k, src="main", lab=True):
    e, lo, hi = (N[src][k] if isinstance(src, str) else src)
    return f"{e:.3f} (95% CrI {lo:.3f}-{hi:.3f})" if lab else f"{e:.3f} ({lo:.3f}-{hi:.3f})"
def tc(k, src): return ci(k, src, False)
def cs(k, src="main"):
    e, lo, hi = (N[src][k] if isinstance(src, str) else src); return f"RR {e:.3f}; 95% CrI {lo:.3f}-{hi:.3f}"
def pct(x): return f"{100 * x:.0f}%"
R = N["rate"]; HC = N["hc"]; MV = N["mv"]; GT = N["gate"]; T1 = N["T1"]["2019-2024"]["cov"]
def rng(k, srcs): v = [N[s][k][0] for s in srcs]; return f"{min(v):.3f}-{max(v):.3f}"
KHS = ("KH_typeII", "KH_typeIII", "KH_typeIV")
GH, GC = N["gi_hot_sido"], N["gi_cold_sido"]
TERT_SD = T1["tertiary"][1]
LABEL = {"nutrition_label": "Nutrition label use", "weight_control": "Weight control attempts", "stress": "Perceived stress", "depressive_mood": "Depressive mood",
         "obesity": "Self-reported obesity", "high_risk_drinking": "High-risk drinking", "smoking": "Current smoking", "tertiary": "Tertiary-educated share",
         "basic_livelihood": "Public assistance recipients", "single_household": "Single-person households", "screening_uptake": "Screening uptake",
         "urban": "Urban population share", "physicians": "Physicians", "sex_ratio": "Sex ratio", "fiscal": "Fiscal autonomy", "pop80": "Aged 80 years or older"}
UNIT = {"nutrition_label": "%", "weight_control": "%", "stress": "%", "depressive_mood": "%", "obesity": "%", "high_risk_drinking": "%", "smoking": "%", "tertiary": "%",
        "basic_livelihood": "per 100", "single_household": "%", "screening_uptake": "%", "urban": "%", "physicians": "per 1,000 residents", "sex_ratio": "men per 100 women", "fiscal": "%", "pop80": "%"}
EXPECT = {"nutrition_label": "−", "weight_control": "−", "stress": "+", "depressive_mood": "+", "obesity": "+", "high_risk_drinking": "+", "smoking": "+", "tertiary": "−",
          "basic_livelihood": "+", "single_household": "+", "screening_uptake": "−"}
GROUPS = [("Diet and weight management", ["nutrition_label", "weight_control"]), ("Psychosocial strain", ["stress", "depressive_mood"]),
          ("Metabolic risk behaviors", ["obesity", "high_risk_drinking", "smoking"]), ("Socioeconomic position and screening reach", ["tertiary", "basic_livelihood", "single_household", "screening_uptake"]),
          ("Fixed adjustments", ["urban", "physicians", "sex_ratio", "fiscal", "pop80"])]
g = GT["2017"]; h = GT["2019"]

