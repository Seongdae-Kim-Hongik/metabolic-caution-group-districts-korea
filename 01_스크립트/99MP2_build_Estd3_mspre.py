#!/usr/bin/env python3
#  분자 = 분석용 고정 복사본 SQLite region_year(mode=ro) chk__대사_주의군_인원, 분모 = chk__대사_수검자수(대사 위험요인 판정 수검자, N135).
#   빈칸: 세종 2013-24(원표 N135 시도 머리행), 부천 2016(원표 N135 하위 구 원미·소사·오정 합). 성별 수검자도 같은 원표에서.
#  연령 프로파일: 전국 성(2)×15연령(19세 이하, 20-24 … 80-84, 85+) 수검자·주의군(N136).
#  시군구 수검자 성·연령 구조: 주민등록 인구[d,y,s,a](ST_FBDZIP=창원 2023 교정 사본) × 전국 수검률[y,s,a], (d,y,s)별 N135 성별 실측 수검자로 재척도.
#  ★판정 구성 게이트(99MP1)에서 2018 전국 수검자 500만(다른 해 1/3)·2019부터 고중성지방·낮은 HDL 판정 절반(2018 지질검사 주기 개편) → 주 2019-2024, 보조 2013-2017, 2018 제외.
#  산출: 02_패널/MSPRE_Estd3s.csv(2019-24), MSPREA_Estd3s.csv(2013-17), 04_분석/MSPRE/00_MSPRE_분자채움_261118.csv
import os, sys, sqlite3, importlib.util, unicodedata
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); AN = os.path.join(ROOT, "04_분석"); PAN = os.path.join(ROOT, "02_패널")
SRC = os.path.join(ROOT, "00_원천", "C_NHIS_검진보험")
DB = os.path.expandvars("$ST_GPT_DATASET") + "/02_체육건강_시공간_GPT버전/02_체육건강_시공간_GPT버전.sqlite"
def _load(nm, f):
    s = importlib.util.spec_from_file_location(nm, os.path.join(HERE, f)); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
m38 = _load("m38", "38_build_Estd_all.py"); cw = _load("cw", "40_region_crosswalk.py")
NFC = lambda s: unicodedata.normalize("NFC", str(s))
assert os.environ.get("ST_FBDZIP"), "ST_FBDZIP(창원 2023 교정 인구 폴더)를 지정"
YEARS = [y for y in range(2013, 2025) if y != 2018]; SEXES = ["남자", "여자"]
GROUPS = {"MSPRE": list(range(2019, 2025)), "MSPREA": list(range(2013, 2018))}
BANDS = ["0-19"] + [f"{lo}-{lo+4}" for lo in range(20, 85, 5)] + ["85+"]
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
RY = pd.read_sql('select year, fbd_region, "chk__대사_주의군_인원" as cases, "chk__대사_수검자수" as offset from region_year where year between 2013 and 2024', con); RY["fbd_region"] = RY.fbd_region.map(NFC)
base = pd.read_sql("select year, key, fbd_region from disease_panel where tag='PERIO'", con); base["fbd_region"] = base.fbd_region.map(NFC); base["key"] = base.key.map(NFC)
PKEYS = set(base.key); assert len(base) == 3206
SJ = NFC("세종시세종시"); BC = NFC("경기도부천시")

# ── 전국 성×연령 수검자·주의군(N136) ──
N = pd.read_csv(os.path.join(SRC, "DT_35007_N136_national_long.csv"), encoding="utf-8-sig")
N = N[(N.item == "인원") & N.grp.isin(["수검자수", "주의군(1~2개)"]) & N.year.isin(YEARS)]
def nb_band(a):
    a = str(a).replace(" ", "")
    if a == "19세이하": return "0-19"
    if a == "85세이상": return "85+"
    if a.endswith("세") and "~" in a: lo, hi = a[:-1].split("~"); return f"{lo}-{hi}"
    return None
N["band"] = N.age.map(nb_band); NT = N[N.age == "계"].pivot_table(index=["year", "sex"], columns="grp", values="value")
N = N[N.band.notna() & N.sex.isin(SEXES)]
EX = N[N.grp == "수검자수"].set_index(["year", "sex", "band"]).value.unstack()[BANDS]
MS = N[N.grp == "주의군(1~2개)"].set_index(["year", "sex", "band"]).value.unstack()[BANDS]
for s in SEXES:
    assert (abs(EX.xs(s, level="sex").sum(1) - NT.xs(s, level="sex")["수검자수"]) <= 1).all(), s
    assert (abs(MS.xs(s, level="sex").sum(1) - NT.xs(s, level="sex")["주의군(1~2개)"]) <= 1).all(), s
RATE = MS / EX

# ── 시군구 성×5세 주민등록 인구 ──
SIDO_HDR = {k for k in cw.SIDO_STD if len(k) >= 3 and (k.endswith("시") or k.endswith("도"))}
FIVE = [f"{lo}-{lo+4}세" for lo in range(0, 85, 5)]; OLD85 = ["85-89세", "90-94세", "95-99세", "100세 이상"]
EXTRA = {("충청북도", "청원군"): "충청북도|청주시"}; rows = []
for y in YEARS:
    d = pd.read_csv(os.path.join(m38.FBDZIP, f"{y}.csv"), encoding="cp949", dtype=str)
    d["행정구역별"] = d["행정구역별"].map(NFC).str.strip(); d["연령별"] = d["연령별"].map(NFC).str.strip()
    for s in SEXES: d[s] = pd.to_numeric(d[s].str.replace(",", ""), errors="coerce")
    sido = None; city = None; blocks = (d["행정구역별"] != d["행정구역별"].shift()).cumsum()
    for _, g in d.groupby(blocks, sort=False):
        nm = g["행정구역별"].iat[0]
        if nm == "전국": continue
        if nm in SIDO_HDR:
            sido = nm; city = None
            if nm != "세종특별자치시": continue
            g = g.drop_duplicates("연령별")
        sg = nm.split("-")[-1]
        if sg.endswith("시"): city = sg
        elif sg.endswith("구") and city is not None and cw.sido_std(sido) not in ("서울시", "부산시", "대구시", "인천시", "광주시", "대전시", "울산시"): continue
        else: city = None
        key = EXTRA.get((cw.sido_std(sido), sg), cw.make_key(sido, sg))
        if key not in PKEYS and key.endswith("군") and key[:-1] + "시" in PKEYS: key = key[:-1] + "시"
        for s in SEXES:
            a = g.set_index("연령별")[s]; tot = a.get("계", np.nan)
            if pd.isna(tot): continue
            f = a.reindex(FIVE); o = a.reindex(OLD85).fillna(0); assert f.notna().all(), (y, nm, s)
            assert abs(tot - f.sum() - o.sum()) < 0.5, (y, nm, s)
            rows.append({"year": y, "sex": s, "key": NFC(key), "tot": tot, "0-19": f["15-19세"], **{b: f[b + "세"] for b in BANDS[1:-1]}, "85+": o.sum()})
G = pd.DataFrame(rows).groupby(["year", "key", "sex"], as_index=False)[["tot"] + BANDS].sum()
NATPOP = G.groupby(["year", "sex"])[BANDS].sum(); UPT = EX / NATPOP
cwk = NFC(base[base.fbd_region == NFC("경상남도창원시")].key.iat[0]); print("[99MP2] 창원 2023 인구", G[(G.key == cwk) & (G.year == 2023)].tot.sum(), "(정답 1,009,038)")

# ── 원표 N135 직접 읽기: 시군구 성별 수검자·주의군(시도 머리행=세종, 부천 2016 하위 구 합) ──
R = pd.read_csv(os.path.join(SRC, "DT_35007_N135.csv"), encoding="utf-8-sig", dtype=str)
R = R[(R.ITM_NM == "인원") & R.C3_NM.isin(["수검자수", "주의군(1~2개)"]) & R.C2_NM.isin(["남자", "여자", "합계"])].copy()
R["year"] = R.PRD_DE.astype(int); R["DT"] = pd.to_numeric(R.DT, errors="coerce"); R = R[R.year.isin(YEARS)]
def pick(mask): return R[mask].pivot_table(index="year", columns=["C3_NM", "C2_NM"], values="DT", aggfunc="sum")
SJR = pick(R.C1_NM.str.contains("세종"))
BCR = pick(R.C1_NM.isin(["부천시원미구", "부천시소사구", "부천시오정구"]) & (R.year == 2016))
# 시군구 일반 칸 성별: 기존 long 정리본(50 매핑 규칙) — 99S2와 같은 경로
m50 = _load("m50", "50_build_master_panel.py")
L = pd.read_csv(os.path.join(PAN, "NHIS검진_시군구_연도_long.csv"), usecols=["year", "sido", "sigungu", "level", "sex", "category", "value", "tbl_id", "measure"], engine="pyarrow")
L = L[(L.tbl_id == "DT_35007_N135") & (L.level == "시군구") & (L.measure == "인원") & L.category.isin(["수검자수", "주의군(1~2개)"]) & L.year.isin(YEARS)].copy()
pairs = L[["sido", "sigungu"]].drop_duplicates(); mp = {(a, b): m50.map_region(a, b, PKEYS) for a, b in zip(pairs.sido, pairs.sigungu)}
L["key"] = [mp[(a, b)]["key"] for a, b in zip(L.sido, L.sigungu)]; L["role"] = [mp[(a, b)]["role"] for a, b in zip(L.sido, L.sigungu)]
L = L[L.key.notna()]; L["key"] = L.key.map(NFC); hasprim = L[L.role == "primary"].groupby(["key", "year"]).size().index
L = L[~((L.role == "sub") & L.set_index(["key", "year"]).index.isin(hasprim))]
SX = L.pivot_table(index=["year", "key"], columns=["category", "sex"], values="value", aggfunc="sum")
SJK = NFC(base[base.fbd_region == SJ].key.iat[0]); BCK = NFC(base[base.fbd_region == BC].key.iat[0])
FILL = []
for (yy, kk, src) in [(y, SJK, SJR.loc[y]) for y in YEARS] + [(2016, BCK, BCR.loc[2016])]:
    for c in ["수검자수", "주의군(1~2개)"]:
        for s in ["남자", "여자", "합계"]:
            SX.loc[(yy, kk), (c, s)] = src[(c, s)]
    FILL.append({"year": yy, "fbd_region": SJ if kk == SJK else BC, "source": "N135 시도 머리행(세종)" if kk == SJK else "N135 하위 구 원미·소사·오정 합(2016)",
                 "examinees": src[("수검자수", "합계")], "cases": src[("주의군(1~2개)", "합계")]})
SX = SX.sort_index()

P = base[base.year.isin(YEARS)].merge(RY, on=["year", "fbd_region"], how="left", validate="one_to_one").reset_index(drop=True)
F = pd.DataFrame(FILL); n_sql_miss = int(P.cases.isna().sum())
for r in FILL:
    m = (P.year == r["year"]) & (P.fbd_region == r["fbd_region"]); assert m.sum() == 1
    if pd.isna(P.loc[m, "cases"]).all(): P.loc[m, "cases"] = r["cases"]; P.loc[m, "offset"] = r["examinees"]
    else: assert abs(P.loc[m, "cases"].iat[0] - r["cases"]) <= 2, r
assert P.cases.notna().all() and P.offset.notna().all(), P[P.cases.isna()]
print(f"[99MP2] SQLite 빈칸 {n_sql_miss}칸 → 원표로 채움 {len(FILL)}칸(세종 {len(YEARS)} + 부천 2016)")
# 성별 합 = 합계 검산(모든 칸)
k = pd.MultiIndex.from_frame(P[["year", "key"]]); S = SX.reindex(k); assert S[[("수검자수", "남자"), ("수검자수", "여자")]].notna().all().all()
d_off = (S[("수검자수", "남자")] + S[("수검자수", "여자")]).values - P.offset.values
d_cas = (S[("주의군(1~2개)", "남자")] + S[("주의군(1~2개)", "여자")]).values - P.cases.values
print(f"[99MP2] 성별 합-합계 최대차 수검자 {np.abs(d_off).max():.0f} · 주의군 {np.abs(d_cas).max():.0f}"); assert np.abs(d_off).max() <= 2 and np.abs(d_cas).max() <= 2
# 시군구 합 / 전국 계 대조
nat = NT.xs("합계", level="sex") if "합계" in NT.index.get_level_values("sex") else None
chk = P.groupby("year")[["cases", "offset"]].sum()
if nat is not None: chk["cases/전국"] = chk.cases / nat["주의군(1~2개)"]; chk["offset/전국"] = chk.offset / nat["수검자수"]
print(chk.round(4).to_string())

e = np.zeros(len(P)); EXA = None
for s in SEXES:
    X = P[["year", "key"]].merge(G[G.sex == s], on=["year", "key"], how="left", validate="one_to_one"); assert X.tot.notna().all(), X[X.tot.isna()][["year", "key"]]
    raw = X[BANDS].values * UPT.xs(s, level="sex").loc[X.year.values].values
    exam = raw * (S[("수검자수", s)].values / raw.sum(1))[:, None]
    e += (exam * RATE.xs(s, level="sex").loc[X.year.values].values).sum(1); EXA = exam if EXA is None else EXA + exam
RATE_A = MS.groupby(level="year").sum() / EX.groupby(level="year").sum(); e_age = (EXA * RATE_A.loc[P.year.values].values).sum(1)
ep = np.zeros(len(P))
for s in SEXES:
    X = P[["year", "key"]].merge(G[G.sex == s], on=["year", "key"], how="left", validate="one_to_one")
    ep += (X[BANDS].values * (MS.xs(s, level="sex") / NATPOP.xs(s, level="sex")).loc[X.year.values].values).sum(1)
cs = P.groupby("year").cases.transform("sum").values
rs = lambda v: v * cs / pd.Series(v, index=P.index).groupby(P.year).transform("sum").values
P["E_std"] = rs(e); P["E_std_age"] = rs(e_age); P["E_pop"] = rs(ep)
P["E_crude"] = P.offset * P.year.map(P.groupby("year").cases.sum() / P.groupby("year").offset.sum())
assert np.allclose(P.groupby("year").E_std.sum(), P.groupby("year").cases.sum()) and (P.E_std > 0).all()
P["SIR"] = P.cases / P.E_std
for T, yrs in GROUPS.items():
    o = P[P.year.isin(yrs)][["year", "fbd_region", "offset", "cases", "E_std", "E_std_age", "E_pop", "E_crude", "SIR"]]
    assert len(o) == 229 * len(yrs) and o.fbd_region.nunique() == 229
    o.to_csv(os.path.join(PAN, f"{T}_Estd3s.csv"), index=False, encoding="utf-8-sig")
    p90 = o.groupby("fbd_region").apply(lambda d: d.cases.sum() / d.E_std.sum(), include_groups=False)
    print(f"[99MP2] {T} {yrs[0]}-{yrs[-1]}: 행 {len(o)} · 합 {o.cases.sum():,.0f} · 지역 SIR P10 {p90.quantile(.1):.3f} P90 {p90.quantile(.9):.3f} P90/P10 {p90.quantile(.9)/p90.quantile(.1):.3f}"
          f" · Spearman(std, pop) {o.SIR.corr(o.cases/o.E_pop, method='spearman'):.3f} · (std, crude) {o.SIR.corr(o.cases/o.E_crude, method='spearman'):.3f}")
os.makedirs(os.path.join(AN, "MSPRE"), exist_ok=True); F.to_csv(os.path.join(AN, "MSPRE", "00_MSPRE_분자채움_261118.csv"), index=False, encoding="utf-8-sig")
