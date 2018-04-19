import cPickle
import sys
import json
from doc2words import extract_words
from docreader import DocumentStreamReader
from vocabulary import Vocabulary


def create_index(args):
    reader = DocumentStreamReader(args[1:])
    if args[0] == 'varbyte':
        vocabulary = Vocabulary()
        for doc in reader:
            for word in extract_words(doc.text):
                vocabulary.append(word, doc.url)
        size = 10 ** 6
        offset = [0 for _ in range(size)]
        words = [[] for _ in range(size)]
        with open('id2url.pkl', 'wb') as id2url:
            cPickle.dump(vocabulary.url_from_id, id2url)
        for term in vocabulary.url_ids.keys():
            bucket = hash(term) % size
            words[bucket].append((term, vocabulary.url_ids[term]))
        with open('vocabulary.pkl', 'wb') as index_file:
            cur_size = 0
            for bucket in range(size):
                offset[bucket] = cur_size
                bucket_str = '['
                for (w, v) in words[bucket]:
                    bucket_str += '(' + json.dumps(w) + ',' + json.dumps(v.array.tolist()) + ')'
                bucket_str += ']'
                index_file.write(bucket_str)
                cur_size += len(bucket_str)
        with open('offsets.pkl', 'wb') as offsets_file:
                for i in range(size):
                    offsets_file.write(str(offset[i]) + '\n')

if __name__ == '__main__':
    create_index(sys.argv[1:])