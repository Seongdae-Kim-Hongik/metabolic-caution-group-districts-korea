# check_citations_mspre.py — APA(저자-연도) 인용 전수검사: 본문 (Author, Year) ↔ 참고문헌 목록 1:1, 목록 순서(첫 저자 성 알파벳), 같은 저자-연도 a/b.
import re, sys, zipfile, unicodedata as ud
from xml.etree import ElementTree as ET
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
nk=lambda t: "".join(c for c in ud.normalize("NFKD",t) if not ud.combining(c)).lower()
x=ET.fromstring(zipfile.ZipFile(sys.argv[1]).read('word/document.xml'))
paras=[''.join(t.text or '' for t in p.iter(W+'t')) for p in x.iter(W+'p')]
i=paras.index('References'); j=next(k for k in range(i+1,len(paras)) if paras[k].startswith('Table 1.'))
body=' '.join(paras[:i]); refs=[p for p in paras[i+1:j] if p.strip()]
cites=set()
for g in re.findall(r'\(([^()]*?\d{4}[a-z]?)\)', body):
    for c in g.split(';'):
        m=re.match(r'^(.*?),\s*(\d{4}[a-z]?)$', c.strip())
        if m and not re.match(r'^(OR|95%|P |n |CrI)', m.group(1)): cites.add((re.sub(r'^(?:[A-Z]\. )+', '', m.group(1).strip()), m.group(2)))
ref_keys=[]; firsts=[]
for r in refs:
    m=re.match(r'^(.*?)\s\((\d{4}[a-z]?)\)\.', r); a,y=m.group(1),m.group(2)
    if re.search(r', (?:[A-Z]\.\s?-?)+', a):
        au=[x.strip() for x in re.split(r'(?<=\.),\s*(?:&\s*)?', a) if x.strip()]
        sur=[x.split(',')[0].strip() for x in au]; sur=[sur[0]] if len(au)==1 else sur
    else: sur=[a.rstrip('.')]
    lab=sur[0] if len(sur)==1 else (f'{sur[0]} & {sur[1]}' if len(sur)==2 else f'{sur[0]} et al.')
    ref_keys.append((lab,y)); firsts.append(nk(sur[0]))
miss=sorted(c for c in cites if c not in ref_keys); unused=sorted(r for r in ref_keys if r not in cites)
order_ok = firsts==sorted(firsts)
if not order_ok: print([ (a,b) for a,b in zip(firsts,sorted(firsts)) if a!=b][:5])
dups=[k for k in set(ref_keys) if ref_keys.count(k)>1]
print(f'refs {len(refs)} | distinct in-text {len(cites)} | missing-in-list {miss} | uncited {unused} | first-author order ok {order_ok} | duplicate labels {dups}')
print('PASS' if not miss and not unused and order_ok and not dups else 'FAIL')
