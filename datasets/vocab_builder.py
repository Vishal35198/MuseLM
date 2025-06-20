from collections import Counter
# import torch
from datasets.data_utils import load_parsed_files


def vocab_builders(elements):
    counter = Counter()
    for seq in elements:
        counter.update(seq)

    vocab = {'<pad>': 0, '<unkn>': 1}
    idx = 2
    for element, count in counter.most_common():
        vocab[element] = idx
        idx += 1

    return vocab

def text_to_indices(text,vocab):
    """Converts text to toek from the vocab"""
    return [vocab[x] for x in text]

def invert_dict(vocab):
    inverted_dict = {}
    for keys,values in vocab:
        invert_dict[values] = keys
        
    return invert_dict

def indices_to_text(indices,vocab):
    """Converts indices to text reverse process"""
    inverted_dicts = invert_dict(vocab)
    if isinstance(indices,int):
        return [invert_dict[indices]]
    else:
        return [invert_dict[x] for x in indices]

