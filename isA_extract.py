# coding=utf-8
# extract is a pair from a list of corpus
import nltk
import re
import logging
from collections import defaultdict
from nltk.tree import Tree
from textblob import TextBlob
from KMP import subsequence
from nltk.tokenize import word_tokenize
from nltk.sem import relextract
from nltk import pos_tag, ne_chunk
from data import data, Sent, save
from utils import stop, show_np, clean_sent
from pprint import pprint
from patterns import such_as_np, such_np_as
from extract_rel import is_hp_pattern, isa_patterns, change_pos, equality_patterns


# multiprocess module
import os
from multiprocessing import Pool

def muilti_test(s):
    print('I am invoked')
    return

NP_PATTERN = r'''
    NP:
        {<VBG><NN.*>}
        {<VBN><NN.*>}
        {<PP\$>?<JJ.*>*<NN(.*)?>+}
        {<VBG>}
'''

NLTK_HEARST = (such_as_np, )


def convert_leaves_to_list(leaves):
    r = []
    for node in leaves:
        if isinstance(node, str):
            r.append(node)
        else:
            r.append(node[0])
    return r


def pair2rel(pairs):
    '''
    conver list(pair(list(str), np_tree)) to relation dictionaries

    -->list(dict), left_gap, left_np, gap, right np, right gap
    '''
    relations = []
    relations_new = []
    while len(pairs) > 1:
        rel = defaultdict(list)
        rel['lcon'] = pairs[0][0]
        rel['lnp'] = pairs[0][1].leaves()
        rel['gap'] = pairs[1][0]
        rel['rnp'] = pairs[1][1].leaves()
        if len(pairs) > 2:
            rel['rcon'] = pairs[2][0]
        else:
            rel['rcon'] = []
        for key in rel.keys():
            rel[key] = convert_leaves_to_list(rel[key])

        relations.append(rel)
        pairs.pop(0)
    return relations


def _build_tree_from_nps(tokens, nps):
    '''
    build nltk Tree from tokens and nps

    tokens: list of tokens
    nps: list of noun phrases
    '''
    tokens = [t.lower() for t in tokens]
    result = []
    list_np_tokens = []
    for np in nps:
        list_np_tokens.append(np.split())
    # build nested list
    # logging.info(list_np_tokens)
    while len(list_np_tokens)>0:
        nps_tokens = list_np_tokens.pop(0)
        s_index = subsequence(nps_tokens, tokens)

        result.extend(tokens[:s_index])
        result.append(nps_tokens)

        tokens = tokens[s_index+len(nps_tokens):]

    result.extend(tokens)

    tree_list = []
    for ele in result:
        if isinstance(ele, str):
            tree_list.append(ele)
        else:
            tree_list.append(Tree('NP', ele))
    np_chunk = Tree('S', tree_list)
    return np_chunk

def extract_relations(s, chunk_type = 'np'):
    '''
    given a sentence, extract the list of relations

    chunk_type: define the chunked type among all relations, 'np'|'ne'
    '''
    s = clean_sent(s)
    tokens = word_tokenize(s)
    # add the an NP to resolve the NLTK relationship BUG
    pos_sent = pos_tag(tokens)
    pos_sent = change_pos(pos_sent)

    cp = nltk.RegexpParser(NP_PATTERN)
    np_sent = cp.parse(pos_sent)
    # pprint(np_sent)

    nps = TextBlob(s).noun_phrases
    np_chunk = _build_tree_from_nps(tokens, nps)
    # pprint(nps)

    if chunk_type=='np':
        pairs = relextract.tree2semi_rel(np_sent)
        # pprint(len(pairs))
    elif chunk_type == 'ne':
        pairs = relextract.tree2semi_rel(nltk.ne_chunk(pos_sent))

    rel_dicts = pair2rel(pairs)
    # pprint(rel_dicts)
    # stop()
    return rel_dicts

def equal_extract(s):
    '''
    try to extract equal relations given a sentence
    '''
    pattern = equality_patterns[0]
    rel_dicts = extract_relations(s, 'np')
    return pattern(rel_dicts)

def syntactic_extraction(sent):
    '''
    given a sentence, using heast pattern to extraction information --> ([X], [Y])
    return the list of super concept cadidates and sub concept candidates
    '''
    try:
        index = sent.index
        s = sent.text
    except Exception as e:
        s  = sent

    pairs = []

    X = set()
    Y = set()
    s = s.strip()

    if not is_hp_pattern(s):
        return pairs
    # clean the sentence, this sentence may be hp pattern
    # stop()

    rel_dicts = extract_relations(s)

    for pattern in isa_patterns:
        cand_x, cand_y  = pattern(rel_dicts)
        if cand_x and cand_y:
            logging.info('_'*30)
            logging.info('From pattern: {}'.format(pattern.__name__))
            X.update(cand_x)
            Y.update(cand_y)


    if len(X)==1 and len(Y)>0:
        x = X.pop()
        for y in Y:
            isa_pair = (x, y)
            logging.info(isa_pair)
            pairs.append(isa_pair)
        # stop()
        # print(str(index)+':'+repr(X)+'----->'+repr(Y))

    # logging.info('Super concept is '+repr(X))
    # logging.info('Sub concept is '+repr(Y))
    # logging.info(pairs)
    # stop()
    return pairs

def sup_concept_extraction(X, Y, r):
    '''
    when len(X) > 2, return the identical super concept
    --> ONE super concept
    '''
    pass

def sub_concept_extraction(x, Y, r):
    '''
    extract the valid sub concept

    --> list of sub concept
    '''
    pass

def isA_extraction():
    '''
    S: sentences from web corpus that match the hearst pattern
    the main entry point for isA extractin

    --> set of isA pairs(x, y)
    '''
    # for sentence in S:
    #     syntactic_extraction(sentence)


    pool = Pool(20)
    tasks = []
    logging.info('loading the data......')
    for s in data():
        logging.info('getting {}'.format(s.index))
        tasks.append(s)
        # logging.info('added {}'.format(s[0]))
    logging.info('loading completed.')

    results = pool.map(generate_isa_pairs, tasks)
    pool.close()
    pool.join()
    logging.info('Complete!! There is total {} pairs'.format(len([x for x in results if x is True])))

    return

def generate_isa_pairs(s):
    logging.info('processing #{}, domain: {}'.format(s.index, s.domain))
    try:
        pairs = syntactic_extraction(s)
        for pair in pairs:
            document = {}
            # logging.info(pair)
            document['sup'], document['sub'] = pair
            document['type'] = s.domain
            document['location'] = s.index
            save(document)
    except Exception as e:
        logging.info(e)
        return False
    return True

def test():
    test_sent = Sent(1, 'These algorithms include distance calculations, scan conversion, closest point determination, fast marching methods, bounding box creation, fast and incremental mesh extraction, numerical integration and narrow band techniques.', 'D')
    test_s = [test_sent]
    # isA_extraction(data())
    for s in data('B'):
        syntactic_extraction(s)
    # with open(OUTPUT_DIR+'equal.txt', 'w', encoding='utf-8') as f:
    #     for s in data():
    #         # syntactic_extraction(s)
    #         # logging.info(s.text)
    #         r = equal_extract(s.text)
    #         for eq in r:
    #             logging.info(s.text)
    #             logging.info(eq)
    #             # f.write(s.text.strip())
    #             # f.write('\n')
    #             f.write('\t'.join(eq))
    #             f.write('\n')
    #             f.flush()
    #             # stop()
    # return
    return


OUTPUT_DIR = './demo/'

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    # logging.basicConfig(level=logging.DEBUG, filename='log_equal.txt', filemode='w')
    isA_extraction()
