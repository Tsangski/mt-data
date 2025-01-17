""""2. Calculate statistics on languages of text from metadata file"""
import argparse
import glob
import json
import os
import shutil

from yimt_bitext.web.base import BasicLangStat
from yimt_bitext.web.cc import merge_k2dict, update_k2set, update_k2dict, merge_k2set


class NetLangDist:

    def __init__(self, stat_file):
        self.stat_file = stat_file
        if os.path.exists(self.stat_file):
            with open(stat_file, encoding="utf-8") as stream:
                self.net2lang2len = json.load(stream)
        else:
            self.net2lang2len = {}

    def __len__(self):
        return len(self.net2lang2len)

    def __contains__(self, item):
        return item in self.net2lang2len

    def __getitem__(self, item):
        return self.net2lang2len[item]

    def __iter__(self):
        return iter(self.net2lang2len)

    def items(self):
        return self.net2lang2len.items()

    def save(self):
        with open(self.stat_file, "w", encoding="utf-8") as stream:
            json.dump(self.net2lang2len, stream)

    def update(self, net2lang2len):
        merge_k2dict(self.net2lang2len, net2lang2len)


def stat_from_meta_by_host(meta_file):
    """For multilingual site"""
    host2lang2len = {}

    report_interval = 10000
    total = 0

    with open(meta_file, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            url, host, domain, lang, content_len = parts
            content_len = int(content_len)

            update_k2dict(host2lang2len, host, lang, content_len)

            total += 1
            if total % report_interval == 0:
                print(" ", total, "urls")
        print(" ", total, "urls")

    return host2lang2len


def stat_from_meta_by_domain(meta_file):
    """For multilingual domain"""
    domain2hosts = {}
    domain2lang2len = {}

    report_interval = 10000
    total = 0

    with open(meta_file, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            url, host, domain, lang, content_len = parts
            content_len = int(content_len)

            update_k2set(domain2hosts, domain, host)
            update_k2dict(domain2lang2len, domain, lang, content_len)

            total += 1
            if total % report_interval == 0:
                print(" ", total, "urls")
        print(" ", total, "urls")

    return domain2hosts, domain2lang2len


def stat_by_host(meta_dir):
    processed_meta_dir = os.path.join(meta_dir, "processed_meta")
    if not os.path.exists(processed_meta_dir):
        os.mkdir(processed_meta_dir)

    host2lang2len = {}
    host2lang2len_fn = os.path.join(args.meta_dir, "host2lang2len.json")
    if os.path.exists(host2lang2len_fn):
        print("Loading existing stat for updating...")
        with open(host2lang2len_fn, encoding="utf-8") as stream:
            host2lang2len = json.load(stream)

    meta_files = glob.glob(os.path.join(meta_dir, "*.meta"))
    for f in meta_files:
        print("Stating from metadata file ", f)
        host2lang2len_local = stat_from_meta_by_host(f)
        print("  # of hosts found: ", len(host2lang2len_local))

        host2lang2len = merge_k2dict(host2lang2len, host2lang2len_local)
        print("  # of hosts after merging: ", len(host2lang2len))

        shutil.move(f, processed_meta_dir)

    with open(host2lang2len_fn, "w", encoding="utf-8") as stream:
        json.dump(host2lang2len, stream)


def stat_by_domain(meta_dir):
    meta_files = glob.glob(os.path.join(meta_dir, "*.meta"))
    processed_meta_dir = os.path.join(meta_dir, "processed_meta")
    if not os.path.exists(processed_meta_dir):
        os.mkdir(processed_meta_dir)

    domain2hosts = {}
    domain2lang2len = {}

    domain2hosts_fn = os.path.join(meta_dir, "domain2hosts.json")
    domain2lang2len_fn = os.path.join(meta_dir, "domain2lang2len.json")

    update = True
    if update:
        print("Loading existing stat for updating...")
        if os.path.exists(domain2hosts_fn):
            with open(domain2hosts_fn, encoding="utf-8") as stream:
                domain2hosts = json.load(stream)

        if os.path.exists(domain2lang2len_fn):
            with open(domain2lang2len_fn, encoding="utf-8") as stream:
                domain2lang2len = json.load(stream)

    for f in meta_files:
        print("Stating from metadata file ", f)
        domain2hosts_local, domain2lang2len_local = stat_from_meta_by_domain(f)

        print("  # of domains found: ", len(domain2lang2len_local))

        domain2hosts = merge_k2set(domain2hosts, domain2hosts_local)
        domain2lang2len = merge_k2dict(domain2lang2len, domain2lang2len_local)

        print("  # of domains after merging: ", len(domain2lang2len))

        shutil.move(f, processed_meta_dir)  # move meta file into done dir

    with open(domain2hosts_fn, "w", encoding="utf-8") as stream:
        json.dump(domain2hosts, stream)

    with open(domain2lang2len_fn, "w", encoding="utf-8") as stream:
        json.dump(domain2lang2len, stream)


def stat_from_metadata(meta_dir):
    processed_meta_dir = os.path.join(meta_dir, "processed_meta")
    if not os.path.exists(processed_meta_dir):
        os.mkdir(processed_meta_dir)

    lang_stat = BasicLangStat(os.path.join(meta_dir, "domain2host2lang2len.json"))
    print("# of domains:", lang_stat.size())

    meta_files = glob.glob(os.path.join(meta_dir, "*.meta"))
    if len(meta_files) == 0:
        print("No meta file to process.")
    for f in meta_files:
        print("Stating from metadata file ", f)
        host2lang2len_local = stat_from_meta_by_host(f)
        for host, lang2len in host2lang2len_local.items():
            lang_stat.update(host, lang2len)

        shutil.move(f, processed_meta_dir)

        print("# of domains:", lang_stat.size())

    lang_stat.save()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--meta_dir", required=True, help="Directory of metadata file")
    args = argparser.parse_args()

    meta_dir = args.meta_dir
    stat_from_metadata(meta_dir)
