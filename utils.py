# coding=utf-8
# help functions
import logging
def stop():
    a = input()
    return

def show_np(t):
    # given a chuncked sentences, print all np
    for sub_t in t.subtrees():
        if sub_t.label() == 'NP':
            logging.info(sub_t)
    return

def clean_sent(sent):
    '''
    given a sentence, clean the unexcepted whitespace
    '''
    remap = {
            ord('\t'): ' ',
            ord('\f'): ' ',
            ord('\r'): None # Delete
            }
    result = sent.translate(remap)
    return result

def test():
    s = 'pýtĥöñ\fis\tawesome\r\n'
    print(clean_sent(s))
    return

if __name__ == '__main__':
    test()

