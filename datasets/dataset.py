# Custom Dataset file for the music acces the note and the durations 
from torch.utils.data import Dataset
import torch
import numpy as np


from torch.utils.data import Dataset

class MusicDataset(Dataset):
    def __init__(self, data, seq_len):
        """
        data: list of tuples (note_idx, duration_idx)
        seq_len: length of input sequences
        """
        self.data = data
        self.seq_len = seq_len
        self.X, self.y_note, self.y_duration = self._apply_window()

    def __len__(self):
        return len(self.X)

    def __getitem__(self, index):
        return self.X[index], self.y_note[index], self.y_duration[index]

    def _apply_window(self):
        xs = []
        ys_notes = []
        ys_durations = []
        
        for i in range(len(self.data) - self.seq_len):
            seq = self.data[i : i + self.seq_len]                     # List of (note_idx, duration_idx)
            x = seq                                                  # input sequence
            y_note, y_duration = self.data[i + self.seq_len]         # target note and duration
            
            xs.append(x)
            ys_notes.append(y_note)
            ys_durations.append(y_duration)

        xs,ys_notes,ys_durations = np.array(xs), np.array(ys_notes), np.array(ys_durations)
        return torch.tensor(xs,dtype=torch.long),torch.tensor(ys_notes,dtype=torch.long),torch.tensor(ys_durations,dtype=torch.long)
