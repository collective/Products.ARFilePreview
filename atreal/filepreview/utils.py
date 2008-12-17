# -*- coding: utf-8 -*-

def chunk2gen(chunkedData):
    while not chunkedData is None:
        yield chunkedData.data
        chunkedData = chunkedData.next

def text2gen(Data):
    while len(Data):
        yield Data[:10000]
        Data = Data[10000:]

def chunk2ugen(chunkedData, charset):
    yield chunkedData.decode(charset, 'ignore')

def text2ugen(data, charset):
    while len(data):
        yield data[:10000].decode(charset)
        data = data[10000:]

def unicodegen(daddygen, charset):
    for data in daddygen:
        yield data.decode(charset)
