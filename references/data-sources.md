# ODFanalyse 取数来源 —— 每个维度去哪儿查数据

打分前必须先把下面这些数据**联网查证**出来，不能凭记忆。给每条数据标注来源，便于复核。

## 理化数据（喂给 A 维）
| 数据 | 首选来源 | 检索词示例 |
|---|---|---|
| 分子量 MW | **PubChem** (pubchem.ncbi.nlm.nih.gov) | "<成分> PubChem molecular weight" |
| logP / XLogP3 | PubChem 的 Computed Properties；DrugBank | "<成分> logP XLogP3" |
| pKa / 解离 | DrugBank、PubChem、Chemicalize | "<成分> pKa" |
| 水溶解度 | PubChem、DrugBank | "<成分> aqueous solubility mg/mL" |

## 药代动力学（喂给 B / C 维）
| 数据 | 首选来源 | 检索词示例 |
|---|---|---|
| 口服绝对生物利用度% | **PubMed / PMC**、DrugBank、FDA label | "<成分> oral bioavailability %" |
| 低BA的机制(首过?降解?渗透?) | PubMed 综述、PMC | "<成分> first-pass metabolism" / "presystemic" |
| 舌下/口腔黏膜人体证据 | PubMed | "<成分> sublingual buccal pharmacokinetics human" |
| Tmax / 起效速度 | PubMed、FDA label | "<成分> Tmax onset" |
| 能否过血脑屏障(中枢成分) | PubMed | "<成分> blood-brain barrier permeability" |

## 剂量（喂给 D 维）
| 数据 | 首选来源 | 检索词示例 |
|---|---|---|
| 常规有效日/单次剂量 | **NIH DSLD**(补剂标签库)、FDA label、临床试验 | "<成分> effective dose mg clinical" |
| 已上市口溶膜/舌下产品的实际剂量 | 厂商页、FDA label | "<成分> oral dissolving film strip mg" |

## 口感/稳定性/包埋（喂给 E 维）
| 数据 | 首选来源 | 检索词示例 |
|---|---|---|
| 味道(苦/腥)、稳定性 | 配方文献、PMC | "<成分> taste masking bitter stability ODF" |
| 是否需包埋及技术 | PMC、AAPS | "<成分> cyclodextrin liposome SEDDS oral film" |

## 市场/TikTok/合规（喂给 F 维 + 商业层）
| 数据 | 首选来源 | 检索词示例 |
|---|---|---|
| 已有口溶膜竞品/品牌/价格 | Amazon、品牌官网、新闻 | "<成分> strips supplement brand price" |
| 品类教育阶段、差评 | Amazon reviews、Reddit、TikTok | "<成分> strips reddit review" |
| TikTok 限流/禁售 | TikTok Shop 政策、合规博客 | "TikTok shop supplement banned <品类>" |
| 合规(FDA DSHEA / NDIN / 成分合法性) | FDA、ODS、合规博客 | "<成分> FDA dietary supplement NDIN status" |

## 取数纪律
1. **优先一手/权威源**：PubChem(理化)、PubMed/PMC(PK)、FDA label、NIH DSLD(剂量)。厂商宣称(尤其"舌下吸收80%")要标注为「厂商宣称、无PK对照」并降权。
2. **区分 onset 与 extent**：很多"舌下更好"说的是起效快(onset，归 C)，不是总吸收量提升(AUC/extent，归 B)——别混。
3. **区分首过型 vs 渗透型**：口服BA低不等于舌下能救。务必查清机制(见 B 维)。
4. 每个关键数字在输出里附来源，置信度低的标注「待证」。
