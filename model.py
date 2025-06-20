import torch 
import torch.nn as nn

class MuseLSTM(nn.Module):
    def __init__(self,note_vocab_size,durations_vocab_size,embed_dim = 128,hidden_dim = 256):
        super().__init__()
        
        # Embeddings layers 
        self.note_embed = nn.Embedding(note_vocab_size,embed_dim)
        self.durations_embed = nn.Embedding(durations_vocab_size,embed_dim)
        
        # LSTM Model
        self.lstm = nn.LSTM(embed_dim*2,hidden_dim,batch_first=True)
        
        # Outputs Heads
        self.note_out = nn.Linear(hidden_dim,note_vocab_size)
        self.durations_out = nn.Linear(hidden_dim,durations_vocab_size)
        
    def forward(self,x):
        note_embed = self.note_embed(x[:,:,0])
        durations_embed = self.durations_embed(x[:,:,1])
        combined = torch.cat([note_embed,durations_embed],dim=-1)
        
        lstm_out,_ = self.lstm(combined)
        
        last_lstm_out = lstm_out[:,-1,:]
        
        # predict the next note and durations 
        note_logits = self.note_out(last_lstm_out)
        durations_logits = self.durations_out(last_lstm_out)
        
        return note_logits,durations_logits