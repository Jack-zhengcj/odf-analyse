# ODFanalyse 批量评分 · 运行协议 (RUNNER)

本文件是**自包含**批处理协议。本地定时任务 / claude.ai 网页云端 / 人工接续 都照此执行,
保证打分口径一致、**幂等不重复**。

## 0. 准备(每次运行开头做一次)
- skill 来源:`https://github.com/Jack-zhengcj/odf-analyse.git`
  - 本地已在 `~/.claude/skills/odf-analyse/`;云端先 `git clone` 到工作目录。
- 工作目录:`~/Desktop/python/odf-batch/`(云端则为 clone 根目录下自建 `odf-batch/`)
- 成分清单:`odf-batch/ingredients.json`(243 条;字段 id/name/mode/src/cat)
- 打分脚本:`odf-batch/score.py`
- 结果目录:`odf-batch/results/`(每个成分一个 `<id>.json` + `<id>.md`)

## 1. 选取本批要做的成分(幂等核心)
- 读 `ingredients.json`,对每条检查 `results/<id>.json` 是否已存在。
- **已存在 = 跳过**(不重复联网、不重复打分)。
- 取前 N 个未完成的(本地定时任务建议 N=8;云端一次性可设 N=全部剩余)。

## 2. 逐个成分评分(严格照 skill,不许凭记忆)
对每个成分,完整执行 `~/.claude/skills/odf-analyse/SKILL.md` 的「运行流程 第0–5步」:
1. **定 mode**:用 `ingredients.json` 里的 `mode` 字段(supplement / drug)。
2. **联网查证**(WebSearch/WebFetch,每个数字标来源+置信度):
   理化 MW/logP/pKa/溶解度;口服BA%**及低/高机制(首过 vs 渗透)**;有效剂量 mg;
   舌下/口腔黏膜人体证据;口感稳定性/是否需包埋;市场竞品价格/TikTok限流/合规。
3. **六维打分**(锚点见 `references/scoring-model.md` + `dimension-glossary.md`):
   A舌下吸收0-20 · B生物利用度提升0-20 · C快起效0-15 · D载药0-15 · E口感成本0-10 · F市场0-20;
   drug 语境另给 `G`(0-20 商业/战略价值,与F解耦)和 `sellable`(otc/rx/controlled/tcm)。
   **drug 语境按用户要求:忽略传播性/开发难度/TikTok,F可填0,重点把 G 商业价值评准。**
4. **跑脚本算分**(别手算):
   - 补剂:`python3 score.py --A .. --B .. --C .. --D .. --E .. --F .. --kill <none|dose|tiktok|taste|permeation|regulatory|stability>`
   - 药物:`python3 score.py --mode drug --A .. --B .. --C .. --D .. --E .. --F 0 --G <0-20> --sellable <rx|controlled|otc|tcm> [--kill permeation]`
5. **自检**:与锚点对齐(褪黑素80/咖啡因75/谷胱甘肽54;硝酸甘油78/速效救心丸70/司美格鲁肽tech24)。偏离要么解释要么修分,不许凑分。

## 3. 写结果(两份,幂等)
**`results/<id>.json`**(机器可聚合,字段固定):
```json
{"id":"melatonin","name":"褪黑素 Melatonin","mode":"supplement","src":["fda","amazon"],
 "A":16,"B":17,"C":13,"D":14,"E":8,"F":12,"G":null,"kill":"none","sellable":null,
 "tech_moat":68,"comm":12,"supp_total":80,"band":"🟢 强烈推荐","quadrant":"①","archetype":"真护城河型",
 "key_data":{"MW":232,"logP":1.25,"oral_BA":"3-15%","BA_mechanism":"CYP1A2首过","dose_mg":"3-5","subl_evidence":"有人体PK"},
 "one_liner":"小分子+首过型低BA+低剂量,舌下成倍救回,立项首选",
 "sources":["PubChem CID 896","PMID ..."],"confidence":"high"}
```
**`results/<id>.md`**:照 skill「输出模板」写完整三段(查证数据/六维打分/产品评估)。

## 4. 全部完成后 → 汇总排序
当 `results/` 的 json 数 == `ingredients.json` 条数:
- 跑 `python3 aggregate.py`(见下),生成 `REPORT.md`:
  - 补剂榜:按 `supp_total` 降序;标档位/原型/一句话。
  - 药品榜:按 `G` 商业价值降序(用户指定 drug 看商业价值);并列出 tech_moat 供对照,标 ④象限「低技高商」金矿(如司美格鲁肽)。
  - 总结论:实现可能性最大的 Top 候选 + 第2层商业体检提示。

## 5. 进度与日志
- 每批结束 echo 一行:`✅ 本批完成 M 个,累计 X/243,剩余 Y`。
- 失败的成分记到 `results/_errors.log`,不阻塞其他成分。

## 纪律(照搬 skill)
1. 数据先查证再打分,关键数字附来源;低置信标「待证」。
2. 永远分开报 技术分(80) 与 商业分,不要只给混合 total。
3. 诚实优先,宁标「待证」不编数。
