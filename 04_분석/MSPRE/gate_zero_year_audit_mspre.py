#!/usr/bin/env python3
import os, unicodedata, numpy as np, pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s)); HERE = os.path.dirname(os.path.abspath(__file__))
P = pd.read_csv(os.path.join(HERE, "panel_MSPRE_std3.csv")); P["fbd_region"] = P.fbd_region.map(NFC)
raw = [c for c in P.columns if c.endswith("_raw")] + ["cases", "offset"]
rows = []
for c in raw:
    g = P.groupby("year")[c]; z = g.apply(lambda s: int((s == 0).sum())); na = g.apply(lambda s: int(s.isna().sum())); mu = g.mean()
    jump = (mu / mu.shift()).round(3)
    rows.append(dict(var=c, zero_cells=int((P[c] == 0).sum()), years_all_zero=[int(y) for y in z.index if z[y] == 229], zero_by_year=z[z > 0].to_dict(), na_cells=int(P[c].isna().sum()),
                     year_mean=mu.round(3).to_dict(), max_yoy_ratio=float(np.nanmax(np.abs(np.log(jump.dropna())))) if jump.notna().any() else np.nan,
                     yoy_flag=[int(y) for y in jump.index if pd.notna(jump[y]) and (jump[y] > 1.3 or jump[y] < 1 / 1.3)]))
A = pd.DataFrame(rows); A.to_csv(os.path.join(HERE, "gate_zero_year_audit_MSPRE_261118.csv"), index=False, encoding="utf-8-sig")
print(A[["var", "zero_cells", "years_all_zero", "na_cells", "yoy_flag", "zero_by_year"]].to_string())
# 군위: 2023 대구 편입 — 패널 키 하나로 연속인지
g = P[P.fbd_region.str.contains("군위")][["year", "fbd_region", "key", "cases", "offset", "population"]]; print(g.to_string())
# 일반구 시: 분자·분모는 하위 구 합(가중 불필요), 비율 공변량은 시 단위 원표(SQLite)와 대조 → gate_sqlite_crosscheck
city = ["경기도수원시", "경기도성남시", "경기도안양시", "경기도부천시", "경기도안산시", "경기도고양시", "경기도용인시", "충청북도청주시", "충청남도천안시", "전라북도전주시", "경상북도포항시", "경상남도창원시"]
print(P[P.fbd_region.isin([NFC(x) for x in city])].groupby("fbd_region")[["cases", "offset"]].agg(["min", "max"]).to_string())
