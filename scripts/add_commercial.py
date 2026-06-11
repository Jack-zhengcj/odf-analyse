#!/usr/bin/env python3
"""
把商业轴字段安全合并进已存在的 batch/results/<id>.json（保留全部技术字段不动）。
agent 只需判定 5 个 M 子分 + 3 个定性字段 + 一句话，computed 字段由 score_commercial 确定性算出。

用法：
  python3 scripts/add_commercial.py 谷胱甘肽的id \
     --M1 24 --M2 24 --M3 14 --M4 10 --M5 10 \
     --efficacy 弱证据 --best-format shot/膜 --redline none \
     --risk "FTC-claim,高退款无体感,品牌扒皮" \
     --one-liner "玻璃肌渴望叙事+亚洲美护肤大盘，Esther 已验证~$1亿；卖故事不卖吸收。"

efficacy ∈ {真实证据, 弱证据, 纯叙事}
redline  ∈ {none, regulatory, safety}
--risk   逗号分隔，取自风险面板：高退款无体感 / FTC-claim / 平台封号 / 成分合规红线 / 品牌扒皮 / 价格锚碾压
"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from score_commercial import quadrant2, go_tier, archetype2, MAXS  # noqa

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "batch", "results")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("id")
    for k in MAXS:
        p.add_argument(f"--{k}", type=float, required=True)
    p.add_argument("--efficacy", required=True, choices=["真实证据", "弱证据", "纯叙事"])
    p.add_argument("--best-format", dest="best_format", required=True)
    p.add_argument("--redline", default="none", choices=["none", "regulatory", "safety"])
    p.add_argument("--risk", default="")
    p.add_argument("--one-liner", dest="one_liner", required=True)
    a = p.parse_args()

    path = os.path.normpath(os.path.join(RES, a.id + ".json"))
    if not os.path.exists(path):
        sys.exit(f"❌ 找不到 {path}（先确认 id 对、技术分已评）")
    d = json.load(open(path, encoding="utf-8"))
    if d.get("mode") == "drug":
        sys.exit(f"❌ {a.id} 是 drug，商业看 G 轴，不叠加 commercial")

    s = {k: getattr(a, k) for k in MAXS}
    for k, mx in MAXS.items():
        if not (0 <= s[k] <= mx):
            sys.exit(f"❌ {k}={s[k]} 超域 0-{mx}")
    comm = int(sum(s.values()))
    tech = d.get("tech_moat") or 0
    risk = [x.strip() for x in a.risk.split(",") if x.strip()]

    d.update({
        "m_demand": int(s["M1"]), "m_story": int(s["M2"]), "m_format": int(s["M3"]),
        "m_claim": int(s["M4"]), "m_econ": int(s["M5"]), "commercial": comm,
        "best_format": a.best_format, "efficacy_basis": a.efficacy, "redline": a.redline,
        "risk_flags": risk,
        "quadrant2": quadrant2(tech, comm),
        "go_tier": go_tier(comm, tech, a.redline),
        "comm_archetype": archetype2(tech, comm, a.efficacy),
        "commercial_one_liner": a.one_liner,
    })
    json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"✅ {a.id}: tech {tech}/80 · commercial {comm}/100 · {d['quadrant2']}")
    print(f"   go {d['go_tier']} | {d['comm_archetype']} | best={a.best_format} | {a.efficacy}")
    if risk:
        print(f"   风险: {' / '.join(risk)}")


if __name__ == "__main__":
    main()
