import torch 
import numpy as np
import music21 as m21
from model import MuseLSTM
from fractions import Fraction

from datasets.data_utils import (
    load_parsed_files,
    get_clean_vocab,
)
from data_pipeline import (
    get_data,
    # create_sequence
)

#! HYPERPARAMETERS
SEQ_LEN = 50
BATCH_SIZE = 64

def sample_from_logits(logits, temperature=1.0):
    probs = torch.softmax(logits / temperature, dim=-1)[0].cpu().numpy()
    probs = probs / probs.sum()
    return np.random.choice(len(probs), p=probs)


class MusicGenerator:
    def __init__(self,note_vocab,duration_vocab,sequence_len):
        # checkpoint = torch.load(model_path)
        self.model = None
        self.note_vocab = note_vocab
        self.duration_vocab = duration_vocab
        self.note_reverse_vocab = {v:k for k,v in self.note_vocab.items()}
        self.duration_reverse_vocab = {v:k for k,v in self.duration_vocab.items()}
        self.sequence_len = sequence_len
        self.duration_type_map = {
            '16th': 0.25,
            'eighth': 0.5,
            'quarter': 1.0,
            'half': 2.0,
            'whole': 4.0
        }
        
    def generate_sequence(self,starting_sequnce,num_steps,temperature):
        """
        Args :
            starting seq is (2,50) in a numpy array 
            output is seq of (2,50+num_steps) in numpy array only
        This function will return the (encoded_note,encoded_duration) for num_steps
        """
        if self.model is None:
            self.model = MuseLSTM(note_vocab_size=len(self.note_vocab),durations_vocab_size=len(self.duration_vocab))
    
        for i in range(num_steps):
            # get the curr_seq that is last 50 notes and durations 
            curr_sequence = torch.tensor(starting_sequnce[:,-self.sequence_len:])
            curr_sequence = curr_sequence.unsqueeze(0)
            with torch.no_grad():
                # print(f"Number of generation step taken {i}")
                note_logits ,duration_logits = self.model(curr_sequence)
                
            note_idx = sample_from_logits(note_logits)
            print(self.note_reverse_vocab[note_idx])
            # print(f"notes logits {note_logits.shape} note vocab size is {len(self.note_vocab)}")
            # print(note_idx,len(self.note_vocab))
            # print(f"Duration logits {duration_logits.shape} durations vocab sze is {len(self.duration_vocab)}")
            duration_idx = sample_from_logits(duration_logits)
            print(self.duration_reverse_vocab[duration_idx])
            # print(duration_idx,len(durations_vocab))
            new_column = np.array([[note_idx], [duration_idx]])  # shape (2, 1)
            starting_sequnce = np.concatenate((starting_sequnce, new_column), axis=1)
            
        return starting_sequnce
    def _parse_duration(self, dur_str):
        """Convert duration string to music21 Duration object"""
        try:
            if '/' in dur_str:
                return m21.duration.Duration(float(Fraction(dur_str)))

            return m21.duration.Duration(float(dur_str))
        except (ValueError, TypeError):
            # Fallback to quarter note
            return m21.duration.Duration(1.0)
        
    def sequence_to_midi(self,sequence,output_path="output.mid",tempo = 120):
        stream = m21.stream.Stream()
        stream.append(m21.tempo.MetronomeMark(number=tempo))
        sequence = sequence.T
        
        decode_sequence = [
            (self.note_reverse_vocab[note_idx],self.duration_reverse_vocab[duration_idx])
            for note_idx,duration_idx in sequence
        ]
        
        for note_str,duration_str in decode_sequence:
            if note_str == "rest":
                n = m21.note.Rest()
            else:
                n = m21.note.Note(note_str)
                
            n.duration = self._parse_duration(duration_str)
            stream.append(n)
            
        stream.write("midi",fp = output_path)
        print("Generation complete ✅")
        
    def generate_and_save(self,starting_sequence,num_steps=50,temperature=1.0,tempo=120):
        sequence = self.generate_sequence(starting_sequence,num_steps=num_steps,temperature=temperature)
        self.sequence_to_midi(sequence=sequence,tempo=tempo)
        


notes,durations = load_parsed_files("parsed_clean_data")
notes_vocab,_ = get_clean_vocab(notes)
durations_vocab,_ = get_clean_vocab(durations)
data = get_data(notes=notes,durations=durations,notes_vocab=notes_vocab,duration_vocab=durations_vocab)

data = np.array(data)
# (9290, 2, 51) (points,(notes,durations),sequ_len)
# X,y_notes,y_durations = create_sequence(data,SEQ_LEN)
# X -> (9290,2,50)
# y_notes -> (9290,)

#! SAMPLE FROM THE DATA WE HAVE TO GENERATE...
sample = data[0][:,:50]

generator = MusicGenerator(
    note_vocab = notes_vocab,
    duration_vocab = durations_vocab,
    sequence_len = SEQ_LEN,
)
generator.generate_and_save(
    starting_sequence = sample,
    num_steps=50,
    temperature=1.0,
    tempo=140,
)
                
      
            
            
        
        
    