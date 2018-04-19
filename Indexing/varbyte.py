import numpy

class DistList:
    def append(self, x):
        arr = []
        while x > 127:
            cur = numpy.int8(x & ((1 << 7) - 1))
            x >>= 7
            arr.append(cur)
        arr.append(numpy.int8(1 << 7) | x)
        self.array = numpy.concatenate([self.array, numpy.uint8(arr)])

    def __init__(self, elements=None):
        if elements is None:
            self.array = numpy.zeros((0,), dtype=numpy.int8)
        else:
            self.array = numpy.array(elements)

    def __iter__(self):
        cur_element = 0
        deg = 0
        for element in self.array:
            if bool(element & (1 << 7)):
                cur_element |= (element ^ (1 << 7)) << deg
                yield cur_element
                cur_element = 0
                deg = 0
            else:
                cur_element |= (element << deg)
                deg += 7


def iterate(elements):
    vb = VarByte(elements)
    return vb.__iter__()


class VarByte(DistList):
    def __init__(self, elements=None):
        self.last = 0
        DistList.__init__(self, elements)
    def __iter__(self):
        cur = 0
        for dist in DistList.__iter__(self):
            cur = cur + dist
            yield cur
    def append(self, elem):
        DistList.append(self, elem - self.last)
        self.last = elem