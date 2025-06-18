import torch
import torch.optim as optim
from torch.utils.data import DataLoader
from datasets.dataset import MusicDataset

import torch.nn as nn
import numpy as np
from collections import defaultdict
from model import MuseLSTM

with open("notes.txt",'r') as file:
    notes = file.read().splitlines()
    
with open("durations.txt",'r') as file:
    durations = file.read().splitlines()
    
# data = list(zip(notes,durations))

def build_vocab(items):
    vocab = defaultdict(int)
    reverse_vocab = {}
    for idx,item in enumerate(sorted(set(items))):
        vocab[item] = idx
        reverse_vocab[idx] = item
    
    return vocab,reverse_vocab

notes_list = notes[0].split(" ")
durations_list = durations[0].split(" ")
note_vocab,note_reverse_vocab = build_vocab(notes_list)
durations_vocab,durations_reverse_vocab = build_vocab(durations_list)

encode_note = [note_vocab[x] for x in notes_list]
encode_durations = [durations_vocab[x] for x in durations_list]

data = list(zip(encode_note,encode_durations)) # return a tuple object with note,durations

def create_sequence(data,seq_len):
    xs = []
    ys_note = []
    ys_duration = []
    
    for i in range(len(data) - seq_len):
        x = data[i:i+seq_len]
        y_note = data[i+seq_len][0]
        y_duration = data[i+seq_len][1]
        
        xs.append(x)
        ys_note.append(y_note)
        ys_duration.append(y_duration)
    
    return np.array(xs),np.array(ys_note),np.array(ys_duration)

SEQ_LEN = 50
BATCH_SIZE = 64

X,y_notes,y_durations = create_sequence(data,SEQ_LEN)

# convert them to tensor and load them into the dataloader 
X = torch.tensor(X, dtype=torch.long).permute(0,2,1)
y_notes = torch.tensor(y_notes, dtype=torch.long)
y_durations = torch.tensor(y_durations, dtype=torch.long)
print(X.shape)
print(y_notes.shape)
print(y_durations.shape)

train_ds = MusicDataset(X = X,y_note= y_notes,y_durations=y_durations)

train_dl = DataLoader(train_ds,batch_size=BATCH_SIZE)

note_vocab_size = len(note_vocab)
durations_vocab_size = len(durations_vocab)


model = MuseLSTM(note_vocab_size=note_vocab_size,durations_vocab_size=durations_vocab_size)

criterion_note = nn.CrossEntropyLoss()
criterion_durations = nn.CrossEntropyLoss()

optimizer = optim.Adam(model.parameters(),lr=0.002)

num_epochs = 50
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model.to(device=device)

for epoch in range(num_epochs):
    print("training started")
    model.train()
    total_loss = 0
    
    for batch_x,batch_y_note,batch_y_durations in train_dl:
        batch_x = batch_x.to(device)
        batch_y_note = batch_y_note.long()
        batch_y_note = batch_y_note.to(device)
        batch_y_durations = batch_y_durations.to(device)
        
        optimizer.zero_grad()
        
        note_logits,duration_logits = model(batch_x)
        
        loss_note = criterion_note(note_logits,batch_y_note)
        loss_duration = criterion_durations(duration_logits,batch_y_durations)
        loss = loss_note + loss_duration
        
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        
    print(f"Epochs {epoch+1} , Loss {total_loss / len(train_dl)}")
    

        
    