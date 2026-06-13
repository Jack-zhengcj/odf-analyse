#!/usr/bin/env python3
"""Compact score dump for given ids (or all). Usage: python3 _dump.py [id ...]"""
import json, os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
ids = sys.argv[1:]
if not ids:
    ids = sorted(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(RES, "*.json"))
                 if not os.path.basename(f).startswith("_"))
for i in ids:
    p = os.path.join(RES, i + ".json")
    if not os.path.exists(p):
        print("%-22s MISSING" % i); continue
    d = json.load(open(p, encoding="utf-8"))
    md = "md:Y" if os.path.exists(os.path.join(RES, i + ".md")) else "md:.."
    scores = "%2s/%2s/%2s/%2s/%2s/%2s" % (d["A"], d["B"], d["C"], d["D"], d["E"], d["F"])
    tot = d.get("supp_total")
    g = d.get("G")
    comm = ("tot%s" % tot) if d["mode"] == "supplement" else ("G%s" % g)
    print("%-22s %s  tech%2s %-7s kill:%-10s %s  %s" % (
        i, scores, d["tech_moat"], comm, d.get("kill"), md, d.get("mode")))
