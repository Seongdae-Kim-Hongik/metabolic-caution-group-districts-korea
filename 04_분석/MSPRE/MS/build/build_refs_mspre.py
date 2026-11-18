import json, os, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__)); AN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ME = json.load(open(os.path.join(AN, "METS_std/MS/build/refs_mets.json"))); LI = json.load(open(os.path.join(AN, "LIPS/MS/build/refs_lips.json"))); HD = json.load(open(os.path.join(AN, "HDRK/MS/build/refs_hdrk.json")))
PM = {"kim2018educational": 29975597, "kim2005educational": 16131515, "ko2015obesity": 23687256, "lee2020exposure": 32993664, "ahn2021cumulative": 33468142, "lee2021change": 34369167}
R = {}
d = json.loads(urllib.request.urlopen("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + urllib.parse.urlencode(dict(db="pubmed", id=",".join(map(str, PM.values())), retmode="json")), timeout=60).read())["result"]
for k, p in PM.items():
    x = d[str(p)]; doi = next((a["value"] for a in x.get("articleids", []) if a["idtype"] == "doi"), "")
    au = [a["name"] for a in x.get("authors", []) if a.get("authtype") == "Author"]
    R[k] = dict(type="journal", authors=au, title=x["title"].rstrip("."), journal=x["source"], fulljournal=x.get("fulljournalname", ""), year=int(x["pubdate"][:4]), vol=x.get("volume", ""), issue=x.get("issue", ""),
                pages=x.get("pages", ""), doi=doi, pmid=str(p), verified="PubMed esummary 2026-11-19")
for k, v in ME.items(): R.setdefault(k, dict(v, verified=v.get("verified", "verified earlier reference set")))
for k in ["ord1995local", "besag1991bayesian", "gelman2014understanding", "vanderweele2017sensitivity", "morgenstern1995ecologic", "heidari2016sex", "web:yonhap2023screening"]: R[k] = dict(LI[k], verified=LI[k].get("verified", "verified earlier reference set"))
R["web:kosis2026"] = dict(HD["web:kosis2026"], title="Population and housing census (educational attainment) and basic livelihood security recipients by district, 2019-2024. Korean Statistical Information Service", accessed="November 19, 2026", verified="verified earlier reference set")
R["hodges2010adding"] = dict(HD["hodges2010adding"], verified=HD["hodges2010adding"].get("verified", "verified earlier reference set"))
for k in ("web:rcore2026", "web:mois2026population", "web:kosis2026screening", "web:yonhap2023screening"):
    if k in R: R[k] = dict(R[k], accessed="November 19, 2026")
R["web:kosis2026screening"]["title"] = "National health screening statistics: metabolic syndrome risk factors of general health screening examinees by district and sex (DT_35007_N135, DT_35007_N138) and by sex and age group (DT_35007_N136, DT_35007_N139), 2013-2024. Korean Statistical Information Service"
R["hanks2015restricted"] = dict(type="journal", authors=["Hanks EM", "Schliep EM", "Hooten MB", "Hoeting JA"], title="Restricted spatial regression in practice: geostatistical models, confounding, and robustness under model misspecification", journal="Environmetrics", fulljournal="Environmetrics", year=2015, vol="26", issue="4", pages="243-254", doi="10.1002/env.2331", verified="Crossref 2026-11-19")
R["khan2022restricted"] = dict(type="journal", authors=["Khan K", "Calder CA"], title="Restricted spatial regression methods: implications for inference", journal="Journal of the American Statistical Association", fulljournal="Journal of the American Statistical Association", year=2022, vol="117", issue="537", pages="482-494", doi="10.1080/01621459.2020.1788949", verified="Crossref 2026-11-19")
for k, r in R.items():
    if r.get("type") == "journal": assert r.get("doi") or r.get("pmid"), k
json.dump(R, open(os.path.join(HERE, "refs_mspre.json"), "w"), ensure_ascii=False, indent=1)
for k in PM: r = R[k]; print(k, "|", r["journal"], r["year"], r["vol"], r["pages"], r["doi"], "|", r["authors"][:3], "|", r["title"][:80])
print(len(R)); print(R["web:kosis2026screening"]["title"])
