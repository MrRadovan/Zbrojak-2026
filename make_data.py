"""Convert parsed questions.json into docs/data.js for the page.

Usage: python3 make_data.py questions.json docs/data.js [--expl expl/merged.json] [--glossary glossary.json] [--practical practical.json]

Optional inputs:
  --expl      JSON dict  {"123": {"why": ..., "ref": ..., "hint": ..., "verify": bool}}  -> q.e
  --glossary  JSON list  [{"term","stems":[regex...],"def","en","cat"}]                   -> QDATA.g
  --practical JSON       {"source","rules":[...],"procedures":[...]}                       -> QDATA.p
"""
import argparse
import json

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("dst")
ap.add_argument("--expl")
ap.add_argument("--glossary")
ap.add_argument("--practical")
a = ap.parse_args()

d = json.load(open(a.src, encoding="utf-8"))
expl = json.load(open(a.expl, encoding="utf-8")) if a.expl else {}
qs = []
missing = []
for q in d["questions"]:
    item = {"n": q["num"], "k": q["key"], "s": q["section"], "p": q["page"], "q": q["q"],
            "a": q["answers"], "c": q["correct"], "i": q["image"]}
    e = expl.get(str(q["num"]))
    if e:
        item["e"] = {"why": e["why"], "ref": e.get("ref", ""), "hint": e.get("hint", ""), "v": 1 if e.get("verify") else 0}
    elif expl:
        missing.append(q["num"])
    qs.append(item)

out = {"source": d["source"], "q": qs}
if a.glossary:
    g = json.load(open(a.glossary, encoding="utf-8"))
    out["g"] = [{"t": x["term"], "s": x["stems"], "d": x["def"], "en": x.get("en", ""), "c": x["cat"]} for x in g]
if a.practical:
    out["p"] = json.load(open(a.practical, encoding="utf-8"))

js = "window.QDATA=" + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";"
assert "�" not in js, "replacement characters left in text"
open(a.dst, "w", encoding="utf-8").write(js)
print(len(qs), "questions written to", a.dst,
      f"({len(qs)-len(missing)} with explanations" + (f", missing: {missing}" if missing else "") + ")",
      f"glossary {len(out.get('g', []))} terms" if a.glossary else "",
      f"practical {len(out['p']['procedures'])} procedures" if a.practical else "")
