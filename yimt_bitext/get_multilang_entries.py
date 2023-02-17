"""Get entries to crawl from dumped metadata files"""
import argparse
import json


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--langs", type=str, nargs=2, help="three-letter language codes")
    args = argparser.parse_args()

    multihost2langs_fn = r"./multihost2langs.json"
    with open(multihost2langs_fn, encoding="utf-8") as stream:
        multihost2langs = json.load(stream)

    entries = set()
    lang1, lang2 = args.langs

    entries_found = 0
    report_interval = 2000
    total = 0

    for host, langs in multihost2langs.items():
        if lang1 in langs and lang2 in langs:
            entries.add(host)
            entries_found += 1

        total += 1
        if total % report_interval == 0:
            print(total, entries_found)
    print(total, entries_found)

    out_path = r"./urls_tocrawl.txt"
    with open(out_path, "w", encoding="utf-8") as stream:
        for url in entries:
            stream.write(url + "\n")
