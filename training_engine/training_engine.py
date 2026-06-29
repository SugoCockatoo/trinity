import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# DEFINE architectures

class MyCNN(nn.Module):
    """
    Classic CNN for grid-like data (e.g., images, spectrograms).
    Expects input shape: (Batch, Channels, Height, Width), for example (32, 1, 28, 28)
    """
    def __init__(self, num_classes=10):
        self.features = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2), # Reduces 28x28 to 14x14
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)                     # Reduces 14x14 to 7x7
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(32 * 7 * 7, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        return self.classifier(self.features(x))


class MyRNN(nn.Module):
    """
    LSTM-based RNN for sequential data (e.g., text, time-series, audio).
    Expects input shape: (Batch, Sequence_Length, Input_Size) for example (32, 28, 28)
    """
    def __init__(self, input_size=28, hidden_size=64, num_layers=2, num_classes=10):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # batch_first=True means input/output tensors are provided as (batch, seq, feature)
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        # Forward pass through LSTM
        # out shape: (batch_size, sequence_length, hidden_size)
        out, _ = self.lstm(x)
        
        # Take the hidden state of the very last time step to make the prediction
        out = self.fc(out[:, -1, :])
        return out

# Setup Data

# MODIFY HERE
def train(MODEL_TYPE, BATCH_SIZE, NUM_CLASSES, EPOCHS):
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    # MODIFY HERE
    X_dummy = torch.randn(1000, 1, 28, 28) 
    y_dummy = torch.randint(0, NUM_CLASSES, (1000,))
    dataset = TensorDataset(X_dummy, y_dummy)
    train_loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    # Model iniT
    if MODEL_TYPE == 'CNN':
        print("Initializing CNN Architecture...")
        model = MyCNN(num_classes=NUM_CLASSES).to(DEVICE)
    elif MODEL_TYPE == 'RNN':
        print("Initializing RNN (LSTM) Architecture...")
        model = MyRNN(input_size=28, hidden_size=64, num_layers=2, num_classes=NUM_CLASSES).to(DEVICE)
    else:
        raise ValueError("Unsupported MODEL_TYPE. Choose 'CNN' or 'RNN'.")

    # opt
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # generic training loop MODIFY
    print(f"Starting training loop on device: {DEVICE}\n" + "-"*40)

    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for batch_idx, (inputs, labels) in enumerate(train_loader):
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
            
            if MODEL_TYPE == 'RNN':
                inputs = inputs.squeeze(1) 
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            # Track statistics
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
        epoch_loss = running_loss / len(train_loader)
        epoch_acc = 100. * correct / total
        print(f"Epoch [{epoch+1}/{EPOCHS}] - Loss: {epoch_loss:.4f} - Accuracy: {epoch_acc:.2f}%")
        return epoch_loss, epoch_acc, epoch
    print("-"*40 + "\nTraining Complete!")