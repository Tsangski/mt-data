import regex


not_letter = regex.compile(r'[^\p{L}]')


def norm(s, lower=True, remove_noletter=True):
    if lower:
        s = s.lower()

    if remove_noletter:
        s = regex.sub(not_letter, "", s)
    return s


def dedup_file(in_path, out_path):
    pairs = set()

    n = 0
    total = 0

    with open(in_path, encoding="utf-8") as f, open(out_path, "w", encoding="utf-8") as out_f:
        for p in f:
            p = p.strip()
            total += 1
            if total % 100000 == 0:
                print("Total:", total, "Unique:", n)

            pn = norm(p)
            h = hash(pn)
            if h in pairs:
                continue
            else:
                pairs.add(h)

            n += 1
            out_f.write(p + "\n")

    print("Total:", total, "Unique:", n)