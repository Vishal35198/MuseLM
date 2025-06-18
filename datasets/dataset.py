# Custom Dataset file for the music acces the note and the durations 
from torch.utils.data import Dataset
import torch

class MusicDataset(Dataset):
    
    def __init__(self,X,y_note,y_durations):
        self.X = X
        self.y_note = y_note
        self.y_duration = y_durations
        
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, index):
        return self.X[index],self.y_note[index],self.y_duration[index]
    