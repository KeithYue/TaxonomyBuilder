# coding=utf-8
# tools for extracting relationships
import re
import nltk
import logging
from collections import defaultdict
from nltk.sem.relextract import extract_rels, tree2semi_rel, semi_rel2reldict
from pprint import pprint
from KMP import subsequence
from utils import stop

gap_limit = 3


def change_pos(pos_sent):
    '''
    given a list of pos tagged sentence, change the pos tag for work 'other'
    change other POS to CC
    '''
    r = []
    for word, tag in pos_sent:
        if word in ['other', 'including', 'such', 'as']:
            tag = 'CC'
        r.append((word, tag))
    return r

def is_hp_pattern(s):
    '''
    justify whether a sentence is suitable for Hearst pattern
    '''
    hp_pattern = re.compile(r'''
    \bsuch\b\s\bas\b|
    # such as
    \bsuch\b\s(?:\w+\s)+\bas\b\s|
    # such as
    \band\b\s\bother\b|
    # and other
    \bor\b\s\bother\b|
    # or other
    \bincluding\b| # the including pattern
    \bespecially\b # the especially pattern
            ''', re.X)

    if re.findall(hp_pattern, s):
        return True
    else:
        return False

def such_as(rel_dicts):
    '''
    given the relation structure, try to extract the sup and sub candidates
    '''
    X = set()
    Y = set()
    i = 0
    for i in range(0, len(rel_dicts)):
        # pprint(rel)
        if subsequence(['such', 'as'], rel_dicts[i]['gap']) > -1:
            X.add(' '.join(rel_dicts[i]['lnp']))
            Y.add(' '.join(rel_dicts[i]['rnp']))
            i += 1
            while i < len(rel_dicts):
                if len(rel_dicts[i]['gap']) < gap_limit:

                    gap_indicator = defaultdict(bool)
                    gap_indicator[','] = ',' in rel_dicts[i]['gap']
                    gap_indicator['and'] = 'and' in rel_dicts[i]['gap']
                    gap_indicator['or'] = 'or' in rel_dicts[i]['gap']
                    # logging.info(gap_indicator)

                    if any(gap_indicator[k] for k in gap_indicator.keys()):
                        Y.add(' '.join(rel_dicts[i]['lnp']))
                        Y.add(' '.join(rel_dicts[i]['rnp']))
                    if gap_indicator['and'] or gap_indicator['or']:
                        break
                    i += 1
                else:
                    break
            break


    return X, Y

def such_np_as(rel_dicts):
    X = set()
    Y = set()
    # pprint(rel_dicts)
    if len(rel_dicts) < 3:
        return X, Y

    for i in range(1, len(rel_dicts)):
        if 'such' in rel_dicts[i-1]['gap'] and 'as' in rel_dicts[i]['gap']:
            X.add(' '.join(rel_dicts[i]['lnp']))
            Y.add(' '.join(rel_dicts[i]['rnp']))
            # logging.info(X)
            # logging.info(Y)
            i += 1
            while i < len(rel_dicts):
                if len(rel_dicts[i]['gap']) < gap_limit:

                    gap_indicator = defaultdict(bool)
                    gap_indicator[','] = ',' in rel_dicts[i]['gap']
                    gap_indicator['and'] = 'and' in rel_dicts[i]['gap']
                    gap_indicator['or'] = 'or' in rel_dicts[i]['gap']
                    # logging.info(gap_indicator)

                    if any(gap_indicator[k] for k in gap_indicator.keys()):
                        Y.add(' '.join(rel_dicts[i]['lnp']))
                        Y.add(' '.join(rel_dicts[i]['rnp']))
                    if gap_indicator['and'] or gap_indicator['or']:
                        break
                    i += 1
                else:
                    break
            break


    return X, Y

def and_other(rel_dicts):
    '''
    try to extract and other relationship
    '''
    X = set()
    Y = set()
    i = 0
    # pprint(rel_dicts)
    for i in range(0, len(rel_dicts)):
        if subsequence(['and', 'other'], rel_dicts[i]['gap']) > -1 or subsequence(['or', 'other'], rel_dicts[i]['gap']) > -1:
            X.add(' '.join(rel_dicts[i]['rnp']))
            Y.add(' '.join(rel_dicts[i]['lnp']))

            i = i - 1
            while i > -1:
                logging.info(rel_dicts[i]['gap'])
                if len(rel_dicts[i]['gap']) < gap_limit:
                    gap_indicator = defaultdict(bool)
                    gap_indicator[','] = ',' in rel_dicts[i]['gap']
                    # logging.info(gap_indicator)
                    if any(gap_indicator[key] for key in gap_indicator.keys()):
                        Y.add(' '.join(rel_dicts[i]['lnp']))
                        Y.add(' '.join(rel_dicts[i]['rnp']))
                    else:
                        break
                    i -= 1
                else:
                    break
            break

    return X, Y

def word_pattern(word):
    '''
    return a pattern method by a word(including, especially)
    '''
    def word_pat(rel_dicts):
        X = set()
        Y = set()
        i = 0
        # pprint(rel_dicts)
        for i in range(0, len(rel_dicts)):
            if  rel_dicts[i]['gap'] in ([word], [',', word]):
                # logging.info(rel_dicts[i]['lnp'])
                # logging.info(rel_dicts[i]['gap'])
                # logging.info(rel_dicts[i]['rnp'])
                X.add(' '.join(rel_dicts[i]['lnp']))
                Y.add(' '.join(rel_dicts[i]['rnp']))
                i += 1
                while i < len(rel_dicts):
                    if len(rel_dicts[i]['gap']) < gap_limit:

                        gap_indicator = defaultdict(bool)
                        gap_indicator[','] = ',' in rel_dicts[i]['gap']
                        gap_indicator['and'] = 'and' in rel_dicts[i]['gap']
                        gap_indicator['or'] = 'or' in rel_dicts[i]['gap']
                        # logging.info(gap_indicator)

                        if any(gap_indicator[k] for k in gap_indicator.keys()):
                            Y.add(' '.join(rel_dicts[i]['lnp']))
                            Y.add(' '.join(rel_dicts[i]['rnp']))
                        if gap_indicator['and'] or gap_indicator['or']:
                            break
                        i += 1
                    else:
                        break
                break
        return X, Y

    return word_pat

def equality_pattern(rel_dicts):
    '''
    given the list of relations

    by now the equality is defined as A, B or/and C


    return a list of equality pairs
    '''
    equality_sign = [['and'], ['or'], [','], [',', 'and']]
    pairs = []
    equality_list = list() # list ot set
    overlap = [] # list of 0,1 0 means there is no overlap between this one and the next one, and 1 indicates there is overlap between this one and next one
    for rel in rel_dicts:
        if any(subsequence(s, rel['gap']) > -1  for s in equality_sign) and len(rel['gap']) < gap_limit:
            pairs.append((' '.join(rel['lnp']), ' '.join(rel['rnp'])))

    # logging.info(pairs)
    if len(pairs) < 2:
        return equality_list
    else:
        i = 0
        # using the greedy algorithm, just find one is enough
        while i < len(pairs) - 1:
            # logging.info(i)
            if pairs[i][1] == pairs[i+1][0]:
                results = set()
                # pprint(rel_dicts)
                results.update(pairs[i])
                results.update(pairs[i+1])

                # keep going for next try
                i += 1
                while i < len(pairs) - 1:
                    if pairs[i][1] == pairs[i+1][0]:
                        results.update(pairs[i])
                        results.update(pairs[i+1])
                        i += 1
                    else:
                        break
                equality_list.append(results)
            i += 1
        return equality_list



def test():
    s = 'I know you a friend such a friend as a girl.'
    s = 'Bruises, wounds, broken bones and other injuries'
    s = 'I like all common-law countries, including Canada and England'
    s = 'I like most European countries, especially France, England, and Spain.'
    print(is_hp_pattern(s))
    return


isa_patterns = (such_as, and_other, such_np_as, word_pattern('including'), word_pattern('especially'))

equality_patterns = (equality_pattern, )




if __name__ == '__main__':
    test()
