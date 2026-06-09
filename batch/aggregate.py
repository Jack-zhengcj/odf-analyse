#!/usr/bin/env python3
"""汇总 results/*.json -> REPORT.md。补剂按 supp_total 降序;药品按 G 商业价值降序。"""
import json, glob, os

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
rows = []
for f in glob.glob(os.path.join(RES, "*.json")):
    if os.path.basename(f).startswith("_"):
        continue
    try:
        rows.append(json.load(open(f, encoding="utf-8")))
    except Exception as e:
        print("跳过坏文件", f, e)

supp = sorted([r for r in rows if r.get("mode") == "supplement"],
              key=lambda r: (r.get("supp_total") or 0, r.get("tech_moat") or 0), reverse=True)
drug = sorted([r for r in rows if r.get("mode") == "drug"],
              key=lambda r: (r.get("G") or 0, r.get("tech_moat") or 0), reverse=True)

def line(r, mode):
    if mode == "supp":
        return (f"| {r.get('name','')} | {r.get('supp_total','?')} | {r.get('tech_moat','?')}/80 "
                f"| {r.get('A')}/{r.get('B')}/{r.get('C')}/{r.get('D')}/{r.get('E')}/{r.get('F')} "
                f"| {r.get('band','')} | {r.get('archetype','')} | {r.get('one_liner','')} |")
    return (f"| {r.get('name','')} | {r.get('G','?')}/20 | {r.get('tech_moat','?')}/80 "
            f"| {r.get('quadrant','')} | {r.get('sellable','')} | {r.get('archetype','')} | {r.get('one_liner','')} |")

out = []
out.append(f"# ODFanalyse 全量评分汇总报告\n\n已评 {len(rows)} 个成分(补剂 {len(supp)} / 药品 {len(drug)})。\n")
out.append("## 一、补剂榜(按补剂总分降序 · 实现可能性从高到低)\n")
out.append("| 成分 | 总分/100 | 技术护城河 | A/B/C/D/E/F | 档位 | 原型 | 一句话 |")
out.append("|---|---|---|---|---|---|---|")
out += [line(r, "supp") for r in supp]
out.append("\n## 二、药品榜(按 G 商业价值降序 · 忽略传播/开发难度)\n")
out.append("| 药物 | 商业价值G/20 | 技术护城河 | 象限 | 可售性 | 原型 | 一句话 |")
out.append("|---|---|---|---|---|---|---|")
out += [line(r, "drug") for r in drug]
out.append("\n## 三、结论速读\n")
if supp:
    top = supp[:5]
    out.append("**补剂实现可能性 Top5:** " + " · ".join(f"{r['name']}({r.get('supp_total')})" for r in top))
if drug:
    topd = drug[:5]
    out.append("\n**药品商业价值 Top5:** " + " · ".join(f"{r['name']}(G{r.get('G')})" for r in topd))

open(os.path.join(HERE, "REPORT.md"), "w", encoding="utf-8").write("\n".join(out))
print(f"✅ REPORT.md 生成。补剂 {len(supp)} / 药品 {len(drug)}。")
if supp:
    print("补剂Top5:", ", ".join(f"{r['name']}={r.get('supp_total')}" for r in supp[:5]))
if drug:
    print("药品商业Top5:", ", ".join(f"{r['name']}=G{r.get('G')}" for r in drug[:5]))
