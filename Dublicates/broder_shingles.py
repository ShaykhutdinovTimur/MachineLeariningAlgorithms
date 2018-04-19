#!/usr/bin/env python

import sys
import re
import mmh3
from docreader import DocumentStreamReader
from itertools import combinations, ifilter, imap, izip
from collections import defaultdict


class MinshinglesCounter:
    SPLIT_RGX = re.compile(r'\w+', re.U)

    def __init__(self, window=5, n=20):
        self.window = window
        self.n = n

    def get_shingles_count(self):
        return self.n

    def count(self, text):
        words = MinshinglesCounter._extract_words(text)
        shs = self._count_shingles(words)
        mshs = self._select_minshingles(shs)

        if len(mshs) == self.n:
            return mshs

        if len(shs) >= self.n:
            return sorted(shs)[0:self.n]

        return None

    def _select_minshingles(self, shs):
        buckets = [None]*self.n
        for x in shs:
            bkt = x % self.n
            buckets[bkt] = x if buckets[bkt] is None else min(buckets[bkt], x)

        return filter(lambda a: a is not None, buckets)

    def _count_shingles(self, words):
        shingles = []
        for i in xrange(len(words) - self.window):
            h = mmh3.hash(' '.join(words[i:i+self.window]).encode('utf-8'))
            shingles.append(h)
        return sorted(shingles)

    @staticmethod
    def _extract_words(text):
        words = re.findall(MinshinglesCounter.SPLIT_RGX, text)
        return words


def duplicated_urls(argv):
    urls_count = defaultdict(int)
    for path in argv[1:]:
        for doc in DocumentStreamReader(path):
            urls_count[doc.url] += 1
    for url, cnt in urls_count.iteritems():
        if cnt > 1:
            print url + " " + url + " 1.0"

def get_docs(argv):
    urls_set = set()
    for path in argv[1:]:
        for doc in DocumentStreamReader(path):
            if doc.url not in urls_set:
                urls_set.add(doc.url)
                yield doc
    del urls_set

def urls_similarity(shingles):
    similarity = defaultdict(int)
    groups = defaultdict(list)
    for docs_group in izip(*shingles):
        for (url, shingle) in docs_group:
            groups[shingle].append(url)
    for _, urls in groups.iteritems():
        for url_i, url_j in combinations(sorted(urls), 2):
            similarity[(url_i, url_j)] += 1
    del groups
    return similarity


def jacquard(val, shin_count):
    if val > 20:
        return 1
    return val * 1.0 / (val + 2 * (shin_count - val))


def main():
    mhc = MinshinglesCounter()
    duplicated_urls(sys.argv)
    docs = get_docs(sys.argv)
    minshingles = imap(lambda document: (document.url, mhc.count(document.text)), docs)
    minshingles = ifilter(lambda (_, minshingle): minshingle is not None, minshingles)
    minshingles = imap(lambda (url, minshingle): [(url, shingle_ind) for shingle_ind in minshingle], minshingles)
    similarity = urls_similarity(minshingles)
    for (url_i, url_j), value in similarity.iteritems():
        measure_val = jacquard(value, mhc.get_shingles_count())
        if measure_val > 0.75:
            print url_i + " " + url_j + " " + str(measure_val)
    del similarity

if __name__ == '__main__':
    main()
