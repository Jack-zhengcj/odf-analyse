#!/usr/bin/env python3
"""商业叠加层的剩余清单（幂等）：列出还没有 commercial 字段的『补剂』(药品走 G 轴不叠加)，分块给 agent。"""
import json, glob, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
rows = {}
for f in glob.glob(os.path.join(RES, "*.json")):
    if os.path.basename(f).startswith("_"):
        continue
    d = json.load(open(f, encoding="utf-8"))
    rows[d["id"]] = d

supp = [d for d in rows.values() if d.get("mode") == "supplement"]
todo = [d for d in supp if "commercial" not in d]
done = [d for d in supp if "commercial" in d]
print(f"补剂 {len(supp)} | 已补商业轴 {len(done)} | 待补 {len(todo)}  (药品 {sum(1 for d in rows.values() if d.get('mode')=='drug')} 个走 G 轴,不计)")

CHUNK = int(sys.argv[1]) if len(sys.argv) > 1 else 7
todo.sort(key=lambda d: d["id"])
groups = [todo[i:i + CHUNK] for i in range(0, len(todo), CHUNK)]
print(f"分块(每块{CHUNK}): {len(groups)} 块\n")
for i, g in enumerate(groups):
    print(f"### CHUNK {i+1:02d}")
    for d in g:
        print(f"{d['id']} | {d.get('name','')} | tech {d.get('tech_moat')}/80 | kill={d.get('kill')}")
    print()
