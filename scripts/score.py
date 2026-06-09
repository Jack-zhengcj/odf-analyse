#!/usr/bin/env python3
"""
ODFanalyse — 口溶膜(ODF/ODS)开品可行性确定性打分器 (v2，双轴+双语境)

设计要点(由 6 个药物对抗验证得出)：
  1. 永远分开报【技术护城河分 tech_moat = A+B+C+D+E，满分80】与【商业分】，不只给混合总分。
  2. 商业轴随语境(mode)取不同口径，与 TikTok-F 解耦，能装下"技术低但商业高"(如司美格鲁肽)。
  3. 一票否决分两类(仅语义区分，便于读者判读)：
     - 技术性否决(剂量>100mg / MW>800渗透不可能 / 口感不可掩)：本就反映在低 A/D/E，并封补剂总分。
     - 合规性否决(监管 / TikTok限流)：技术分不受影响，只封补剂总分/商业可售性。

用法：
  # 补剂语境(默认，TikTok开品)
  python3 score.py --A 16 --B 17 --C 13 --D 14 --E 8 --F 12 --kill none
  python3 score.py --A 6 --B 7 --C 9 --D 3 --E 8 --F 15 --kill dose
  # 药物语境(舌下/口溶膜可行性)；商业分用 --G 药物商业价值(0-20)
  python3 score.py --mode drug --A 20 --B 20 --C 15 --D 15 --E 8 --G 12 --sellable rx
  python3 score.py --json '{"mode":"drug","A":1,"B":2,"C":3,"D":12,"E":6,"G":20,"sellable":"rx"}'

参数：
  --mode      supplement(默认) | drug
  --A..--F    六维子分(F仅补剂语境的TikTok赛道分；药物语境可填0)
  --G         药物/战略商业价值 0-20(drug语境用；与F-TikTok解耦)
  --kill      一票否决(封补剂总分)：none|dose|tiktok|taste|permeation|regulatory|stability
  --sellable  drug语境可售性标志(仅注释，不改技术分)：otc|rx|controlled|tcm
"""
import argparse, json, sys

MAXS = {"A": 20, "B": 20, "C": 15, "D": 15, "E": 10, "F": 20}
TECH_KEYS = ["A", "B", "C", "D", "E"]                       # 技术护城河 = A+B+C+D+E (80)
CAPS = {"none": 100, "dose": 40, "tiktok": 45, "taste": 50,
        "permeation": 50, "regulatory": 45, "stability": 100}
KILL_KIND = {"none": "无", "dose": "剂量>100mg(技术性)", "tiktok": "TikTok限流(合规性)",
             "taste": "口感不可掩(技术性)", "permeation": "MW>800渗透不可能(技术性)",
             "regulatory": "监管/NDIN(合规性)", "stability": "稳定性阻断(技术性,E≤3)"}
SELL_LABEL = {"otc": "OTC可售", "rx": "处方药(不可作补剂)",
              "controlled": "管制药(合规封死)", "tcm": "中成药(草本+宣称受限)"}


def tech_band(t):   # /80
    if t >= 65: return "高技：舌下/口溶膜真值得做"
    if t >= 45: return "中技：有真实优势但带短板"
    return "低技：舌下救不动/装不下，多为噱头"


def supp_band(total):  # /100
    if total >= 80: return "🟢 强烈推荐", "双层皆高，舌下化真值钱 → 进第2层商业体检"
    if total >= 70: return "🟢🟡 推荐(补一条腿)", "一处短板被补偿；卖点切便携别押BA"
    if total >= 55: return "🟡 谨慎/有条件", "有结构性硬伤未触否决；重定位/上工艺后再评"
    if total >= 40: return "🟠 不推荐(伪需求)", "护城河不成立，成膜主要是噱头"
    return "🔴 直接Pass", "触一票否决或根基不成立"


def quadrant(tech, comm):   # tech/80, comm/20
    hi_t, hi_c = tech >= 55, (comm is not None and comm >= 12)
    if hi_t and hi_c: return "① 高技×高商 → 立项首选(如褪黑素)"
    if hi_t and not hi_c: return "② 高技×低商 → 剂型完美但变现受限(药物/管制/红海，如硝酸甘油/丁丙诺啡)"
    if not hi_t and hi_c: return "③ 低技×高商 → 该剂型不可行，但成分本身是金矿，换给药途径(如司美格鲁肽)"
    return "④ 低技×低商 → 放弃(如二甲双胍/益生菌)"


def archetype(s, mode, kill, sellable):
    tech = sum(s[k] for k in TECH_KEYS); A, B, C, D, F = s["A"], s["B"], s["C"], s["D"], s["F"]
    if mode == "drug" and sellable in ("rx", "controlled", "tcm") and tech >= 55:
        return "技术可行但合规封顶（剂型科学上该做，但管制/处方/草本，作补剂卖不了）"
    if tech <= 30 and s.get("_comm_high"):
        return "技术死局但商业重磅（分子透不过，但成分本身是金矿，走皮下/换剂型）"
    if D == 0 or kill == "dose": return "剂量否决型（有效剂量>100mg，物理装不进膜）"
    if A <= 3 and B <= 4: return "概念错配/渗透不可能型（分子根本透不过，或靶点不在血液）"
    if B <= 9 and A <= 9: return "渗透型伪需求（透不过黏膜，舌下救不动，正解换剂型）"
    if B >= 16 and A >= 14: return "真护城河型（小分子+首过型低BA+舌下成倍救回）"
    if B <= 9 and F >= 16 and C >= 12: return "赛道补腿型（BA无提升，靠急性场景+赛道补回）"
    return "（按六维形状人工判定原型）"


def run(s, mode, G, kill, sellable):
    for k in MAXS:
        if not (0 <= s[k] <= MAXS[k]):
            print(f"⚠️ {k}={s[k]} 超出 0-{MAXS[k]}", file=sys.stderr)
    tech = sum(s[k] for k in TECH_KEYS)                  # /80
    comm = G if mode == "drug" else s["F"]               # /20
    s["_comm_high"] = comm is not None and comm >= 12
    print("=" * 60)
    print(f"  语境 mode                 : {mode}")
    print(f"  ▶ 技术护城河 tech_moat    : {tech:>3} / 80   [{tech_band(tech)}]")
    print(f"      A舌下吸收{s['A']:>2} B-BA提升{s['B']:>2} C起效{s['C']:>2} D载药{s['D']:>2} E成本{s['E']:>2}")
    if mode == "supplement":
        cap = CAPS.get(kill, 100); raw = tech + s["F"]; total = min(raw, cap)
        label, meaning = supp_band(total)
        note = f" ← 被『{KILL_KIND.get(kill,kill)}』封顶({cap})" if total < raw else ""
        print(f"  ▶ 商业分(F·TikTok赛道)    : {s['F']:>3} / 20")
        print(f"  ▶ 补剂总分(经封顶)        : {total:>3} / 100{note}")
        print(f"      档位 → {label} : {meaning}")
    else:
        print(f"  ▶ 药物/战略商业价值 G     : {('%3d / 20'%G) if G is not None else ' 待评(0-20)'}  (与TikTok解耦)")
        if sellable: print(f"      可售性 → {SELL_LABEL.get(sellable, sellable)}（不影响技术分）")
        print(f"  ▶ 补剂总分                : 不适用（药物语境：看技术分判舌下可行性）")
        if kill and kill != "none":
            print(f"      技术性约束 → {KILL_KIND.get(kill,kill)}（已反映在低 A/D/E）")
    print(f"  ▶ 四象限                  : {quadrant(tech, comm)}")
    print(f"  ▶ 原型                    : {archetype(s, mode, kill, sellable)}")
    print("=" * 60)
    print("  说明：技术分高 ≠ 能赚钱。≥70(补剂)或高技(药物)须人工过第2层商业体检：")
    print("        G单位经济 / 复购LTV / 供应链CDMO / FTO自由实施权 / 安全边界 / 剂型横向对标。")


def main():
    p = argparse.ArgumentParser()
    for k in MAXS: p.add_argument(f"--{k}", type=float)
    p.add_argument("--mode", default="supplement", choices=["supplement", "drug"])
    p.add_argument("--G", type=float, default=None)
    p.add_argument("--kill", default="none")
    p.add_argument("--sellable", default=None)
    p.add_argument("--json", default=None)
    a = p.parse_args()
    if a.json:
        d = json.loads(a.json); s = {k: float(d.get(k, 0)) for k in MAXS}
        run(s, d.get("mode", "supplement"), d.get("G"), d.get("kill", "none"), d.get("sellable"))
    else:
        if any(getattr(a, k) is None for k in MAXS):
            p.error("需提供全部六维 --A..--F（药物语境 F 可填0），或用 --json")
        run({k: getattr(a, k) for k in MAXS}, a.mode, a.G, a.kill, a.sellable)


if __name__ == "__main__":
    main()
