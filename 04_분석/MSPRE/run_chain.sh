#!/bin/bash
#  주 2019-2024(6년, 229곳 세종 포함), 보조 2013-2017(ST_VER=aux, 주모형·세트 비교만), 2018 제외(판정 구성 게이트).
#  6년 사본: kh_constraints_mspre.R·88k_struct_kh_mspre.R·88g_sens_suite_mspre.R·86_yearly_maps_ehsa_mspre.py, 창 2개 → 82L_core_report_nwin.py.
#  CPU: rslot 7슬롯·nice 10·INLA 1스레드, 5분 부하 14 이상이면 10분씩 대기, 이 체인 동시 작업 ≤3.
set -x
export SK_RSLOTS=7
S="${ST_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"; cd "$S"; RS="$S/01_스크립트/rslot.sh"
T=MSPRE; GR="$S/04_분석/$T/graph_593.graph"; D=261118; NW=3; NMV=200
q(){ while [ "$(jobs -rp | wc -l)" -ge 3 ]; do sleep 10; done; }
lw(){ while [ "$(sysctl -n vm.loadavg | awk '{print int($3)}')" -ge 14 ]; do sleep 600; done; }
lw; ST_VER=main python3 01_스크립트/80_build_disease_panel_v.py $T > 04_분석/$T/run_80_main.log 2>&1 || exit 1
( for V in s577 s2 sc sp r2 aux; do lw; ST_VER=$V python3 01_스크립트/80_build_disease_panel_v.py $T && (cd 01_스크립트 && ST_VER=$V ST_THREADS=1 ST_MV_N=2 ST_GRAPH=$([ $V = s577 ] || echo "$GR") $RS Rscript 81_fit_inla.R $T); done > 04_분석/$T/run_sens_main.log 2>&1 ) &
export ST_VER=main ST_THREADS=1 ST_GRAPH="$GR"
lw; (cd 01_스크립트 && ST_MV_STOP=1 $RS Rscript 81_fit_inla.R $T) > 04_분석/$T/run_v2_81a.log 2>&1 || exit 1
echo STAGE_A_done
STEP=$(( (NMV + NW - 1) / NW ))
for k in $(seq 0 $((NW-1))); do a=$(( k*STEP+1 )); b=$(( (k+1)*STEP )); [ $b -gt $NMV ] && b=$NMV; lw; (cd 01_스크립트 && ST_MV_RANGE=$a-$b $RS Rscript 81_fit_inla.R $T) > 04_분석/$T/run_v2_81_mv_$a.log 2>&1 & sleep 20; done
wait
lw; (cd 01_스크립트 && $RS Rscript 81_fit_inla.R $T) > 04_분석/$T/run_v2_81b.log 2>&1 || exit 1
python3 01_스크립트/82L_core_report_nwin.py $T $D > 04_분석/$T/run_v2_82.log 2>&1
python3 01_스크립트/83_check_report.py $T $D >> 04_분석/$T/run_v2_82.log 2>&1
echo "CHAIN done"
python3 01_스크립트/87_window_grid.py $T main; (cd 01_스크립트 && TAG=$T ST_VER=main $RS Rscript 85_window_maps.R $T main); python3 01_스크립트/86_yearly_maps_ehsa_mspre.py $T main
python3 01_스크립트/88g_sens_prep.py $T main METSC,LIPTC6 || exit 1
cd 01_스크립트; export TAG=$T NCO=METSC,LIPTC6
L=../04_분석/$T
for G in 1 2 3 4 5 6; do q; lw; GROUP=$G $RS Rscript 88g_sens_suite_mspre.R > $L/run_v2_88g_$G.log 2>&1 & sleep 5; done
q; lw; $RS Rscript 88h_ppc_varpart.R > $L/run_v2_88h.log 2>&1 &
for G in nb struct kh review conf; do q; lw; $RS Rscript 88k_struct_kh_mspre.R $G > $L/run_v2_88k_$G.log 2>&1 & sleep 5; done
wait
if grep -q 'KH_typeII FAILED' $L/run_v2_88k_kh.log; then mv $L/results_main/S43_part_KH_typeII.csv $L/results_main/S43_part_KH_typeII_failed_init.csv.bak; KH_INIT=0 $RS Rscript 88k_struct_kh_mspre.R kh > $L/run_v2_88k_kh_init0.log 2>&1; fi
cd ..; TAG=$T ST_VER=main python3 01_스크립트/89g_sens_combine.py $T main > 04_분석/$T/run_v2_89g.log 2>&1
echo "ALL rc=$?"; grep -l "FAILED" 04_분석/$T/run_v2_88*.log; true
