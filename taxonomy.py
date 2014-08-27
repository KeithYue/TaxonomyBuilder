# coding=utf-8
# build taxonomy using lists of isa pairs
import pickle
import logging
from utils import stop
from igraph import Graph, plot
from pymongo import MongoClient

test_pairs = [
        ('fruit', 'apple'),
        ('fruit', 'banana'),
        ('fruit', 'raspberry pi'),
        ('apple', 'Asia apple')
        ]

def add_vertex(g, name):
    '''
    add a vertext to the graph when possible
    '''
    try:
        g.vs.find(name)
    except ValueError:
        g.add_vertex(name=name)
    return


def add_edge(g, pair):
    source = g.vs.find(name=pair[0])
    target = g.vs.find(name=pair[1])
    if g.es.select(_source=source, _target=target):
        pass
    else:
        g.add_edge(*pair)
    return


class Taxonomy():
    '''
    The data structure for representing the taxonomy
    '''
    def __init__(self, name, pairs):
        '''
        para pairs: list of isa pairs
        '''
        self.name = name
        self._construct_g(pairs)
        return

    def __str__(self):
        return str(self._graph)

    def _construct_g(self, pairs):
        g = Graph()
        for pair in pairs:
            sup, sub = pair
            add_vertex(g, sup)
            add_vertex(g, sub)
            add_edge(g, pair)
        self._graph = g
        return self

    def draw(self):
        layout = self._graph.layout("kamada_kawai")
        plot(self._graph, layout=layout)
        return

    def save(self):
        '''
        save the graph to the disk
        '''
        pickle.dump(self, open('./{}.graph'.format(self.name), 'wb'))
        return

    def save_as_triple(self):
        '''
        format the graph into triple representation
        '''

def data(_type='B'):
    '''
    get the pairs from the mongodb dataset
    '''
    client = MongoClient('127.0.0.1', port=27017)
    cursor = client['rm_taxonomy']['pairs'].find({'type': _type})
    cursor.batch_size(100)
    try:
        for document in cursor:
            logging.info('yielding {}, {}'.format(document['sup'], document['sub']))
            yield document['sup'], document['sub']
    finally:
        cursor.close()


def test():
    tax = Taxonomy('Computer_Science', data())
    tax.save()

    return

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    test()


