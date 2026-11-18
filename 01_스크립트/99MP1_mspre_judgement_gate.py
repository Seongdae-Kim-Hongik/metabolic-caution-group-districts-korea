#!/usr/bin/env python3
#  ① 전국 연도별: 수검자, 0개·1개·2개·주의군·3~5개 비율, 성분 5종(복부비만·높은 혈압·높은 혈당·고중성지방·낮은 HDL) 양성률(N136·N139)
#  ② 시도 연도별: 주의군 비율과 성분 양성률(N135·N138 시도 행)
#  ③ 시군구: 2017→2019 성분 양성률 변화의 지역 간 이질성, 보조(2013-17)·주(2019-24) 기간 SIR 순위 상관
#  산출: 04_분석/MSPRE/gate/MSPRE_gate_national.csv·_sido.csv·_district_shift.csv, 00_MSPRE_판정구성게이트_261118.md
import os, sqlite3, unicodedata
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); SRC = os.path.join(ROOT, "00_원천", "C_NHIS_검진보험"); PAN = os.path.join(ROOT, "02_패널")
OUT = os.path.join(ROOT, "04_분석", "MSPRE", "gate"); os.makedirs(OUT, exist_ok=True)
DB = os.path.expandvars("$ST_GPT_DATASET") + "/02_체육건강_시공간_GPT버전/02_체육건강_시공간_GPT버전.sqlite"
NFC = lambda s: unicodedata.normalize("NFC", str(s))
# ① 전국
a = pd.read_csv(os.path.join(SRC, "DT_35007_N136_national_long.csv"), encoding="utf-8-sig"); a = a[(a.age == "계") & (a.sex == "합계") & (a.item == "인원")].pivot_table(index="year", columns="grp", values="value")
b = pd.read_csv(os.path.join(SRC, "DT_35007_N139_national_long.csv"), encoding="utf-8-sig"); b = b[(b.age == "계") & (b.sex == "합계") & (b.item == "인원")].pivot_table(index="year", columns="grp", values="value")
NAT = pd.DataFrame({"examinees": a["수검자수"]})
NAT["n0_pct"] = 100 * (a["수검자수"] - a["합계"]) / a["수검자수"]
for c, k in [("1개", "n1_pct"), ("2개", "n2_pct"), ("주의군(1~2개)", "mspre_pct"), ("대사증후군(3~5개)", "mets_pct")]: NAT[k] = 100 * a[c] / a["수검자수"]
for c, k in [("복부비만", "waist_pct"), ("높은혈압", "bp_pct"), ("높은혈당", "glu_pct"), ("고중성지방혈증", "tg_pct"), ("낮은 HDL 콜레스테롤 혈증", "hdl_pct")]: NAT[k] = 100 * b[c] / b["수검자수"]
NAT["examinees_ratio_vs_prev"] = NAT.examinees / NAT.examinees.shift(); NAT = NAT.round(3); NAT.to_csv(os.path.join(OUT, "MSPRE_gate_national.csv"), encoding="utf-8-sig")
# ② 시도
def sido(tb, cats):
    R = pd.read_csv(os.path.join(SRC, f"{tb}.csv"), encoding="utf-8-sig", dtype=str); R = R[(R.ITM_NM == "인원") & (R.C2_NM == "합계")]
    R["DT"] = pd.to_numeric(R.DT, errors="coerce"); R["year"] = R.PRD_DE.astype(int)
    # 시도 머리행 = C1 코드 길이 최소(시도) — C1_NM에 시도명만 있는 행
    lv = R.C1.str.len(); R = R[lv == lv.min()]
    return R.pivot_table(index=["C1_NM", "year"], columns="C3_NM", values="DT", aggfunc="sum")
S1 = sido("DT_35007_N135", None); S2 = sido("DT_35007_N138", None)
SD = pd.DataFrame({"mspre_pct": 100 * S1["주의군(1~2개)"] / S1["수검자수"], "mets_pct": 100 * S1["대사증후군(3~5개)"] / S1["수검자수"]})
for c in S2.columns:
    if c != "수검자수": SD[c + "_pct"] = 100 * S2[c] / S2["수검자수"]
SD = SD.round(2); SD.to_csv(os.path.join(OUT, "MSPRE_gate_sido.csv"), encoding="utf-8-sig")
# ③ 시군구(분석용 복사본 SQLite 성분 비율)
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cols = ["chk__대사_수검자수", "chk__대사_복부비만_인원", "chk__대사_높은혈압_인원", "chk__대사_높은혈당_인원", "chk__대사_고중성지방_인원", "chk__대사_낮은HDL_인원", "chk__대사_주의군_인원", "chk__대사_대사증후군_인원"]
D = pd.read_sql("select year, fbd_region, " + ", ".join(f'"{c}"' for c in cols) + " from region_year where year in (2017, 2019)", con); D["fbd_region"] = D.fbd_region.map(NFC)
for c in cols[1:]: D[c.replace("chk__대사_", "").replace("_인원", "") + "_pct"] = 100 * D[c] / D["chk__대사_수검자수"]
pc = [c for c in D.columns if c.endswith("_pct")]
W = D.pivot_table(index="fbd_region", columns="year", values=pc)
SH = pd.DataFrame({c: W[(c, 2019)] / W[(c, 2017)] for c in pc}).dropna()
desc = SH.describe(percentiles=[.1, .5, .9]).T.round(3); desc["cv"] = (SH.std() / SH.mean()).round(3)
SH.round(4).to_csv(os.path.join(OUT, "MSPRE_gate_district_shift.csv"), encoding="utf-8-sig")
A = pd.read_csv(os.path.join(PAN, "MSPREA_Estd3s.csv")); M = pd.read_csv(os.path.join(PAN, "MSPRE_Estd3s.csv"))
sa = A.groupby("fbd_region").apply(lambda d: d.cases.sum() / d.E_std.sum(), include_groups=False); sm = M.groupby("fbd_region").apply(lambda d: d.cases.sum() / d.E_std.sum(), include_groups=False)
rho = sa.corr(sm, method="spearman")
y17 = A[A.year == 2017].set_index("fbd_region").SIR; y19 = M[M.year == 2019].set_index("fbd_region").SIR; y20 = M[M.year == 2020].set_index("fbd_region").SIR; y16 = A[A.year == 2016].set_index("fbd_region").SIR
r1719 = y17.corr(y19, method="spearman"); r1617 = y16.corr(y17, method="spearman"); r1920 = y19.corr(y20, method="spearman")
# 2017→2019 주의군 SIR 변화와 지질 성분 변화 비율의 상관(지역별 지질검사 공백이 판정을 옮겼는지)
dl = np.log(y19 / y17).rename("dlogSIR"); J = SH.join(dl, how="inner")
cor_shift = {c: round(J[c].corr(J.dlogSIR, method="spearman"), 3) for c in pc}
md = f"""# MSPRE 판정 구성 대조 게이트 (2026-11-18)

결론: **2018은 제외하고, 주분석 2019–2024, 보조 2013–2017로 나눈다.** 주의군(1~2개) 전국 비율은 47–49%로 평탄하지만, 그 안의 성분 구성은 2019에 바뀌었다. 고중성지방·낮은 HDL 양성률이 2017 {NAT.loc[2017,'tg_pct']:.1f}%·{NAT.loc[2017,'hdl_pct']:.1f}% → 2019 {NAT.loc[2019,'tg_pct']:.1f}%·{NAT.loc[2019,'hdl_pct']:.1f}%로 절반이 됐다(같은 기간 혈압·혈당·복부비만은 ±3%p). 원인은 2018 지질검사 주기 개편(20세 이상 2년마다 → 남 24세·여 40세 이상 4년마다)으로, 그해 지질을 재지 않은 수검자는 지질 2성분이 '해당 없음'으로 세어진다. 그 결과 0개 {NAT.loc[2017,'n0_pct']:.1f}→{NAT.loc[2019,'n0_pct']:.1f}%, 3~5개 {NAT.loc[2017,'mets_pct']:.1f}→{NAT.loc[2019,'mets_pct']:.1f}%로 옮겼고, 주의군은 들고 나는 몫이 상쇄돼 {NAT.loc[2017,'mspre_pct']:.1f}→{NAT.loc[2019,'mspre_pct']:.1f}%였다.
2018 표는 전국 수검자 {NAT.loc[2018,'examinees']:,.0f}명으로 앞뒤 해의 약 1/3이고(앞해 대비 {NAT.loc[2018,'examinees_ratio_vs_prev']:.2f}배), 성분 양성률이 모두 높다(지질 측정자만 담긴 것으로 보임). 제외한다.

## ① 전국 연도별(N136·N139, %)
{NAT.to_markdown()}

## ② 시도 — 주의군 비율의 시도 간 범위(연도별 최소~최대, %)
{SD.groupby('year').mspre_pct.agg(['min','max']).round(1).T.to_markdown()}

## ③ 시군구 — 2017→2019 성분 양성률 비(2019/2017)의 지역 간 분포
{desc.to_markdown()}

- 주의군 연도 SIR 순위 상관: 2016–17 ρ = {r1617:.3f}, **2017–19 ρ = {r1719:.3f}**(단절을 가로지름), 2019–20 ρ = {r1920:.3f}.
- 기간 합 SIR 순위 상관: 보조 2013–17 대 주 2019–24 ρ = {rho:.3f}.
- 2017→2019 주의군 log SIR 변화와 성분 비의 Spearman ρ: {cor_shift}.
- 해석: 지질 2성분 비(2019/2017)는 지역마다 다르다(위 표 P10–P90). 단절을 가로지르는 비교·추세는 하지 않고, 기간을 나눠 각 기간 안에서 그해 전국 성·연령 율로 기대값을 만든다(추정 대상 = 그해 전국 대비 상대 위험).

## 방법 절에 넣을 문장(원고용 요지)
- 주의군 = 국가건강검진 대사증후군 위험요인 5종(허리둘레 남 ≥90·여 ≥85 cm, 혈압 ≥130/85 mmHg 또는 치료, 공복혈당 ≥100 mg/dL 또는 치료, 중성지방 ≥150 mg/dL, HDL 남 <40·여 <50 mg/dL) 중 1~2개 보유자; 분모 = 그해 대사 위험요인 판정 수검자(N135). 판정 기준 원문은 문헌 단계에서 국민건강보험공단 건강검진통계연보 용어 정의로 확인한다.
- 2018 지질검사 주기 개편 → 2019부터 지질 성분 양성률 절반; 2018 표는 수검자 규모 이상 → 제외. 주분석 2019–24(6년), 보조 2013–17(5년).
- 수검자 조건부 유병(검진을 받은 사람 중 주의군 비율)이다. 수검 선택은 E_pop(주민 인구 분모) 민감도로 본다.
"""
open(os.path.join(ROOT, "04_분석", "MSPRE", "00_MSPRE_판정구성게이트_261118.md"), "w").write(md)
print(md)
