#!/usr/bin/env python3
"""看进度:已评/总数、按mode拆分、当前榜首预览。随时跑 python3 progress.py"""
import json, glob, os
HERE = os.path.dirname(os.path.abspath(__file__))
allg = json.load(open(os.path.join(HERE, "ingredients.json"), encoding="utf-8"))
done_ids = {os.path.basename(f)[:-5] for f in glob.glob(os.path.join(HERE, "results", "*.json"))
            if not os.path.basename(f).startswith("_")}
def cnt(mode):
    a = [x for x in allg if x["mode"] == mode]
    d = [x for x in a if x["id"] in done_ids]
    return len(d), len(a)
sd, st = cnt("supplement"); dd, dt = cnt("drug")
tot_done, tot = len(done_ids), len(allg)
bar = lambda d, t: "█"*int(20*d/t) + "░"*(20-int(20*d/t))
print(f"\n  ODF 全量批跑进度  {tot_done}/{tot}  [{bar(tot_done,tot)}] {100*tot_done//tot}%")
print(f"  ├ 补剂  {sd}/{st}")
print(f"  └ 药品  {dd}/{dt}")
rows = []
for f in glob.glob(os.path.join(HERE, "results", "*.json")):
    if os.path.basename(f).startswith("_"): continue
    try: rows.append(json.load(open(f, encoding="utf-8")))
    except: pass
supp = sorted([r for r in rows if r.get("mode")=="supplement"], key=lambda r:(r.get("supp_total") or 0), reverse=True)[:8]
drug = sorted([r for r in rows if r.get("mode")=="drug"], key=lambda r:(r.get("G") or 0), reverse=True)[:8]
if supp:
    print("\n  补剂榜(实现可能性) TOP:")
    for r in supp: print(f"    {r.get('supp_total','?'):>4}  {r.get('name','')}  {r.get('archetype','')}")
if drug:
    print("\n  药品榜(商业价值G) TOP:")
    for r in drug: print(f"    G{r.get('G','?'):>3}  tech{r.get('tech_moat','?')}/80  {r.get('name','')}")
print(f"\n  剩余 {tot-tot_done} 个。全部完成后 REPORT.md 自动生成。\n")
