"""3. Get multilingual domains for given languages"""
import json
import sys
from collections import defaultdict

from yimt_bitext.web.base import BasicLangStat
from yimt_bitext.web.url_language import UrlLanguage

if __name__ == "__main__":
    stat_f = sys.argv[1]
    langs = sys.argv[2].split(",")
    lang_stat = BasicLangStat(stat_f)
    out_f = "sites-" + "-".join(langs) + ".json"

    filter = True
    url_language = UrlLanguage()
    normalized_langs = [url_language.normalize_lang_code(lang) for lang in langs]

    domain2hosts_langs = defaultdict(list)
    for domain, hosts in lang_stat.hosts_for_langs(langs):
        for h in hosts:
            lang = url_language.find_language(h)
            if lang and lang not in normalized_langs:
                print(h, "filtered")
                continue
            domain2hosts_langs[domain].append(h)

    with open(out_f, "w", encoding="utf-8") as f:
        json.dump(domain2hosts_langs, f)

    print("# of domains: {}".format(len(domain2hosts_langs)))
