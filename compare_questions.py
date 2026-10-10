"""Compare two parsed question files (output of parse_pdf.py) and print what changed.

Usage: python3 compare_questions.py old_questions.json new_questions.json [--json diff.json]

Questions are matched by their number. For each number the script reports whether the
question text, the answers, the marked correct answer or the image changed. Added and
removed numbers are listed too. The summary at the end tells you how many explanations
need to be written or re-checked.
"""
import argparse
import json
import sys


def load(path):
    d = json.load(open(path, encoding="utf-8"))
    return d.get("source", "?"), {q["num"]: q for q in d["questions"]}


def short(t, n=90):
    t = " ".join(t.split())
    return t if len(t) <= n else t[: n - 1] + "…"


ap = argparse.ArgumentParser()
ap.add_argument("old")
ap.add_argument("new")
ap.add_argument("--json", help="write the machine-readable diff here")
a = ap.parse_args()

src_old, old = load(a.old)
src_new, new = load(a.new)
print(f"starý soubor: {src_old} ({len(old)} otázek)")
print(f"nový soubor:  {src_new} ({len(new)} otázek)\n")

added = sorted(set(new) - set(old))
removed = sorted(set(old) - set(new))
changed = []
for n in sorted(set(old) & set(new)):
    o, q = old[n], new[n]
    what = []
    if " ".join(o["q"].split()) != " ".join(q["q"].split()):
        what.append("znění")
    if [" ".join(x.split()) for x in o["answers"]] != [" ".join(x.split()) for x in q["answers"]]:
        what.append("odpovědi")
    if o["correct"] != q["correct"]:
        what.append(f"správná odpověď {'ABC'[o['correct']]}→{'ABC'[q['correct']]}")
    if bool(o.get("image")) != bool(q.get("image")):
        what.append("obrázek")
    if o.get("key") != q.get("key") or o.get("section") != q.get("section"):
        what.append("oddíl")
    if what:
        changed.append((n, what, o, q))

for n in added:
    print(f"+ {n:4d} [{new[n]['key']}] {short(new[n]['q'])}")
for n in removed:
    print(f"- {n:4d} [{old[n]['key']}] {short(old[n]['q'])}")
for n, what, o, q in changed:
    print(f"~ {n:4d} {', '.join(what)}")
    if "znění" in what:
        print(f"       bylo: {short(o['q'])}\n       nyní: {short(q['q'])}")
    if "odpovědi" in what:
        for i, (x, y) in enumerate(zip(o["answers"], q["answers"])):
            if " ".join(x.split()) != " ".join(y.split()):
                print(f"       {'ABC'[i]}) bylo: {short(x)}\n          nyní: {short(y)}")

print(f"\npřidáno {len(added)}, odebráno {len(removed)}, změněno {len(changed)}")
need = len(added) + sum(1 for _, w, _, _ in changed if any(x.startswith(("znění", "odpovědi", "správná")) for x in w))
print(f"vysvětlení k napsání nebo kontrole: {need}")
if a.json:
    json.dump({"added": added, "removed": removed, "changed": [{"num": n, "what": w} for n, w, _, _ in changed]},
              open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
sys.exit(1 if (added or removed or changed) else 0)
