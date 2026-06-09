# 🌩️ 云端全量跑 · 自包含粘贴提示词（claude.ai/code · 关机仍跑）

## 怎么用
1. 打开 **claude.ai/code**,新建会话(任意空仓库/新建即可,它会自己 clone skill)。
2. 把下面「========」之间**整段**粘贴为第一条消息,发送。
3. 它会 clone 你的 skill 仓库、并行联网评分、每批 commit+push。**结果持久化,你可随时关机**,回来看 `odf-batch/REPORT.md`。

========
你是 ODFanalyse 全量批处理执行器。目标:对下面内嵌的**全部 243 个成分**逐一用 odf-analyse skill 评分,**幂等续跑**,最后汇总排序成 `odf-batch/REPORT.md`。

### 准备
1. `git clone https://github.com/Jack-zhengcj/odf-analyse.git` 到工作区。这是打分 skill。
2. 读透:`odf-analyse/SKILL.md` + `odf-analyse/references/scoring-model.md` + `dimension-glossary.md` + `data-sources.md` + `drug-validation.md`。打分脚本在 `odf-analyse/scripts/score.py`。
3. 新建 `odf-batch/results/` 目录。把本提示词末尾「INGREDIENTS_JSON」整段存成 `odf-batch/ingredients.json`。

### 逐成分评分(并行子 agent,一次 10–15 个)
对每个成分:
- 若 `odf-batch/results/<id>.json` 已存在 → **跳过**(幂等)。
- 否则:WebSearch/WebFetch 联网查证(理化 MW/logP/pKa/溶解度、口服BA%**及低/高机制:首过型 vs 渗透型**、有效剂量mg、舌下/口腔黏膜人体证据、口感稳定性、市场竞品/合规;**每个数字标来源+置信度**)→ 六维打分(A舌下0-20 / B-BA提升0-20 / C起效0-15 / D载药0-15 / E口感成本0-10 / F市场0-20;判 kill∈{none,dose,tiktok,taste,permeation,regulatory,stability})→ 跑 `python3 odf-analyse/scripts/score.py ...` 取 tech_moat/总分/档位/象限/原型 → 写两份文件:
  - `odf-batch/results/<id>.json` —— **严格扁平顶层 schema**(下方),**禁止嵌套 scores/data**。
  - `odf-batch/results/<id>.md` —— 照 SKILL.md「输出模板」写三段(查证数据带来源 / 六维打分 / 产品评估)。

**扁平 JSON schema(逐字段照填):**
```json
{"id":"","name":"","mode":"supplement|drug","src":[],
 "A":0,"B":0,"C":0,"D":0,"E":0,"F":0,"G":null,"kill":"none","sellable":null,
 "tech_moat":0,"comm":0,"supp_total":0,"band":"","quadrant":"①|②|③|④","archetype":"",
 "key_data":{"MW":0,"logP":0,"oral_BA":"","BA_mechanism":"","dose_mg":"","subl_evidence":""},
 "one_liner":"","sources":[],"confidence":"high|mid|low"}
```
- 补剂:`python3 odf-analyse/scripts/score.py --A .. --B .. --C .. --D .. --E .. --F .. --kill ..`;`comm`=F,`supp_total`=脚本总分,`G`=null。
- **药物(mode=drug):按用户要求忽略传播性/开发难度/TikTok,`--F 0`,重点评准 `G` 商业价值(0-20:市场规模/刚需/竞争)**,`--sellable` 标 otc/rx/controlled/tcm;`comm`=G,`supp_total`=null。命令:`python3 odf-analyse/scripts/score.py --mode drug --A .. --B .. --C .. --D .. --E .. --F 0 --G .. --sellable .. [--kill ..]`。

### 续跑与持久化
- **每完成一批 commit+push 一次**(push 到任意你有写权限的仓库;或在 claude.ai/code 的工作仓库里提交),保证断点续跑安全、关机不丢。

### 收尾(243 全完成后)
写并运行一个等价于 odf-analyse 仓库 `batch/aggregate.py` 的汇总脚本:读 `odf-batch/results/*.json`,**补剂按 `supp_total` 降序、药品按 `G` 降序**,输出 `odf-batch/REPORT.md`(补剂榜=实现可能性排名;药品榜=商业价值排名,并列 tech_moat 对照,标出④低技高商金矿)。末尾给「实现可能性最大 Top 候选 + 第2层商业体检提示」。

### 锚点自检(必须复现,否则查打分逻辑)
褪黑素80🟢 / 肌酸29🔴(剂量否决) / 硝酸甘油 tech78 ② / 司美格鲁肽 tech24·G20 ③ / 尼古丁 tech69·G18 ①。

纪律:数据先查证再打分附来源;永远分开报技术分(80)和商业分;诚实优先,宁标「待证」不编数。

INGREDIENTS_JSON:
```json
[把 https://github.com/Jack-zhengcj/odf-analyse 仓库 batch/ingredients.json 内容粘到这里;若仓库还没有该文件,则使用本机 /Users/jack/Desktop/python/odf-batch/ingredients.json 的 243 条内容]
```
========

## 备注
- `ingredients.json` 已在本机 `/Users/jack/Desktop/python/odf-batch/ingredients.json`(243条)。Jack 把它推到 GitHub 仓库 `batch/` 后,这段提示词可改成直接读仓库文件,无需内嵌。
- 跑完读 `odf-batch/REPORT.md`:补剂按总分排=口溶膜实现可能性;药品按 G 排=商业价值。
