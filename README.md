# ODFanalyse — 口溶膜(ODF/ODS)开品可行性分析 Skill

把「一个成分 / 成分组 / 产品（input）」变成「可行性评分 + 产品评估（output）」。

口溶膜（oral dissolving film / 舌下膜）真正的竞争力不是「无水便携」这种表面卖点，而是
**①能否真舌下吸收 ②能否提高生物利用度 ③能否加快吸收 ④载药量够不够**。本 skill 把这套逻辑拆成
六维护城河模型，联网查证数据后打分，并做产品评估。

## 六维模型
| 维度 | 满分 | 含义 |
|---|---|---|
| A 舌下黏膜吸收可行性 | 20 | 分子能否透过口腔上皮（MW/logP/解离/剂量） |
| B 生物利用度提升空间 | 20 | 口服BA低是否因首过/降解、且舌下能救（护城河核心） |
| C 快起效场景价值 | 15 | 急性即感 vs 慢性积累 |
| D 载药量可行性 | 15 | 有效剂量 vs 单膜~50mg上限（>100mg判死） |
| E 口感·稳定性·包埋成本 | 10 | 分越高问题越少 |
| F 市场·TikTok·竞品 | 20 | 补剂渠道适配（药物语境改用商业价值轴 G） |

输出 **技术护城河分(A+B+C+D+E，满分80)** 与 **商业分** 永远分开报，附四象限判型与决策原型。

## 校准与验证
- 补剂锚点：褪黑素 80 🟢 / 咖啡因 75 🟢🟡 / 谷胱甘肽 54 🟠（24-agent 联网研究校准）。
- 药物锚点：硝酸甘油 78 / 速效救心丸 70 / 丁丙诺啡 69 / 昂丹司琼 66（已上市舌下膜验证）；
  司美格鲁肽 24（MW4114 渗透死局，但作为药物商业价值极高 → ③低技×高商）；二甲双胍 17（负对照）。

## 安装

### Claude Code
把整个 `odf-analyse/` 目录放到下面任一位置，重启 Claude Code 即自动加载：
- 个人（所有项目可用）：`~/.claude/skills/odf-analyse/`
- 项目（仅该仓库）：`<repo>/.claude/skills/odf-analyse/`

```bash
git clone https://github.com/<you>/odf-analyse.git ~/.claude/skills/odf-analyse
```
之后在对话里说「用 odf-analyse 评估 褪黑素 / 75mg咖啡因 / 硝酸甘油」即可触发。

### Codex / 其它 Agent
Codex 不读 Claude 的 SKILL.md 格式。把本仓库克隆到项目里，并在 `AGENTS.md`（Codex 的指令文件）中
加一段引用，让模型在相关请求时读取 `SKILL.md` 与 `references/`：
```markdown
## ODFanalyse skill
评估口溶膜/舌下/ODF 开品可行性时，先读 odf-analyse/SKILL.md 按其流程执行，
打分用 odf-analyse/scripts/score.py。
```

## 用法
```bash
# 补剂语境
python3 scripts/score.py --A 16 --B 17 --C 13 --D 14 --E 8 --F 12 --kill none
# 药物语境
python3 scripts/score.py --mode drug --A 20 --B 20 --C 15 --D 15 --E 8 --F 0 --G 11 --sellable rx
```

## 目录
```
odf-analyse/
├── SKILL.md                       # 主入口：运行流程
├── README.md
├── scripts/score.py               # 确定性打分器（双轴+双语境）
└── references/
    ├── scoring-model.md           # 完整打分卡
    ├── dimension-glossary.md      # 六维详解
    ├── data-sources.md            # 取数来源
    └── drug-validation.md         # 药物锚点验证
```

## 免责
本 skill 输出为开品/剂型可行性的快速研判，不构成医疗、监管或投资建议。涉及人体使用、claim、合规与上市，
须经专业药剂、法规与临床评估。
