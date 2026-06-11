#!/usr/bin/env python3
"""
ODFanalyse 商业可行性打分器（第 2 轴，叠加在 tech_moat 之上）。
确定性算出 commercial 总分 + 四象限(tech×commercial) + go 档位 + 原型。
配套 references/commercial-model.md。

用法：
  python3 score_commercial.py --M1 24 --M2 24 --M3 14 --M4 10 --M5 10 --tech 40 \
      --efficacy 弱证据 --best-format shot --redline none
  python3 score_commercial.py --json '{"M1":25,"M2":22,"M3":10,"M4":13,"M5":14,"tech":24,"efficacy":"真实证据","best_format":"powder/gummy"}'

M1 需求规模&刚性 0-25 | M2 叙事/趋势/病毒 0-25 | M3 剂型即卖点 0-20 | M4 claim&渠道 0-15 | M5 单位经济&复购 0-15
--tech    复用已评 tech_moat(/80)
--redline none|regulatory|safety  成分违法/安全红线→go 档位下压一档并标注
"""
import argparse, json, sys

MAXS = {"M1": 25, "M2": 25, "M3": 20, "M4": 15, "M5": 15}
TECH_HI, COMM_HI = 45, 60


def quadrant2(tech, comm):
    ht, hc = tech >= TECH_HI, comm >= COMM_HI
    if ht and hc: return "🟢 双高黄金（既真又好卖）"
    if not ht and hc: return "🟣 营销驱动型爆品（卖叙事不卖科学，附风险面板）"
    if ht and not hc: return "🔵 真实效力小众（科学成立但没人买）"
    return "⚫ 放弃（既不真又不好卖）"


def go_tier(comm, tech, redline):
    if comm >= 75: t = "🟢 强推" if tech >= TECH_HI else "🟣 营销驱动旗舰·可做(睁眼下注)"
    elif comm >= 60: t = "🟢🟣 推荐" if tech >= TECH_HI else "🟣 营销驱动·可做"
    elif comm >= 45: t = "🟡 边缘/有条件"
    else: t = "🔴 放弃"
    if redline and redline != "none" and comm >= 45:
        t += f" ← 被『{redline}红线』下压(成分违法/安全，需先解合规)"
    return t


def archetype2(tech, comm, efficacy):
    if tech >= TECH_HI and comm >= COMM_HI: return "双高黄金型（真护城河+大市场，立项首选）"
    if comm >= COMM_HI and tech < TECH_HI:
        if efficacy == "纯叙事": return "营销驱动型·纯叙事爆品（全靠故事，最高退款/扒皮风险）"
        if efficacy == "真实证据": return "营销驱动型·真效力错格式（效力是真的，ODF不对→换最佳剂型）"
        return "营销驱动型·弱证据故事盘（叙事强证据弱，管好claim）"
    if tech >= TECH_HI and comm < COMM_HI: return "真实效力小众型（科学成立但需求/叙事撑不起规模）"
    return "双低弃子型"


def run(s, tech, efficacy, best_format, redline):
    for k in MAXS:
        if not (0 <= s[k] <= MAXS[k]):
            print(f"⚠️ {k}={s[k]} 超出 0-{MAXS[k]}", file=sys.stderr)
    comm = sum(s[k] for k in MAXS)
    print("=" * 64)
    print(f"  ▶ 技术/效力护城河 tech_moat : {tech:>3} / 80   (复用已评)")
    print(f"  ▶ 商业可行性 commercial     : {comm:>3} / 100")
    print(f"      M1需求{s['M1']:>2} M2叙事{s['M2']:>2} M3剂型{s['M3']:>2} M4claim{s['M4']:>2} M5经济{s['M5']:>2}")
    print(f"  ▶ 四象限                    : {quadrant2(tech, comm)}")
    print(f"  ▶ go 档位                   : {go_tier(comm, tech, redline)}")
    print(f"  ▶ 原型                      : {archetype2(tech, comm, efficacy)}")
    print(f"  ▶ 效力底色 efficacy_basis   : {efficacy}")
    print(f"  ▶ 最佳剂型 best_format      : {best_format}")
    print("=" * 64)
    return comm


def main():
    p = argparse.ArgumentParser()
    for k in MAXS: p.add_argument(f"--{k}", type=float)
    p.add_argument("--tech", type=float, default=0)
    p.add_argument("--efficacy", default="弱证据")
    p.add_argument("--best-format", dest="best_format", default="ODF")
    p.add_argument("--redline", default="none")
    p.add_argument("--json", default=None)
    a = p.parse_args()
    if a.json:
        d = json.loads(a.json); s = {k: float(d.get(k, 0)) for k in MAXS}
        run(s, d.get("tech", 0), d.get("efficacy", "弱证据"),
            d.get("best_format", "ODF"), d.get("redline", "none"))
    else:
        if any(getattr(a, k) is None for k in MAXS):
            p.error("需提供全部 --M1..--M5，或用 --json")
        run({k: getattr(a, k) for k in MAXS}, a.tech, a.efficacy, a.best_format, a.redline)


if __name__ == "__main__":
    main()
