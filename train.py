import torch
import torch.optim as optim
from torch.utils.data import DataLoader
from datasets.dataset import MusicDataset

import torch.nn as nn
import numpy as np
from collections import defaultdict
from model import MuseLSTM

from data_pipeline import (
    get_long_data,
)
from datasets.transformer_utils import (
    load_parsed_files,
    get_clean_vocab
)

SEQ_LEN = 50
BATCH_SIZE = 64

notes,durations = load_parsed_files("parsed_clean_data")
notes_vocab,_ = get_clean_vocab(notes)
durations_vocab,_ = get_clean_vocab(durations)
data = get_long_data(notes=notes,durations=durations,notes_vocab=notes_vocab,duration_vocab=durations_vocab)


train_ds = MusicDataset(data=data,seq_len=SEQ_LEN)
# print(len(train_ds))
train_dl = DataLoader(train_ds,batch_size=BATCH_SIZE)
# X Size is torch.Size([64, 50, 2])
# y_note Size is torch.Size([64])
# y_duration Size is torch.Size([64])

note_vocab_size = len(notes_vocab)
durations_vocab_size = len(durations_vocab)


model = MuseLSTM(note_vocab_size=note_vocab_size,durations_vocab_size=durations_vocab_size)

criterion_note = nn.CrossEntropyLoss()
criterion_durations = nn.CrossEntropyLoss()

optimizer = optim.Adam(model.parameters(),lr=0.002)

num_epochs = 50
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model.to(device=device)

from tqdm import tqdm
import torch
import os

def train_muselstm(model, train_dl, optimizer, criterion_note, criterion_durations,
                   num_epochs, device, checkpoint_path="checkpoints/", save_every=5):
    
    os.makedirs(checkpoint_path, exist_ok=True)
    epoch_losses = []

    for epoch in range(num_epochs):
        print(f"\n🎼 Epoch {epoch+1}/{num_epochs} — Training Started")
        model.train()
        total_loss = 0

        loop = tqdm(train_dl, desc="Batch Progress", leave=False)

        for batch_x, batch_y_note, batch_y_durations in loop:
            batch_x = batch_x.to(device)
            batch_y_note = batch_y_note.long().to(device)
            batch_y_durations = batch_y_durations.long().to(device)

            optimizer.zero_grad()

            note_logits, duration_logits = model(batch_x)

            loss_note = criterion_note(note_logits, batch_y_note)
            loss_duration = criterion_durations(duration_logits, batch_y_durations)

            loss = loss_note + loss_duration
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            loop.set_postfix(loss=loss.item())

        avg_loss = total_loss / len(train_dl)
        print(f"✅ Epoch {epoch+1} Complete — Loss: {avg_loss:.4f}")
        epoch_losses.append(avg_loss)

        # Save checkpoint
        if (epoch + 1) % save_every == 0:
            checkpoint_file = os.path.join(checkpoint_path, f"model_epoch_{epoch+1}.pt")
            torch.save(model.state_dict(), checkpoint_file)
            print(f"💾 Checkpoint saved at: {checkpoint_file}")

    return epoch_losses

losses = train_muselstm(
    model=model,
    train_dl=train_dl,
    optimizer=optimizer,
    criterion_note=criterion_note,
    criterion_durations=criterion_durations,
    num_epochs=2,
    device=device
)

import matplotlib.pyplot as plt

plt.plot(losses, label="Training Loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.title("MuseLSTM Training Loss Over Time")
plt.legend()
plt.grid(True)
plt.show()

        
    