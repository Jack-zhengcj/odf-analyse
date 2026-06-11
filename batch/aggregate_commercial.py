#!/usr/bin/env python3
"""
双轴汇总：技术/效力护城河(tech_moat /80) × 商业可行性(commercial /100) → REPORT_COMMERCIAL.md
只覆盖补剂(药品走 G 轴)。四象限：技术高线 45、商业高线 60。
"""
import json, glob, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
TECH_HI, COMM_HI = 45, 60

rows = []
for f in glob.glob(os.path.join(RES, "*.json")):
    if os.path.basename(f).startswith("_"):
        continue
    try:
        rows.append(json.load(open(f, encoding="utf-8")))
    except Exception as e:
        print("跳过坏文件", f, e)

supp = [r for r in rows if r.get("mode") == "supplement"]
scored = [r for r in supp if "commercial" in r]
pending = [r for r in supp if "commercial" not in r]
scored.sort(key=lambda r: (r.get("commercial") or 0, r.get("tech_moat") or 0), reverse=True)


def q(r):
    t, c = (r.get("tech_moat") or 0) >= TECH_HI, (r.get("commercial") or 0) >= COMM_HI
    return "gold" if (t and c) else "mkt" if (c and not t) else "niche" if (t and not c) else "drop"


def risk_str(r):
    rf = r.get("risk_flags") or []
    rl = r.get("redline", "none")
    s = " / ".join(rf) if rf else "—"
    if rl and rl != "none":
        s = f"⛔{rl} | " + s
    return s


def row_full(r):
    return (f"| {r.get('name','')} | **{r.get('commercial','?')}** | {r.get('tech_moat','?')}/80 "
            f"| {r.get('m_demand')}/{r.get('m_story')}/{r.get('m_format')}/{r.get('m_claim')}/{r.get('m_econ')} "
            f"| {r.get('go_tier','')} | {r.get('best_format','')} | {r.get('efficacy_basis','')} "
            f"| {risk_str(r)} | {r.get('commercial_one_liner','')} |")


HEAD_FULL = ("| 成分 | 商业/100 | 技术/80 | 需求/叙事/剂型/claim/经济 | go档位 | 最佳剂型 | 效力底色 | 风险面板 | 商业判词 |\n"
             "|---|---|---|---|---|---|---|---|---|")

out = []
out.append("# ODFanalyse 双轴评估报告 · 技术护城河 × 商业可行性\n")
out.append(f"> 已补商业轴的补剂 **{len(scored)}/{len(supp)}**（药品 {sum(1 for r in rows if r.get('mode')=='drug')} 个走 G 商业价值轴，见 REPORT.md）。"
           f"{'仍有 '+str(len(pending))+' 个待补。' if pending else '补剂全覆盖。'}\n")
out.append("**方法论**：技术分(tech_moat /80，复用已评)答「舌下/口溶膜科学上值不值」；商业可行性(commercial /100=需求25+叙事25+剂型20+claim15+经济15，本轮新评)答「DTC 卖不卖得动」。两轴正交——**生物利用度低≠卖不动**（谷胱甘肽口服几乎不吸收却被营销到~$1亿/年）。`efficacy_basis` 当诚实护栏。\n")

cnt = collections.Counter(q(r) for r in scored)
out.append("## 一、四象限分布（技术高线45 × 商业高线60）\n")
out.append("| 象限 | 含义 | 数量 |")
out.append("|---|---|---|")
out.append(f"| 🟢 双高黄金 | 既真又好卖，立项首选 | {cnt['gold']} |")
out.append(f"| 🟣 营销驱动型爆品 | 卖叙事不卖科学，可做但睁眼下注 | {cnt['mkt']} |")
out.append(f"| 🔵 真实效力小众 | 科学成立但需求/叙事撑不起规模 | {cnt['niche']} |")
out.append(f"| ⚫ 放弃 | 既不真又不好卖 | {cnt['drop']} |")
out.append("")

out.append("## 二、商业可行性总榜（按 commercial 降序 · 全补剂）\n")
out.append(HEAD_FULL)
out += [row_full(r) for r in scored]
out.append("")

gold = [r for r in scored if q(r) == "gold"]
out.append(f"## 三、🟢 双高黄金榜（tech≥{TECH_HI} 且 commercial≥{COMM_HI} · 最该做的 ODF 标的）\n")
out.append("> 技术护城河和商业可行性都过线：既能讲诚实的「更好吸收」claim、退款/合规风险低，又有大市场。**优先立项。**\n")
out.append(HEAD_FULL)
out += [row_full(r) for r in gold] or ["| —（暂无）| | | | | | | | |"]
out.append("")

mkt = [r for r in scored if q(r) == "mkt"]
out.append(f"## 四、🟣 营销驱动型爆品榜（commercial≥{COMM_HI} 但 tech<{TECH_HI} · 行业主战场）\n")
out.append("> **旧的纯技术模型会把这些全判死，这是最大错误。** 它们卖叙事不卖吸收，商业上成立（Esther 谷胱甘肽~$1亿即此类）。"
           "做，但必须照 `风险面板` 睁眼下注，并参考 `最佳剂型`（很多 ODF 装不下、要换粉/软糖/贴/胶囊/液体）。按效力底色分三亚型看：\n")
for basis, title in [("真实证据", "真效力·错格式（效力是真的，只是 ODF 不对 → 换最佳剂型，最稳）"),
                     ("弱证据", "弱证据·故事盘（证据弱叙事强，管好 claim）"),
                     ("纯叙事", "纯叙事·爆品（全靠故事，最高退款/扒皮风险，合规走钢丝）")]:
    sub = [r for r in mkt if r.get("efficacy_basis") == basis]
    if sub:
        out.append(f"### 4.{['真实证据','弱证据','纯叙事'].index(basis)+1} {basis} — {title}（{len(sub)}个）\n")
        out.append(HEAD_FULL)
        out += [row_full(r) for r in sub]
        out.append("")

niche = [r for r in scored if q(r) == "niche"]
out.append(f"## 五、🔵 真实效力小众榜（tech≥{TECH_HI} 但 commercial<{COMM_HI}）\n")
out.append("> 舌下/口溶膜科学成立，但需求小、没故事、教育成本高。技术党的自留地，**不是好生意**，除非找到细分叙事。\n")
out.append(HEAD_FULL)
out += [row_full(r) for r in niche] or ["| —（暂无）| | | | | | | | |"]
out.append("")

drop = [r for r in scored if q(r) == "drop"]
out.append(f"## 六、⚫ 放弃榜（双低）\n")
out.append("> 既透不过黏膜也没人买、没故事。真·放弃。\n")
out.append(HEAD_FULL)
out += [row_full(r) for r in drop] or ["| —（暂无）| | | | | | | | |"]
out.append("")

# 最佳剂型指路
fmt = collections.defaultdict(list)
for r in scored:
    fmt[r.get("best_format", "?")].append(r.get("name", ""))
out.append("## 七、最佳剂型指路（放宽到全剂型 · ODF 不是唯一答案）\n")
out.append("| 最佳剂型 | 数量 | 代表成分 |")
out.append("|---|---|---|")
for k in sorted(fmt, key=lambda k: -len(fmt[k])):
    names = "、".join(fmt[k][:10]) + ("…" if len(fmt[k]) > 10 else "")
    out.append(f"| {k} | {len(fmt[k])} | {names} |")
out.append("")

# 红线面板
redline = [r for r in scored if r.get("redline", "none") != "none"]
out.append("## 八、合规/安全红线面板（下注前先解）\n")
if redline:
    out.append("| 成分 | 红线 | 商业/100 | 风险面板 | 判词 |")
    out.append("|---|---|---|---|---|")
    for r in sorted(redline, key=lambda r: -(r.get("commercial") or 0)):
        out.append(f"| {r.get('name','')} | ⛔{r.get('redline')} | {r.get('commercial')} | {risk_str(r)} | {r.get('commercial_one_liner','')} |")
else:
    out.append("（暂无标红线成分）")
out.append("")

# 速读
out.append("## 九、结论速读\n")
if gold:
    out.append("**🟢 双高黄金 Top（最该做）：** " + " · ".join(f"{r['name']}(商{r.get('commercial')}/技{r.get('tech_moat')})" for r in gold[:8]))
if mkt:
    out.append("\n**🟣 营销驱动型 Top（卖叙事、睁眼下注）：** " + " · ".join(f"{r['name']}(商{r.get('commercial')})" for r in sorted(mkt, key=lambda r:-(r.get('commercial') or 0))[:10]))
real_wrong = [r for r in mkt if r.get("efficacy_basis") == "真实证据"]
if real_wrong:
    out.append("\n**🟣 内「真效力·错格式」（效力是真的，换剂型即可，最稳的营销驱动盘）：** " + " · ".join(f"{r['name']}→{r.get('best_format')}" for r in real_wrong[:10]))
if pending:
    out.append(f"\n> ⏳ 还有 {len(pending)} 个补剂待补商业轴：" + "、".join(r.get("name", "") for r in pending[:12]) + ("…" if len(pending) > 12 else ""))

open(os.path.join(HERE, "REPORT_COMMERCIAL.md"), "w", encoding="utf-8").write("\n".join(out))
print(f"✅ REPORT_COMMERCIAL.md 生成。补剂商业轴 {len(scored)}/{len(supp)}（待补 {len(pending)}）。")
print(f"   🟢双高{cnt['gold']} · 🟣营销驱动{cnt['mkt']} · 🔵真实小众{cnt['niche']} · ⚫放弃{cnt['drop']}")
if scored:
    print("   商业Top5:", ", ".join(f"{r['name']}={r.get('commercial')}" for r in scored[:5]))
