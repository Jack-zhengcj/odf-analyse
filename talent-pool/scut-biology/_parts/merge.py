#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge part_*.json + official_roster.json into faculty.json + faculty.csv.

Official roster (2026 学院官网师资页, 教授/副教授) is authoritative for
title / email / office / official research direction, and defines who is
currently on staff. Detailed research/papers/patents/tags come from the
web-search shards. Anyone in the shards but NOT on the official page is
kept and flagged; any official name missing a shard gets a minimal stub.
"""
import json, csv, glob, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)

# --- official roster ---
with open(os.path.join(HERE, "official_roster.json"), encoding="utf-8") as f:
    roster = {r["name"]: r for r in json.load(f)["roster"]}

# --- shards ---
records = []
for fp in sorted(glob.glob(os.path.join(HERE, "part_*.json"))):
    with open(fp, encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, dict):
            data = [data]
        records.extend(data)

# de-dup by name (keep first / richest)
seen, deduped = set(), []
for r in records:
    n = (r.get("name") or "").strip()
    if n and n not in seen:
        seen.add(n)
        deduped.append(r)
records = deduped

CURRENT = "现任(官网师资页2026)"
NOT_LISTED = "未在现任师资页(教授/副教授)名单，待核实(可能属研究员序列/退休/调离/院系调整)"

def overlay(r):
    off = roster.get((r.get("name") or "").strip())
    if off:
        r["title"] = off["title"]            # official title wins (fixes 梁书利/马毅/叶健文 等)
        r["email"] = off.get("email", "")
        r["office"] = off.get("office", "")
        r["research_official"] = off.get("research_official", "")
        r["roster_status"] = CURRENT
    else:
        r.setdefault("email", "")
        r.setdefault("office", "")
        r.setdefault("research_official", "")
        r["roster_status"] = NOT_LISTED
    return r

records = [overlay(r) for r in records]

# stub any official name with no shard yet
have = {(r.get("name") or "").strip() for r in records}
for name, off in roster.items():
    if name not in have:
        areas = [a for a in re.split(r"[、,，/；;]", off.get("research_official", "")) if a]
        records.append({
            "name": name, "name_en": "", "title": off["title"],
            "email": off.get("email", ""), "office": off.get("office", ""),
            "research_official": off.get("research_official", ""),
            "research_areas": areas, "education": "", "career": "",
            "talent_titles": [], "representative_papers": [], "patents": [],
            "metrics": {"google_scholar_citations": "", "h_index": "", "paper_count_est": ""},
            "external_links": [],
            "tags": {"research_field": areas[:3], "seniority": off["title"],
                     "industry_potential": "", "collaboration": ""},
            "confidence": "low", "roster_status": CURRENT,
            "data_caveat": "仅官方基础信息(职称/邮箱/办公室/方向)，检索补充数据待完善",
            "sources": ["学院官网师资队伍页(用户提供)"]
        })

TITLE_RANK = {"教授": 0, "副教授": 1, "研究员": 1, "副研究员": 2}
def trank(t):
    t = (t or "").strip()
    for k, v in TITLE_RANK.items():
        if t.startswith(k):
            return v
    return 3
# current staff first, then by title, then name
records.sort(key=lambda r: (0 if r.get("roster_status") == CURRENT else 1,
                            trank(r.get("title", "")), r.get("name", "")))

def grade(s):
    m = re.match(r"\s*(高|中[-偏]?高|中|中[-偏]?低|低)", (s or "").strip())
    return m.group(1) if m else ""

with open(os.path.join(OUT, "faculty.json"), "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

cols = ["姓名","英文名","职称","在岗状态","邮箱","办公室","研究方向(官方)","研究领域标签",
        "产业转化潜力","产业转化潜力_说明","合作可对接性","合作可对接性_说明","人才头衔",
        "资历层级","细分研究方向(检索)","代表论文数","专利数","论文数估计","数据置信度","官网链接","外部链接"]
with open(os.path.join(OUT, "faculty.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(cols)
    for r in records:
        tags = r.get("tags", {}) or {}
        m = r.get("metrics", {}) or {}
        ip = tags.get("industry_potential", ""); co = tags.get("collaboration", "")
        w.writerow([
            r.get("name",""), r.get("name_en",""), r.get("title",""), r.get("roster_status",""),
            r.get("email",""), r.get("office",""), r.get("research_official",""),
            "; ".join(tags.get("research_field", []) or []),
            grade(ip), ip, grade(co), co,
            "; ".join(r.get("talent_titles", []) or []),
            tags.get("seniority",""),
            "; ".join(r.get("research_areas", []) or []),
            len(r.get("representative_papers", []) or []),
            len(r.get("patents", []) or []),
            m.get("paper_count_est",""), r.get("confidence",""),
            r.get("profile_url",""), "; ".join(r.get("external_links", []) or []),
        ])

cur = [r for r in records if r.get("roster_status") == CURRENT]
notl = [r for r in records if r.get("roster_status") != CURRENT]
bt = {}
for r in cur: bt[r["title"]] = bt.get(r["title"],0)+1
print("total:", len(records), "| current:", len(cur), bt, "| not-listed:", len(notl))
print("not-listed names:", [r["name"] for r in notl])
print("stub(low+official-only):", [r["name"] for r in records if r.get("data_caveat","").startswith("仅官方")])
