# coding=utf-8
# the pattern part for sup-sub extraction
import re
import logging
from utils import stop
from pprint import pprint
from nltk.tokenize import word_tokenize
from nltk.sem import relextract
from nltk import pos_tag, ne_chunk

def such_as_np(s, np_sent):
    '''
    Given a np chunked sentences, try to extract the concepts

    X--set
    y--set
    '''
    X = set()
    Y = set()
    if re.findall(r'\bsuch\b\s\bas\b', s):
        # extract the such as pattern
        # logging.info(s)

        semi_pairs = relextract.tree2semi_rel(np_sent)
        reldicts = relextract.semi_rel2reldict(semi_pairs)
        # find the first such as
        logging.info(np_sent)
        # pprint(semi_pairs)
        # pprint(reldicts)
        # logging.info(len(reldicts))
        if len(reldicts) > 0:
            try:
                while 'such as' not in reldicts[0]['untagged_filler']:
                    reldicts.pop(0)


                X.add(reldicts[0]['subjsym'])
                Y.add(reldicts[0]['objsym'])

                reldicts.pop(0)

                # find the sub concept
                for reldict in reldicts:
                    if reldict['untagged_filler'] not in [',', 'and', 'or']:
                        Y.add(reldict['subjsym'])
                        break
                    Y.add(reldict['subjsym'])
                    Y.add(reldict['objsym'])
            except Exception as e:
                logging.error(e)
                logging.error(reldicts)
                logging.error('Original sentence: '+s)
        stop()
    return (X, Y)

def such_np_as(s, np_sent):
    '''
    extract the pattern such np as
    return (X, Y)
    '''
    X = set()
    Y = set()
    if re.findall(r'\bsuch\b\s(\w+\s)+\bas\b', s):
        logging.info(s)
    return (X, Y)

def test():
    pass

if __name__ == '__main__':
    test()
