# coding=utf-8
# this file is to provide access point to the data on the disk
import logging
from nltk.tokenize import sent_tokenize
from collections import namedtuple
from pymongo import MongoClient

Sent = namedtuple('Sent', ['index', 'text', 'domain'])

g_data_file = './data/data_taxonomy/lang_tag.txt'

def data(domain_type = 'B'):
    '''
    access the data on the disk, return the list of sentences

    domain_type: B or D
    '''
    index = 0
    with open(g_data_file, encoding='iso-8859-1') as f:
        for line in f:
            # for debug use of the small account
            # if index == 10:
            #     break
            _id,journal,year,title,abstract,domain,language = line.strip().split('\t')
            if language == 'english' and (domain=='D' or domain == 'B'):
                # yield sentences
                sentences = sent_tokenize(abstract.strip())
                for s in sentences:
                    yield Sent(index, s, domain) # add the index for refer to
                index += 1

def hearst_rel_sents():
    with open('./data/sentences.txt', 'w', encoding='utf-8') as f:
        for index, s in data():
            if any([x in s for x in ['such', 'and', 'or', 'including', 'especially']]):
                f.write(s.strip())
                f.write('\n')
    return

def save(document):
    '''
    save the document to the mongo database
    '''
    client = MongoClient(host='127.0.0.1', port=27017)
    try:
        logging.info(client['rm_taxonomy']['pairs'].insert(document))
    except Exception as e:
        logging.error(e)
    finally:
        client.close()
    return


def test():
    for sentence in data():
        print(sentence)
    return

if __name__ == '__main__':
    hearst_rel_sents()
