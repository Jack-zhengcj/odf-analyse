#!/usr/bin/env python3
"""体检 results/*.json:必须扁平 schema、字段齐全、分值在域内。打印不合格项。"""
import json, glob, os
HERE = os.path.dirname(os.path.abspath(__file__))
REQ = ["id","name","mode","src","A","B","C","D","E","F","kill","tech_moat","archetype","one_liner","key_data","sources"]
MAXS = {"A":20,"B":20,"C":15,"D":15,"E":10,"F":20}
bad = 0
for f in sorted(glob.glob(os.path.join(HERE, "results", "*.json"))):
    if os.path.basename(f).startswith("_"): continue
    name = os.path.basename(f)
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        print(f"❌ {name}: JSON坏 {e}"); bad += 1; continue
    miss = [k for k in REQ if k not in d]
    if "scores" in d or "data" in d:
        print(f"❌ {name}: 用了嵌套 scores/data,必须扁平顶层 A..F/key_data"); bad += 1
    if miss:
        print(f"❌ {name}: 缺字段 {miss}"); bad += 1
    for k,mx in MAXS.items():
        v = d.get(k)
        if isinstance(v,(int,float)) and not (0 <= v <= mx):
            print(f"❌ {name}: {k}={v} 超域 0-{mx}"); bad += 1
    if d.get("mode") == "drug" and d.get("G") is None:
        print(f"⚠️ {name}: drug 但 G 未填(商业价值)"); bad += 1
print(f"\n{'✅ 全部合格' if bad==0 else f'共 {bad} 处问题待修'}  (已检 {len(glob.glob(os.path.join(HERE,'results','*.json')))} 个)")
