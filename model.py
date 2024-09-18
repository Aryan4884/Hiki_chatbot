import torch
import torch.nn as nn

class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes, dropout_prob=0.5):
        super(NeuralNet, self).__init__()
        # Define layers
        self.l1 = nn.Linear(input_size, hidden_size)  # First Linear Layer
        self.l2 = nn.Linear(hidden_size, hidden_size)  # Second Linear Layer
        self.l3 = nn.Linear(hidden_size, num_classes)  # Output Layer
        self.relu = nn.ReLU()  # Activation Function
        self.dropout = nn.Dropout(p=dropout_prob)  # Dropout Layer
    
    def forward(self, x):
        x = x.float()  # Ensure input is float32
        out = self.l1(x)  # First Layer
        out = self.relu(out)  # Activation
        out = self.dropout(out)  # Dropout
        out = self.l2(out)  # Second Layer
        out = self.relu(out)  # Activation
        out = self.dropout(out)  # Dropout
        out = self.l3(out)  # Output Layer
        
        return out
