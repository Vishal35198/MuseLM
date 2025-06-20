from collections import defaultdict
import numpy as np

def read_from_files(path):
    with open(path,'r') as file:
        data = file.read().splitlines()
        
    return data


def get_data(notes,durations,notes_vocab,duration_vocab):
    """
    Returns the data in shape -> # (9290, 2, 51) (points,(notes,durations),sequ_len)
    """
    encoded_notes = []
    for note_str in notes:
        note_str_list = note_str.split(" ")
        note_str_encoded = []
        for note in note_str_list:
            note_str_encoded.append(notes_vocab[note])
        encoded_notes.append(note_str_encoded)
            
    encoded_durations = []
    for dur_str in durations:
        dur_str_list = dur_str.split(" ")
        dur_str_encoded = []
        for dur in dur_str_list:
            dur_str_encoded.append(duration_vocab[dur])
        encoded_durations.append(dur_str_encoded)
            
    data = list(zip(encoded_notes,encoded_durations))
    return data
        
def get_long_data(notes,durations,notes_vocab,duration_vocab):
    """
    Return the data in shape -> (total_points,(encoded_notes,encoded_duration))
    (139000,2)
    """
    encoded_notes = []
    for note_str in notes:
        note_str_list = note_str.split(" ")
        for note in note_str_list:
            encoded_notes.append(notes_vocab[note])
            
    encoded_durations = []
    for dur_str in durations:
        dur_str_list = dur_str.split(" ")
        for dur in dur_str_list:
            encoded_durations.append(duration_vocab[dur])
            
    data = list(zip(encoded_notes,encoded_durations))
    return data
    

