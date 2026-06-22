#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge part_*.json into faculty.json + faculty.csv for the SCUT Biology talent pool."""
import json, csv, glob, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)

records = []
for fp in sorted(glob.glob(os.path.join(HERE, "part_*.json"))):
    with open(fp, encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, dict):
            data = [data]
        records.extend(data)

# de-dup by name (keep first)
seen, deduped = set(), []
for r in records:
    n = r.get("name", "").strip()
    if n and n not in seen:
        seen.add(n)
        deduped.append(r)
records = deduped

TITLE_RANK = {"教授": 0, "副教授": 1, "研究员": 1, "副研究员": 2}
def trank(t):
    t = (t or "").strip()
    for k, v in TITLE_RANK.items():
        if t.startswith(k):
            return v
    return 3
records.sort(key=lambda r: (trank(r.get("title", "")), r.get("name", "")))

def grade(s):
    """Extract 高/中/低 leading grade from a tag string."""
    s = (s or "").strip()
    m = re.match(r"\s*(高|中[-偏]?高|中|中[-偏]?低|低)", s)
    return m.group(1) if m else ""

# faculty.json
with open(os.path.join(OUT, "faculty.json"), "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

# faculty.csv
cols = ["姓名","英文名","职称","研究领域标签","细分研究方向","人才头衔",
        "产业转化潜力","产业转化潜力_说明","合作可对接性","合作可对接性_说明",
        "资历层级","代表论文数","专利数","论文数估计","数据置信度","官网链接","外部链接"]
with open(os.path.join(OUT, "faculty.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(cols)
    for r in records:
        tags = r.get("tags", {}) or {}
        m = r.get("metrics", {}) or {}
        ip = tags.get("industry_potential", "")
        co = tags.get("collaboration", "")
        w.writerow([
            r.get("name",""),
            r.get("name_en",""),
            r.get("title",""),
            "; ".join(tags.get("research_field", []) or []),
            "; ".join(r.get("research_areas", []) or []),
            "; ".join(r.get("talent_titles", []) or []),
            grade(ip), ip,
            grade(co), co,
            tags.get("seniority",""),
            len(r.get("representative_papers", []) or []),
            len(r.get("patents", []) or []),
            m.get("paper_count_est",""),
            r.get("confidence",""),
            r.get("profile_url",""),
            "; ".join(r.get("external_links", []) or []),
        ])

# stats
by_title = {}
for r in records:
    by_title[r.get("title","?")] = by_title.get(r.get("title","?"),0)+1
print("total:", len(records))
print("by_title:", by_title)
print("industry_high:", sum(1 for r in records if grade((r.get("tags") or {}).get("industry_potential","")) in ("高",)))
