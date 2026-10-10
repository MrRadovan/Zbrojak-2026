"""Parse the MV question bank PDF into structured JSON + question images.

Usage: python3 -I parse_pdf.py <pdf> <out.json> <img_dir>

Marking convention (verified visually on pages 2, 146, 158, 190):
  - section headers: font size ~20
  - question text: Calibri-Bold; for image questions the number ("715.") stands
    alone on a line, the image follows, then the bold question text
  - answers: Calibri regular; the correct answer is set in Calibri-Italic AND
    highlighted with a gray filled rectangle (fill 0.827). A few answers carry
    only the highlight, so the highlight is the primary signal.
"""
import json
import os
import re
import sys
from collections import Counter

import pdfplumber

PDF, OUT, IMG_DIR = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(IMG_DIR, exist_ok=True)

Q_RE = re.compile(r"^(\d+)\.\s*(.*)$", re.S)
A_RE = re.compile(r"^([ABCabc])\)\s*(.*)$", re.S)

SECTION_MAP = [
    ("I.", "Zákon o zbraních a střelivu", "pravo"),
    ("II.", "Prováděcí právní předpisy", "pravo"),
    ("III.", "Jiné právní předpisy", "pravo"),
    ("IV.", "Nauka o zbraních a střelivu", "nauka"),
    ("V.", "Zdravotnické minimum", "zdravi"),
]


def group_lines(words):
    lines, cur, cur_top = [], [], None
    for w in words:
        if cur_top is None or abs(w["top"] - cur_top) > 3:
            if cur:
                lines.append(cur)
            cur, cur_top = [], w["top"]
        cur.append(w)
    if cur:
        lines.append(cur)
    return lines


def line_text(line):
    t = " ".join(w["text"] for w in line)
    t = t.replace("�", "ti")  # the Calibri "ti" ligature has no Unicode mapping in this PDF
    t = re.sub(r"\s+([.,;:)])", r"\1", t)
    t = re.sub(r"\(\s+", "(", t)
    t = re.sub(r"„\s+", "„", t)
    t = re.sub(r"\s+“", "“", t)
    return t.strip()


def line_stats(chars, top, bottom, rects):
    """Return (n, italic, bold, highlighted) char counts for chars in the band."""
    n = it = bd = hl = 0
    for c in chars:
        if c["text"].isspace():
            continue
        cy = (c["top"] + c["bottom"]) / 2
        if not (top - 2 <= cy <= bottom + 2):
            continue
        n += 1
        if "Italic" in c["fontname"]:
            it += 1
        if "Bold" in c["fontname"]:
            bd += 1
        for r in rects:
            if r["x0"] - 1 <= c["x0"] and c["x1"] <= r["x1"] + 1 and r["top"] - 1 <= cy <= r["bottom"] + 1:
                hl += 1
                break
    return n, it, bd, hl


questions = []
section = section_key = None
cur_q = cur_a = None
pending_image = None  # (page, num_line_bottom) waiting for the question text line

pdf = pdfplumber.open(PDF)
n_pages = len(pdf.pages)


def flush_answer():
    global cur_a
    if cur_a is not None and cur_q is not None:
        cur_q["answers"].append(cur_a)
    cur_a = None


def flush_question():
    global cur_q
    flush_answer()
    if cur_q is not None:
        questions.append(cur_q)
    cur_q = None


for pno, page in enumerate(pdf.pages):
    if pno == 0:
        continue  # table of contents
    chars = page.chars
    rects = [r for r in page.rects if r.get("fill") and r.get("non_stroking_color") not in (None, 1, (1,), [1])
             and r["x1"] - r["x0"] > 20]
    words = page.extract_words(x_tolerance=3)
    lines = group_lines(words)
    for line in lines:
        text = line_text(line)
        top, bottom = min(w["top"] for w in line), max(w["bottom"] for w in line)
        n, it, bd, hl = line_stats(chars, top, bottom, rects)
        max_size = max((c["size"] for c in chars if top - 2 <= (c["top"] + c["bottom"]) / 2 <= bottom + 2), default=11)
        # page number
        if re.fullmatch(r"\d+", text) and max_size < 13:
            continue
        # section header
        if max_size >= 16:
            flush_question()
            for num, name, key in SECTION_MAP:
                if text.startswith(num):
                    section, section_key = name, key
                    break
            continue
        bold_frac = bd / n if n else 0
        mq = Q_RE.match(text)
        ma = A_RE.match(text)
        if mq and bold_frac >= 0.5 and not (cur_a is None and cur_q is not None and not cur_q["q"] and not re.fullmatch(r"\d+\.", text)):
            # new question (number-only line or number + text)
            flush_question()
            cur_q = {
                "num": int(mq.group(1)), "section": section, "key": section_key, "page": pno + 1,
                "q": mq.group(2).strip(), "answers": [], "image": None,
            }
            if not cur_q["q"]:
                pending_image = (pno, bottom)
            continue
        if ma and cur_q is not None:
            flush_answer()
            body = ma.group(2).strip()
            cur_a = {"letter": ma.group(1).upper(), "text": body, "n": n, "it": it, "hl": hl}
            continue
        # continuation
        if cur_a is not None:
            cur_a["text"] += " " + text
            cur_a["n"] += n
            cur_a["it"] += it
            cur_a["hl"] += hl
        elif cur_q is not None:
            if not cur_q["q"] and pending_image is not None and bold_frac >= 0.5:
                ipage, itop = pending_image
                # the image sits between the number line and the question text,
                # possibly on the previous page when the text wrapped to a new page
                ipg = pdf.pages[ipage]
                limit = top + 2 if ipage == pno else ipg.height
                imgs = [i for i in ipg.images if i["top"] >= itop - 2 and i["bottom"] <= limit]
                if imgs:
                    x0 = max(0, min(i["x0"] for i in imgs) - 4)
                    x1 = min(ipg.width, max(i["x1"] for i in imgs) + 4)
                    y0 = max(0, min(i["top"] for i in imgs) - 2)
                    y1 = min(ipg.height, max(i["bottom"] for i in imgs) + 2)
                    fname = f"q{cur_q['num']}.png"
                    ipg.crop((x0, y0, x1, y1)).to_image(resolution=130).save(os.path.join(IMG_DIR, fname), format="PNG")
                    cur_q["image"] = fname
                pending_image = None
            cur_q["q"] = (cur_q["q"] + " " + text).strip()

flush_question()

problems, out = [], []
for q in questions:
    hl = [a["hl"] / a["n"] if a["n"] else 0 for a in q["answers"]]
    it = [a["it"] / a["n"] if a["n"] else 0 for a in q["answers"]]
    by_hl = [i for i, r in enumerate(hl) if r > 0.5]
    by_it = [i for i, r in enumerate(it) if r > 0.5]
    correct = by_hl[0] if len(by_hl) == 1 else (by_it[0] if len(by_it) == 1 else None)
    flag = None
    if len(q["answers"]) != 3:
        flag = f"{len(q['answers'])} answers"
    elif correct is None:
        flag = "no unique correct"
    elif by_hl and by_it and by_hl != by_it:
        flag = "highlight/italic disagree"
    elif not by_hl or not by_it:
        flag = "single signal only"
    if flag:
        problems.append({"num": q["num"], "page": q["page"], "flag": flag,
                         "hl": [round(x, 2) for x in hl], "it": [round(x, 2) for x in it], "q": q["q"][:70]})
    out.append({"num": q["num"], "section": q["section"], "key": q["key"], "page": q["page"],
                "q": q["q"], "answers": [a["text"] for a in q["answers"]], "correct": correct,
                "image": q["image"]})

counts = Counter((q["section"], q["key"]) for q in out)
print("pages:", n_pages, "questions:", len(out))
for (s, k), c in counts.items():
    print(f"  {s} [{k}]: {c}")
nums = [q["num"] for q in out]
print("num range", min(nums), max(nums), "missing", [n for n in range(1, max(nums) + 1) if n not in nums],
      "dups", [n for n in set(nums) if nums.count(n) > 1])
print("images:", sum(1 for q in out if q["image"]))
print("problems:", len(problems))
for p in problems:
    print("  ", p)
json.dump({"source": "MV – Soubor testových otázek pro teoretickou část ZOZ a komisionální zkoušku, verze 15. 12. 2025",
           "questions": out}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
