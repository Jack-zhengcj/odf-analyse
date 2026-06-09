# 🌩️ 云端全量跑 · 仓库原生提示词（claude.ai/code · 关机仍跑）

## 三步开跑(出门前 1 分钟搞定)
1. 打开 **claude.ai/code** → 新建会话 → 仓库选 **`Jack-zhengcj/odf-analyse`**。
2. 把下面「========」之间整段**粘贴**为第一条消息,发送。
3. 走人去打球。它会并行限流评分、每波 commit+push,进度持久化在 GitHub。回来看 `batch/REPORT.md`。

========
你是 ODFanalyse 全量批处理执行器。当前仓库就是 odf-analyse skill,已含 `batch/` 工作包。目标:把 `batch/ingredients.json` 里**全部 243 个成分**评完,**幂等续跑**(`batch/results/` 里已有 16 个,跳过),最后汇总成 `batch/REPORT.md`。

**限流(单进程也要克制,防账号风控)**:并行子 agent 一次**最多 5 个**,分波——每波等完再开下一波;联网检索别狂刷,够用即可。

步骤:
1. 读透打分卡:`SKILL.md` + `references/scoring-model.md` + `dimension-glossary.md` + `data-sources.md` + `drug-validation.md`。打分脚本 `scripts/score.py`。
2. 读 `batch/RUNNER.md`(协议)+ `batch/ingredients.json`(243个,字段 id/name/mode/src/cat)。
3. 逐成分评分(**子 agent 并发≤5,分波**):
   - 若 `batch/results/<id>.json` 已存在 → **跳过**。
   - 否则:WebSearch/WebFetch 联网查证(理化 MW/logP/pKa、口服BA%**及低/高机制:首过型 vs 渗透型**、有效剂量mg、舌下/口腔黏膜人体证据、口感稳定性、市场合规;**每数字标来源+置信度**)→ 六维打分(A0-20/B0-20/C0-15/D0-15/E0-10/F0-20,判 kill)→ `python3 scripts/score.py ...` 取 tech_moat/总分/档位/象限/原型 → 写 `batch/results/<id>.json`(**严格扁平顶层 schema,见 RUNNER.md 第3节,禁止嵌套 scores/data**)+ `batch/results/<id>.md`(skill 输出模板三段)。
4. **drug 语境**(mode=drug):按用户要求**忽略传播性/开发难度/TikTok,`--F 0`**,重点把 **G 商业价值(0-20)** 评准;`--sellable` 标 otc/rx/controlled/tcm。命令:`python3 scripts/score.py --mode drug --A .. --B .. --C .. --D .. --E .. --F 0 --G .. --sellable .. [--kill ..]`。
5. **每完成一波就** `git add batch/results && git commit -m "score wave" && git push`(进度持久化,关机/断网都不丢,可随时回来看 commit)。
6. 全部 243 完成后:`python3 batch/validate.py` 体检并修不合格 → `python3 batch/aggregate.py` 生成 `batch/REPORT.md` → 最后 commit+push。
7. 锚点自检(必须复现):褪黑素80🟢 / 肌酸29🔴 / 硝酸甘油 tech78② / 司美格鲁肽 tech24·G20③ / 尼古丁 tech69·G18①。

纪律:数据先查证再打分附来源;永远分开报技术分(80)和商业分;诚实优先,宁标「待证」不编数。每跑几十个汇报一次累计 X/243。
========

## 看进度
- **GitHub 仓库** Jack-zhengcj/odf-analyse 的 commit 历史 = 实时进度(每波一个 commit)。
- 跑完读 `batch/REPORT.md`:补剂按总分排=口溶膜实现可能性;药品按 G 排=商业价值。
- 或在那个 claude.ai/code 会话页直接看它干到哪。
