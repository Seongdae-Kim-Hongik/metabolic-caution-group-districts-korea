#!/usr/bin/env python3
#      LIPS 분자·분모 열을 빼고 MSPRE 분자·분모(02_패널/MSPRE_Estd3s.csv·MSPREA_Estd3s.csv, 99MP2, 세종 시도 머리행·부천 2016 하위 구 합)를 넣는다.
#  주 2019-2024(6년), 보조 2013-2017(5년), 2018 제외 — 판정 구성 게이트 04_분석/MSPRE/00_MSPRE_판정구성게이트_261118.md.
import os, json, hashlib, unicodedata
import pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); PAN = os.path.join(ROOT, "02_패널"); AN = os.path.join(ROOT, "04_분석")
POOL = "EXT_canonical_pool_MSPRE_v2_261118.csv"
import sqlite3
DB = os.path.expandvars("$ST_GPT_DATASET") + "/02_체육건강_시공간_GPT버전/02_체육건강_시공간_GPT버전.sqlite"
D = pd.read_csv(os.path.join(PAN, "EXT_canonical_pool_LIPS_261116.csv")).drop(columns=["lips_cases", "lips_examinees"]); D["fbd_region"] = D.fbd_region.map(NFC)
E = pd.concat([pd.read_csv(os.path.join(PAN, f)) for f in ["MSPREA_Estd3s.csv", "MSPRE_Estd3s.csv"]])[["year", "fbd_region", "cases", "offset"]]
E = E.rename(columns={"cases": "mspre_cases", "offset": "mspre_examinees"}); E["fbd_region"] = E.fbd_region.map(NFC)
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
SQ = {"nutrition_label_use_rate": "kchs__DT_11775_NUT_LABEL_UTIL__SR", "weight_control_rate": "kchs__DT_H_OBE_CONTROL__SR", "depressive_mood_rate": "kchs__DT_H_MENTAL_DEPRESS__SR",
      "perceived_stress_rate": "kchs__DT_H_MENTAL_STRESS__SR", "single_person_household_share": "eloc__DT_1YL21161__1인가구비율＜br＞(A÷B×100)", "regular_employee_share": "eloc__DT_1YL15004__상용직비중＜br＞(A÷B×100)"}
RY = pd.read_sql("select year, fbd_region, " + ", ".join(f'"{c}" as {k}' for k, c in SQ.items()) + " from region_year where year between 2011 and 2024", con); RY["fbd_region"] = RY.fbd_region.map(NFC)
print("SQLite main 열 연도별 비결측(2013-24):", {k: RY[RY.year >= 2013].groupby("year")[k].count().to_dict() for k in SQ})
# 결측: 시군구 안 선형 보간, 끝은 가까운 연도(기록). 세종 등 빈칸은 같은 규칙.
RY = RY.sort_values(["fbd_region", "year"]); MISS = {k: RY.loc[RY[k].isna() & RY.year.between(2013, 2024), ["fbd_region", "year"]].values.tolist() for k in SQ}
for k in SQ: RY[k] = RY.groupby("fbd_region")[k].transform(lambda s: s.interpolate(limit_area="inside").bfill().ffill())
print("main 열 보간·이월 칸(2013-24):", {k: len(v) for k, v in MISS.items()}, {k: v[:8] for k, v in MISS.items() if v})
P = D.merge(E, on=["year", "fbd_region"], how="left", validate="one_to_one").merge(RY, on=["year", "fbd_region"], how="left", validate="one_to_one"); assert len(P) == 229 * 14
yy = P[P.mspre_cases.notna()].year.unique(); assert sorted(yy) == [2013, 2014, 2015, 2016, 2017, 2019, 2020, 2021, 2022, 2023, 2024], yy
print("남은 결측(세종 영양표시·1인가구는 원표 없음 → 80 빌더가 연도 평균으로 채움, Methods 기록):", P[P.nutrition_label_use_rate.isna()].fbd_region.unique().tolist(), P[P.single_person_household_share.isna()].fbd_region.unique().tolist())
for k in ["nutrition_label_use_rate", "single_person_household_share"]:   # 세종 원표 없음 → 그해 228곳 중앙값(6+6칸 주 기간, Methods 기록)
    m = P[k].isna(); P.loc[m, k] = P.loc[m, "year"].map(P.groupby("year")[k].median()); print(f"{k} 세종 등 {int(m.sum())}칸 → 연도 중앙값")
print("결측 칸(분자 2011·2012·2018 제외):", P.drop(columns=["mspre_cases", "mspre_examinees"]).isna().sum()[lambda s: s > 0].to_dict())
P.to_csv(os.path.join(PAN, POOL), index=False, encoding="utf-8-sig")
for t2, src, f in [("METSC", "METS", "panel_METS_main.csv"), ("LIPTC6", "LIPT", "panel_LIPT_std3.csv")]:
    S = pd.read_csv(os.path.join(AN, src, f), usecols=["year", "fbd_region", "cases", "E"]); S = S[S.year.between(2019, 2024)]
    os.makedirs(os.path.join(AN, t2), exist_ok=True); S[["year", "fbd_region", "cases"]].to_csv(os.path.join(AN, t2, f"panel_{t2}.csv"), index=False)
    S.rename(columns={"E": "E_std"})[["year", "fbd_region", "E_std"]].to_csv(os.path.join(PAN, f"{t2}_Estd.csv"), index=False)
    open(os.path.join(AN, t2, "README.md"), "w").write(f"# {t2}: MSPRE 비교 결과 전용 복사본(2026-11-18). 원본 = 04_분석/{src}/{f} cases·E(2019-24). 분석 대상 아님.\n")
    print(t2, len(S), S.year.min(), S.year.max(), S.fbd_region.nunique())

FORCED = ["urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence", "pop80_share"]
NEG = ["hit_and_run_rate", "traffic_culture_index", "fires_per_10000"]
SENS = ["tertiary_educated_share", "unmet_need_rate", "living_alone_elderly"]
HYP = ["nutrition_label_use_rate", "weight_control_rate", "perceived_stress_rate", "depressive_mood_rate", "obesity_rate", "high_risk_drinking", "smoking_rate",
       "tertiary_educated_share", "basic_livelihood_rate", "single_person_household_share", "screening_uptake"]
SENS = ["unmet_need_rate", "living_alone_elderly"]
OBES = "kchs__DT_H_OBE_OBE__SR"
X = lambda L: [OBES if v == "obesity_rate" else "ext__" + v for v in L]
XK = lambda v: OBES if v == "obesity_rate" else "ext__" + v
EXPECT = {
 "nutrition_label_use_rate": "- (KCHS 영양표시 활용률: 식생활 인식·식품 선택 → 허리둘레·중성지방·혈당 위험요인 획득 지연)",
 "weight_control_rate": "± (KCHS 체중 조절 시도율: 관리 행동(−)이면서 이미 체중 문제가 있다는 표지(+))",
 "perceived_stress_rate": "+ (KCHS 스트레스 인지율: 만성 스트레스 → 복부비만·혈압·혈당; 선별 단계 단순 ρ −0.59 — 결과 전 방향은 기전대로 +)",
 "depressive_mood_rate": "+ (KCHS 우울감 경험률: 우울 → 대사 위험 축적)",
 "obesity_rate": "+ (KCHS 자가보고 비만율: 위험요인 획득. 단 0개→1~2개(+)와 1~2개→3개 이상(−)이 섞여 중간 단계 순효과는 사전에 불확실)",
 "high_risk_drinking": "+ (KCHS 고위험음주율: 혈압·중성지방; 순효과 불확실성 같음)",
 "smoking_rate": "+ (KCHS 현재흡연율: 낮은 HDL·고중성지방; 순효과 불확실성 같음)",
 "tertiary_educated_share": "- (대졸 이상 비율: 건강 문해·식생활)",
 "basic_livelihood_rate": "+ (기초생활 수급률, 2021-23 양쪽 규칙 정정: 박탈 → 대사 위험 축적)",
 "single_person_household_share": "+ (1인가구 비율: 혼밥·불규칙 식사 → 대사 위험; kwon2018eating)",
 "screening_uptake": "± (일반건강검진 수검률: 수검자 구성 선택 효과)",
}
SETS = {"S1_narrative_full": X(HYP),
        "S2_core": X(["nutrition_label_use_rate", "perceived_stress_rate", "obesity_rate", "tertiary_educated_share", "basic_livelihood_rate", "screening_uptake"]),
        "S3_diet_weight": X(["nutrition_label_use_rate", "weight_control_rate", "obesity_rate"]),
        "S4_psychosocial": X(["perceived_stress_rate", "depressive_mood_rate", "single_person_household_share"]),
        "S5_risk_behaviour": X(["obesity_rate", "high_risk_drinking", "smoking_rate"]),
        "S6_socioeconomic_detection": X(["tertiary_educated_share", "basic_livelihood_rate", "single_person_household_share", "screening_uptake"])}
pov = [{"year": 2023, "fbd_region": "경상남도창원시", "population": 1009038, "source": "KOSIS DT_1YL20651E 2023 통합창원시 계(유방암 11/4 population_final_audit)"}]
allv = ["mspre_cases", "mspre_examinees"] + FORCED + NEG + SENS + [v for v in HYP if v != "obesity_rate"]
def make(efile, years, windows, post, elabel, note_extra):
    return {
     "tag": "MSPRE", "outcome_column": "ext__mspre_cases",
     "outcome_label_en": "Examinees with one or two metabolic syndrome risk components ('caution group') among those assessed for metabolic risk at the National General Health Screening (NHIS health screening statistics DT_35007_N135, annual)",
     "disease_en": "Screen-assessed metabolic caution group (1-2 of 5 metabolic syndrome components)",
     "disease_ko": "검진 대사증후군 주의군(위험요인 1~2개 보유)",
     "offset": "ext__mspre_examinees", "exclude_years": [],
     "forced": X(FORCED), "negative_controls": X(NEG),
     "offset_E_column": "E_std", "offset_E_file": efile, "offset_E_label": elabel,
     "graph": "593-edge contact graph, ST_GRAPH=04_분석/MSPRE/graph_593.graph",
     "population_override": pov, "sensitivity_only_extra": X(SENS),
     "version": f"main early metabolic-risk narrative (metabolic caution group: diet awareness and weight control, psychosocial stress, risk behaviours, socioeconomic position, screening selection), {years[0]}-{years[1]}" + note_extra,
     "sets": SETS, "transform": {XK(v): "none" for v in FORCED + NEG + SENS + HYP},
     "expected_direction": {XK(k): v for k, v in EXPECT.items()},
     "rules": {"likelihood": "forced-only 모형 WAIC 낮은 쪽(Poisson/NB)", "set_choice": "WAIC 최소, 4 이내면 변수 적은 세트", "credible": "95% CrI 1 제외", "vif_drop": 10, "multiverse_specs": 200,
               "main_model_note": "주모형 = S1_narrative_full(가설 11 + 강제통제 5). 세트를 다시 바꾸지 않음. VIF>10 유지·보고.",
               "years": list(years), "windows": windows, "covid_post_from": post,
               "windows_note": "6년 패널(2019-24): 시간 효과 rw1 6점, 창 = 2019-21·2022-24 2개(결과 전 고정). 2018 지질검사 주기 개편 단절을 가로지르지 않는다."},
     "note": "MSPRE = 일반건강검진 대사증후군 위험요인 보유 개수별 '주의군(1~2개)'(KOSIS DT_35007_N135). 분모 = 대사 위험요인 판정 수검자(N135 수검자수). 기준 입력 = 분석용 고정 복사본 SQLite region_year chk__대사_주의군_인원·chk__대사_수검자수(빈칸 12칸: 세종 원표 시도 머리행, 부천 2016 원표 하위 구 합; 99MP2). 2018 표 수검자 500만(1/3) 제외, 2019부터 지질 2성분 양성률 절반(2018 지질검사 주기 개편) → 주 2019-24, 보조 2013-17. E = 성×15연령 간접표준화(전국 N136 율, 시군구 수검자 연령 구조는 주민등록×전국 수검률 근사·성별 실측 재척도). 수검자 조건부 유병. 겹침: LIPT ρ −0.73·CLRD 0.65·PERIO −0.64·ALLD 0.60; METS(3~5개)와 같은 표의 다른 칸.",
     "extra_columns": {"ext__" + v: [POOL, v] for v in allv}}
LAB = "sex-and-age-standardised expected caution-group cases, 2 sexes x 15 age bands (<=19, 20-24 to 80-84, 85+) (national screening rates DT_35007_N136; district examinee age structure approximated from resident population x national uptake, sex totals observed), {}"
w_main = {"W1_2019-21": [2019, 2021], "W2_2022-24": [2022, 2024]}
for ver in ["main", "s577", "s2", "sc", "sp", "r2"]:
    j = make("MSPRE_Estd3s.csv", (2019, 2024), w_main, 2020, LAB.format("2019-2024"), "")
    if ver == "s577": j["sens_note"] = "민감도: 그래프만 queen 577"
    if ver == "s2": j["sens_note"] = "민감도: 80세 이상 비율 강제통제 없음"; j["forced"] = X(FORCED[:4])
    if ver == "sc": j["sens_note"] = "민감도: 비표준화(조) E(수검자 × 전국 연도 주의군 율)"; j["offset_E_column"] = "E_crude"; j["offset_E_label"] = "crude E (examinees x national annual caution-group rate)"
    if ver == "sp": j["sens_note"] = "민감도: 주민 인구 분모 성·연령 표준화 E(수검 선택 민감도, 무조건부 유병)"; j["offset_E_column"] = "E_pop"; j["offset_E_label"] = "population-based sex-age standardised E (resident population x national caution-group per resident rate)"
    if ver == "r2": j["sens_note"] = "재현성 점검: 주 분석과 같은 사양 2회째 적합(threads 1:1)"
    json.dump(j, open(os.path.join(HERE, f"sets_MSPRE_{ver}.json"), "w"), ensure_ascii=False, indent=1)
w_aux = {"W1_2013-15": [2013, 2015], "W2_2016-17": [2016, 2017]}
j = make("MSPREA_Estd3s.csv", (2013, 2017), w_aux, 2016, LAB.format("2013-2017"), " [aux: before the 2018 lipid-testing-cycle change]")
j["rules"]["windows_note"] = "보조 기간 2013-17(2018 지질검사 주기 개편 이전). S5 COVID 단계는 해당 없음."
json.dump(j, open(os.path.join(HERE, "sets_MSPRE_aux.json"), "w"), ensure_ascii=False, indent=1)
# 해시 기록(적합 전 고정 증빙)
with open(os.path.join(HERE, "00_MSPRE_sets_hash_v2_261118.txt"), "w") as f:
    for ver in ["main", "s577", "s2", "sc", "sp", "r2", "aux"]:
        fn = f"sets_MSPRE_{ver}.json"; h = hashlib.sha256(open(os.path.join(HERE, fn), "rb").read()).hexdigest(); f.write(f"{fn}\t{h}\n"); print(fn, h[:16])
print("sets 저장: main 계열 7개")
