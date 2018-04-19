from varbyte import VarByte


class Vocabulary:
    def __init__(self):
        self.url_ids = {}
        self.last_url = {}
        self.id_from_url = {}
        self.url_from_id = {}

    def __getitem__(self, term):
        if term not in self.url_ids:
            return []
        return self.url_ids[term]

    def urls_count(self):
        return len(self.id_from_url)

    def append(self, term, url):
        if url not in self.id_from_url:
            length = len(self.id_from_url)
            self.url_from_id[length] = url
            self.id_from_url[url] = length
        url_id = self.id_from_url[url]
        if term not in self.url_ids:
            self.url_ids[term] = VarByte()
            self.last_url[term] = -1
        if self.last_url[term] != url_id:
            self.last_url[term] = url_id
            self.url_ids[term].append(url_id)