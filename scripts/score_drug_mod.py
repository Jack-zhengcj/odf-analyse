#!/usr/bin/env python3
"""
药品·分子修饰可行性打分器 v2（drug 第 2 轴）。确定性算 MF 总分 + G×MF 决策矩阵。
配套 references/drug-modification-model.md。

v2 调整（因为「现在有分子修饰」）：
- 调低原生分子属性(大小/溶解)的权重：MF1 障碍残余 30→20
- 调低营销味的路由价值：MF5 20→15，且改为「临床/路由必要性」而非市场卖点
- 新增 MF4 IP/FTO 自由实施 0-15（修饰路由被原研专利占住=低）
- 修饰工具箱+技术先例(MF2,30)与难度(MF3,20)相对加重——重点从「分子多烂」转向「有没有解法、多难、能不能拥有」

用法：
  python3 score_drug_mod.py --MF1 12 --MF2 26 --MF3 6 --MF4 4 --MF5 10 --G 20 \
     --barrier 渗透-大分子肽 --strategy "促渗SNAC+脂化(口服Rybelsus先例)" --difficulty NCE脂化 --fto "原研占位(Novo口服配方专利)"
  python3 score_drug_mod.py --json '{"MF1":18,"MF2":30,"MF3":20,"MF4":14,"MF5":14,"G":9,"barrier":"首过型"}'

MF1 障碍残余严重度(逆向·越可解越高) 0-20 | MF2 工具箱适配+技术先例 0-30 | MF3 修饰难度(易=高) 0-20
MF4 IP/FTO 自由实施 0-15 | MF5 修饰后路由临床价值 0-15
"""
import argparse, json, sys

MAXS = {"MF1": 20, "MF2": 30, "MF3": 20, "MF4": 15, "MF5": 15}
G_HI, MF_HI, MF_MID = 12, 60, 40


def matrix(g, mf):
    g_hi = g >= G_HI
    if mf >= MF_HI:
        return "🟢 攻坚首选（大奖且可解，立项）" if g_hi else "⚪ 能做不急（易解但奖小）"
    if mf >= MF_MID:
        return "🟡 值得长攻（难但有路，平台/长周期）" if g_hi else "⚫ 放弃偏弱"
    return "🔴 硬骨头/暂搁（大奖但近死局，等模态突破）" if g_hi else "⚫ 放弃"


def run(s, g, barrier, strategy, difficulty, fto):
    for k in MAXS:
        if not (0 <= s[k] <= MAXS[k]):
            print(f"⚠️ {k}={s[k]} 超出 0-{MAXS[k]}", file=sys.stderr)
    mf = sum(s[k] for k in MAXS)
    print("=" * 68)
    print(f"  ▶ 商业大奖 G                : {g:>3} / 20")
    print(f"  ▶ 分子修饰可行性 MF         : {mf:>3} / 100")
    print(f"      MF1障碍残余{s['MF1']:>2}/20 MF2工具+先例{s['MF2']:>2}/30 MF3难度(易高){s['MF3']:>2}/20 "
          f"MF4-IP/FTO{s['MF4']:>2}/15 MF5路由价值{s['MF5']:>2}/15")
    print(f"  ▶ 决策矩阵 G×MF             : {matrix(g, mf)}")
    print(f"  ▶ 障碍类型 barrier_type     : {barrier}")
    print(f"  ▶ 解法 mod_strategy         : {strategy}")
    print(f"  ▶ 难度档 mod_difficulty_tag : {difficulty}")
    print(f"  ▶ IP/FTO                    : {fto}")
    print("=" * 68)
    return mf


def main():
    p = argparse.ArgumentParser()
    for k in MAXS:
        p.add_argument(f"--{k}", type=float)
    p.add_argument("--G", type=float, default=0)
    p.add_argument("--barrier", default="")
    p.add_argument("--strategy", default="")
    p.add_argument("--difficulty", default="")
    p.add_argument("--fto", default="")
    p.add_argument("--json", default=None)
    a = p.parse_args()
    if a.json:
        d = json.loads(a.json)
        s = {k: float(d.get(k, 0)) for k in MAXS}
        run(s, d.get("G", 0), d.get("barrier", ""), d.get("strategy", ""), d.get("difficulty", ""), d.get("fto", ""))
    else:
        if any(getattr(a, k) is None for k in MAXS):
            p.error("需提供全部 --MF1..--MF5，或用 --json")
        run({k: getattr(a, k) for k in MAXS}, a.G, a.barrier, a.strategy, a.difficulty, a.fto)


if __name__ == "__main__":
    main()
