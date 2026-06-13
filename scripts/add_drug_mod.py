#!/usr/bin/env python3
"""
把药品分子修饰可行性(MF)字段安全合并进已存在的 batch/results/<id>.json（保留全部技术字段+G不动）。
agent 只判 5 个 MF 子分 + 4 个定性字段 + 一句话；G 用 JSON 里已评的(可 --G 覆盖)；矩阵确定性算出。

用法：
  python3 scripts/add_drug_mod.py semaglutide \
     --MF1 12 --MF2 26 --MF3 6 --MF4 4 --MF5 10 \
     --barrier 渗透-大分子肽 --strategy "促渗SNAC/C10+酶抑制+已C18脂化;口服Rybelsus先例" \
     --difficulty NCE脂化/平台 --fto "原研占位:Novo口服配方专利,需绕配方或等generic" \
     --one-liner "大奖G20但属大分子肽;修饰有路(口服已先例)、舌下难,FTO是真风险→值得长攻而非死磕。"

MF1 障碍残余(越可解越高) 0-20 | MF2 工具箱+技术先例 0-30 | MF3 难度(易=高) 0-20 | MF4 IP/FTO 0-15 | MF5 路由临床价值 0-15
"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from score_drug_mod import matrix, MAXS  # noqa

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "batch", "results")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("id")
    for k in MAXS:
        p.add_argument(f"--{k}", type=float, required=True)
    p.add_argument("--G", type=float, default=None, help="覆盖 JSON 里的 G（默认用已评 G）")
    p.add_argument("--barrier", required=True)
    p.add_argument("--strategy", required=True)
    p.add_argument("--difficulty", required=True)
    p.add_argument("--fto", required=True)
    p.add_argument("--one-liner", dest="one_liner", required=True)
    a = p.parse_args()

    path = os.path.normpath(os.path.join(RES, a.id + ".json"))
    if not os.path.exists(path):
        sys.exit(f"❌ 找不到 {path}")
    d = json.load(open(path, encoding="utf-8"))
    if d.get("mode") != "drug":
        sys.exit(f"❌ {a.id} 不是 drug，分子修饰轴只评药品")

    s = {k: getattr(a, k) for k in MAXS}
    for k, mx in MAXS.items():
        if not (0 <= s[k] <= mx):
            sys.exit(f"❌ {k}={s[k]} 超域 0-{mx}")
    g = a.G if a.G is not None else (d.get("G") or 0)
    mf = int(sum(s.values()))

    d.update({
        "mf1_barrier": int(s["MF1"]), "mf2_toolbox": int(s["MF2"]), "mf3_difficulty": int(s["MF3"]),
        "mf4_fto": int(s["MF4"]), "mf5_routevalue": int(s["MF5"]), "mf_total": mf,
        "barrier_type": a.barrier, "mod_strategy": a.strategy,
        "mod_difficulty_tag": a.difficulty, "fto_note": a.fto,
        "drug_quadrant": matrix(g, mf),
        "drug_mod_one_liner": a.one_liner,
    })
    json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"✅ {a.id}: G{g} · MF {mf}/100 · {d['drug_quadrant']}")
    print(f"   障碍={a.barrier} | 难度={a.difficulty} | FTO={a.fto}")
    print(f"   解法={a.strategy}")


if __name__ == "__main__":
    main()
