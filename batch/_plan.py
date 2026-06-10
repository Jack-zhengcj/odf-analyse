#!/usr/bin/env python3
"""Compute remaining (idempotent) ingredients and chunk into waves of agents."""
import json, glob, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
allg = json.load(open(os.path.join(HERE, "ingredients.json"), encoding="utf-8"))
done = {os.path.basename(f)[:-5] for f in glob.glob(os.path.join(HERE, "results", "*.json"))
        if not os.path.basename(f).startswith("_")}
todo = [x for x in allg if x["id"] not in done]
print("TOTAL", len(allg), "| DONE", len(done), "| TODO", len(todo))
supp = [x for x in todo if x["mode"] == "supplement"]
drug = [x for x in todo if x["mode"] == "drug"]
print("TODO supplement", len(supp), "| TODO drug", len(drug))

CHUNK = int(sys.argv[1]) if len(sys.argv) > 1 else 6
groups = [todo[i:i+CHUNK] for i in range(0, len(todo), CHUNK)]
print("NUM CHUNKS (size %d): %d -> waves of 5 = %d" % (CHUNK, len(groups), (len(groups)+4)//5))
for i, g in enumerate(groups):
    rows = ["%s|%s|%s|%s" % (x["id"], x["name"], x["mode"], x["cat"]) for x in g]
    print("CHUNK %02d (%s): %s" % (i+1, g[0]["mode"], "  ;  ".join(rows)))
