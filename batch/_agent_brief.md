# ODFanalyse 子执行器协议（每个打分子agent必须严格照此执行）

工作目录 `/home/user/odf-analyse`（已是 odf-analyse skill 仓库）。任务：把分配给你的成分逐个评完，每个写两份文件到 `batch/results/`。**先联网查证后打分，诚实优先，宁标「待证」不编数。**

## 0. 幂等（先做）
每个成分先查 `batch/results/<id>.json` 是否已存在 → **存在则跳过**，不重做、不重复联网。

## 1. 联网查证（每个成分 2–4 次定向检索，别狂刷；每个关键数字附来源 URL/PMID + 置信度）
- **理化（→A）**：MW、logP/XLogP3、pKa/解离、水溶性 —— 首选 **PubChem**（一次搜索常拿全）。
- **药代（→B/C）**：口服绝对 BA%，**及低/高 BA 的机制**——必须判定属于哪类：
  - **首过型**（肝/肠 first-pass、胃酸/酶降解，分子本身能透膜）→ 舌下绕过首过**真能救**，B 高 16–20；
  - **渗透/溶解度型**（太大/太亲水/带电/极亲脂结晶，根本透不过膜）→ 舌下**救不动**，B 7–9 伪需求；
  - **BA 已高地板**（口服 BA>70%，无可救缺口但能工作）→ B 5–8；
  - **路线错误**（入血到不了靶点，如过不了血脑屏障；或高剂量口服即饱和）→ B 0–4。
  来源：PubMed/PMC/DrugBank/FDA label。
- **剂量（→D）**：常规单次有效剂量 mg；已上市舌下/口腔膜剂剂量。
- **舌下/口腔黏膜人体证据（→A/B/C）**：有无人体舌下/buccal PK（金标准）。厂商「舌下吸收 80%」类宣称**降权**并标注「无 PK 对照」。区分 onset(起效快→C) 与 extent(总吸收提升→B)。
- **口感/稳定性/包埋（→E）**。
- **[仅补剂] 市场（→F）**：竞品/价格、TikTok 限流红线、FDA DSHEA/NDIN 合规。
- 明显结论可短路少搜：肽/蛋白/单抗 MW≫800（渗透死局）、克级粉（剂量否决）、活菌/活酶（稳定性）。

## 2. 六维打分（满分与锚）
| 维度 | 满分 | 高 | 中 | 低 |
|---|---|---|---|---|
| **A 舌下吸收** | 20 | 16-20：MW<500+logP1.6-3.3+口腔pH中性+剂量<20mg（褪黑素16/硝酸甘油20） | MW<800 一项偏离（咖啡因13） | MW>800/强亲水带电/极亲脂结晶（CoQ10≈2/B12≈1） |
| **B BA提升** | 20 | 16-20：首过型+能透膜（褪黑素17/硝酸甘油20/尼古丁18） | 7-9 渗透型伪需求；5-8 BA已高地板（咖啡因9） | 0-4 路线错误（GABA/B12/二甲双胍） |
| **C 起效** | 15 | 13-15：急性即感（咖啡因14/救心15/硝酸甘油15） | 8-12 半急性/仪式感 | 1-7 纯慢性积累（NMN5） |
| **D 载药** | 15 | 13-15：≤20mg | 9-12：20-50mg；5-8：50-100mg | **>100mg=0（dose 一票否决）** |
| **E 成本** | 10 | 9-10：无需包埋（褪黑素8） | 5-6：需微囊/增溶 | 3-4：需脂质体/纳米乳；0：口感不可掩 |
| **F 市场** | 20 | 16-20：可搭便车赛道+不限流（能量膜19） | 10-15：需自费教育/差异化仅一维 | **0：触限流红线** |

**一票否决 kill（命中即封顶，传给 score.py 的 --kill）**：
- `dose` 单次有效剂量>100mg（单膜物理装不下）→ 封顶≤40，D 记 0。
- `tiktok` 触 TikTok 限流红线 → 封顶≤45。红线含：**减肥/食欲抑制、性功能/睾酮、所有草本(herbal/botanical/蘑菇/adaptogen)、美白/淡斑、疾病 claim**。⚠️大量植物提取/适应原/蘑菇/激素增强类补剂命中此项，技术再好补剂总分也 ≤45。
- `taste` 强苦涩腥且任何掩味都盖不住（krill 级）→ 封顶≤50，E 低。
- `permeation` MW>800 且无促渗方案、且本属渗透型 → 封顶≤50（CoQ10/肽/单抗）。
- `regulatory` 成分被 FDA 排除/诉讼，或「舌下=新摄入途径」可能触发 NDIN → 封顶≤45。
- `stability` 常温含水成膜无法存活（活菌/活性酶）→ E≤3，不封总分（用 `stability`）。
- `none` 无。

**药物语境（mode=drug）**：按用户要求**忽略传播性/开发难度/TikTok，F=0**。另给：
- **G 药物/战略商业价值 0-20**（与 F 解耦，**重点评准**）：看该药本身市场规模/刚需/是否已有舌下或膜剂临床/可替代性。锚：G16-20=数十亿美元级 blockbuster 或强战略（GLP-1/单抗/他汀/DOAC/脱发DTC/ED）；G10-15=中等刚需市场；G5-9=仿制红海薄利/小适应症（硝酸甘油G9）；G0-4=边缘。
- **sellable** ∈ {otc, rx, controlled, tcm}。
- 技术性渗透死局加 `--kill permeation`。

## 3. 跑脚本（必须，别手算总分）
- 补剂：`python3 scripts/score.py --A .. --B .. --C .. --D .. --E .. --F .. --kill <none|dose|tiktok|taste|permeation|regulatory|stability>`
- 药物：`python3 scripts/score.py --mode drug --A .. --B .. --C .. --D .. --E .. --F 0 --G <0-20> --sellable <otc|rx|controlled|tcm> [--kill permeation]`
从脚本输出**抄回**：`tech_moat`（=A+B+C+D+E，/80）、补剂 `supp_total`（经封顶 /100，药物为 null）、`band`（补剂抄「档位 →」标签如「🟢 强烈推荐」；药物抄技术档位如「高技：舌下/口溶膜真值得做」）、`quadrant`（四象限，存符号+短label 如「① 高技×高商」）、`archetype`（原型整串）。

## 4. 自检锚点（结果须符合直觉；偏离要解释或修分，不许凑分）
- 补剂(supp_total)：褪黑素80 / 咖啡因75 / 谷胱甘肽54 / 维D3 51 / B12 46 / L-茶氨酸40 / 5-HTP40 / CBD38 / NMN35 / 姜黄素33 / GABA30 / 肌酸29 / CoQ10 27 / 醉茄24 / 胶原肽23 / 益生菌16。
- 药物(tech_moat·G)：硝酸甘油78·G9 / 尼古丁69·G18 / 丁丙诺啡69 / 昂丹司琼66 / 司美24·G20 / 二甲双胍17。
- 若你负责的成分本身是上述锚点，**复现该分**（联网查证以支撑维度拆分，总分落在锚点±2）。

## 5. 只写一份文件：`batch/results/<id>.json`（MD 由上层用脚本统一生成，**你不要写 .md**——省你的 token，确保你能把整块成分都做完）
**严格扁平顶层，禁止嵌套 scores/data 对象**：
```json
{"id":"<id>","name":"<name>","mode":"<mode>","src":["<src>"],
 "A":int,"B":int,"C":int,"D":int,"E":int,"F":int,"G":int或null,"kill":"<kill>","sellable":"<sellable>或null",
 "tech_moat":int,"comm":int,"supp_total":int或null,
 "band":"<band>","quadrant":"<quadrant>","archetype":"<archetype>",
 "key_data":{"MW":..,"logP":..,"pKa":..,"oral_BA":"..","BA_mechanism":"首过型/渗透型/地板/路线错误 + 说明","dose_mg":"..","subl_evidence":".."},
 "notes":"3-5 句：A-F 六维各自为何这么打分（首过 vs 渗透判定、剂量、口感、市场/G），供生成 MD 用",
 "one_liner":"一句话判型+理由",
 "sources":["URL或PMID",..],"confidence":"high/中/待证 + 说明"}
```
字段纪律：`src` 用 ingredients 给的（补剂如 ["fda","amazon"]，药物 ["drug"]）；`comm` 补剂=F、药物=G；补剂 `G`=null、`sellable`=null、`supp_total`=数；药物 `F`=0、`supp_total`=null、`G`=数、`sellable`填。`key_data` 至少含 MW/logP/oral_BA/BA_mechanism/dose_mg/subl_evidence（pKa/solubility/taste/market/regulatory 可加）。`notes` 必填（给 MD 用）。

## 6. 收尾自检
每个成分写完跑 `python3 -c 'import json;json.load(open("batch/results/<id>.json"))'` 验证 JSON 合法且扁平。**写完一个就存一个**（别攒到最后，防中途被截断丢进度）。

## 7. 返回给上层（务必简短，别回贴文件全文）
一个 markdown 表，每行一个成分：`id | mode | A/B/C/D/E/F | tech_moat | supp_total或G | kill | band`，外加一行确认所有 JSON 已写、校验通过。
