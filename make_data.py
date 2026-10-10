"""Convert parsed questions.json into build/data.js for the page.

Usage: python3 make_data.py questions.json build/data.js
"""
import json
import sys

src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(src, encoding="utf-8"))
qs = [{"n": q["num"], "k": q["key"], "s": q["section"], "p": q["page"], "q": q["q"],
       "a": q["answers"], "c": q["correct"], "i": q["image"]} for q in d["questions"]]
js = "window.QDATA=" + json.dumps({"source": d["source"], "q": qs}, ensure_ascii=False, separators=(",", ":")) + ";"
assert "�" not in js, "replacement characters left in text"
open(dst, "w", encoding="utf-8").write(js)
print(len(qs), "questions written to", dst)
