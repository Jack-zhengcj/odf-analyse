#!/usr/bin/env python3
"""Generate a 3-section MD from a result JSON for any ingredient missing its MD.
Hand-written MDs (already on disk) are never overwritten. Usage: python3 _genmd.py [--force id...]"""
import json, os, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
MAX = {"A": 20, "B": 20, "C": 15, "D": 15, "E": 10, "F": 20}
LABEL = {"A": "舌下吸收", "B": "生物利用度提升", "C": "快起效", "D": "载药", "E": "口感成本", "F": "市场"}
KD_LABEL = {"MW": "分子量 MW", "logP": "logP/logD", "pKa": "pKa/解离", "solubility": "水溶解度",
            "oral_BA": "口服绝对BA%", "BA_mechanism": "BA低/高的机制(首过 vs 渗透)",
            "Tmax": "Tmax/起效", "dose_mg": "有效剂量 mg", "effective_dose": "有效剂量",
            "subl_evidence": "舌下/口腔黏膜人体证据", "taste": "口感/稳定性",
            "market": "市场/竞品", "regulatory": "合规", "nature": "性质"}

force = set()
args = sys.argv[1:]
if args and args[0] == "--force":
    force = set(args[1:])

def md_for(d):
    name = d.get("name", d["id"])
    is_drug = d.get("mode") == "drug"
    ctx = "药物（口腔黏膜/舌下可行性）" if is_drug else "补剂（美国 TikTok DTC 开品）"
    L = []
    L.append("【ODFanalyse 评估：%s】  语境：%s" % (name, ctx))
    L.append("")
    L.append("## 一、查证数据（带来源）")
    L.append("")
    L.append("| 维度 | 数据 |")
    L.append("|---|---|")
    kd = d.get("key_data", {})
    for k, v in kd.items():
        lab = KD_LABEL.get(k, k)
        L.append("| %s | %s |" % (lab, str(v).replace("\n", " ")))
    L.append("")
    src = d.get("sources", [])
    L.append("**来源**：" + "；".join(str(s) for s in src))
    L.append("")
    L.append("**置信度**：%s" % d.get("confidence", ""))
    L.append("")
    L.append("## 二、六维打分")
    L.append("")
    dims = " · ".join("%s %s %s/%d" % (k, LABEL[k], d.get(k), MAX[k]) for k in ["A", "B", "C", "D", "E", "F"])
    L.append("- " + dims)
    tech = d.get("tech_moat")
    if is_drug:
        L.append("- → **技术护城河 %s/80** ｜ 药物商业价值 **G %s/20** ｜ 补剂总分：不适用（药物语境看技术分）" % (tech, d.get("G")))
    else:
        L.append("- → **技术护城河 %s/80** ｜ 商业分 F **%s/20** ｜ **补剂总分 %s/100**" % (tech, d.get("F"), d.get("supp_total")))
    L.append("- → 档位 **%s** ｜ 四象限 **%s** ｜ 原型 **%s**" % (d.get("band", ""), d.get("quadrant", ""), d.get("archetype", "")))
    kill = d.get("kill", "none")
    sell = d.get("sellable")
    tail = "- → 一票否决：**%s**" % kill
    if is_drug and sell:
        tail += " ｜ 可售性：**%s**" % sell
    L.append(tail)
    L.append("")
    L.append("## 三、产品评估")
    L.append("")
    L.append(d.get("one_liner", ""))
    L.append("")
    return "\n".join(L)

made = 0
for f in sorted(glob.glob(os.path.join(RES, "*.json"))):
    if os.path.basename(f).startswith("_"):
        continue
    i = os.path.basename(f)[:-5]
    mdp = os.path.join(RES, i + ".md")
    if os.path.exists(mdp) and i not in force:
        continue
    d = json.load(open(f, encoding="utf-8"))
    open(mdp, "w", encoding="utf-8").write(md_for(d))
    made += 1
    print("wrote", i + ".md")
print("done, generated %d md files" % made)
