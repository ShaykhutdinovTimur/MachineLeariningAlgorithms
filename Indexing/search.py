import cPickle as pickle
import re
import json
from varbyte import iterate
import mmap
import os.path

size = 10**6

class Conjunction:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self, index_path, offsets):
        l = self.left.evaluate(index_path, offsets)
        r = self.right.evaluate(index_path, offsets)
        try:
            lv = next(l)
            rv = next(r)
            while True:
                if lv < rv:
                    lv = next(l)
                elif lv > rv:
                    rv = next(r)
                else:
                    yield lv
                    lv = next(l)
                    rv = next(r)
        except StopIteration:
            return


class Variable:
    def __init__(self, name):
        self.name = name
        self.value = name

    def evaluate(self, index_path, offsets):
        term = self.name
        bucket = hash(term) % size
        begin = offsets[bucket]
        if bucket != size - 1:
            length = offsets[bucket + 1] - begin
        else:
            length = os.path.getsize(index_path) - begin
        if length < 3:
            return iterate(None)
        with open(index_path, 'r+b') as index_file:
            mm = mmap.mmap(index_file.fileno(), 0)
            data = mm[begin:begin + length]
        m = {}
        data = data[1:len(data) - 2]
        for p in data.split(')'):
            w, v = p.split(',[')
            w = json.loads(w[1:])
            m[w] = json.loads('[' + v)
        return iterate(m[term])

def parse_query(q):
    tokens = re.findall(r'\w+|[\(\)&\|!]', q, re.UNICODE)
    result = Variable(tokens[0])
    tokens = tokens[1:]
    while len(tokens) > 0:
        result = Conjunction(Variable(tokens[1]), result)
        tokens = tokens[2:]
    return result


def search():
    with open('id2url.pkl', 'rb') as id2url:
        url_from_id = pickle.load(id2url)
    with open('offsets.pkl', 'rb') as offsets_file:
        offset = []
        lines = offsets_file.readlines()
        for line in lines:
            offset.append(int(line))
    while True:
        try:
            initial_query = raw_input()
            query = initial_query.decode('utf-8').lower()
            if query == '':
                return
            urls = parse_query(query).evaluate('vocabulary.pkl', offset)
            answer = map(url_from_id.__getitem__, urls)
            l = len(answer)
            print(initial_query)
            print(l)
            print('\n'.join(map(str, answer)))
        except EOFError:
            return


if __name__ == '__main__':
    search()