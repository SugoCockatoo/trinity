Trinity
│
├── Project
│   ├── name
│   ├── author
│   ├── version
│   ├── description
│   └── workspace
│
├── Data
│   ├── source
│   ├── type
│   ├── format
│   ├── split
│   ├── normalize
│   ├── shuffle
│   └── cache
│
├── Input
│   ├── image
│   ├── text
│   ├── audio
│   ├── video
│   ├── sequence
│   ├── database
│   ├── stream
│   └── user
│
├── Model
│   ├── mode
│   ├── type
│   ├── parameters
│   │   ├── input_size
│   │   ├── output_size
│   │   ├── hidden_size
│   │   ├── layers
│   │   ├── heads
│   │   ├── dropout
│   │   └── activation
│   │
│   └── Architecture
│       ├── Linear
│       ├── MLP
│       ├── CNN
│       ├── RNN
│       ├── LSTM
│       ├── Transformer
│       ├── GNN
│       ├── Diffusion
│       └── Custom
│
├── Train
│   ├── epochs
│   ├── batch_size
│   ├── learning_rate
│   ├── optimizer
│   ├── loss
│   ├── scheduler
│   ├── device
│   ├── checkpoint
│   └── save_every
│
├── Evaluate
│   ├── accuracy
│   ├── precision
│   ├── recall
│   ├── f1
│   ├── confusion_matrix
│   └── benchmark
│
├── Visualize
│   ├── architecture
│   ├── metrics
│   ├── loss
│   ├── accuracy
│   ├── weights
│   ├── gradients
│   ├── activations
│   ├── embeddings
│   └── dataset
│
├── Export
│   ├── path
│   ├── format
│   └── metadata
│
├── Convert
│   ├── ONNX
│   ├── TensorFlow
│   ├── Torch
│   ├── TFLite
│   ├── C++
│   └── Trinity
│
├── Deploy
│   ├── Desktop
│   ├── Server
│   ├── Mobile
│   ├── RaspberryPi
│   ├── ESP32
│   ├── Browser
│   └── Custom
│
├── Morph
│   ├── Prune
│   ├── Quantize
│   ├── Distill
│   ├── Compress
│   ├── Optimize
│   ├── Reshape
│   └── Transfer
│
└── Libraries
    │
    ├── trinity.data
    │   ├── load()
    │   ├── save()
    │   ├── split()
    │   ├── normalize()
    │   └── augment()
    │
    ├── trinity.model
    │   ├── create()
    │   ├── load()
    │   ├── save()
    │   ├── summary()
    │   └── inspect()
    │
    ├── trinity.train
    │   ├── start()
    │   ├── stop()
    │   ├── pause()
    │   └── resume()
    │
    ├── trinity.evaluate
    │   ├── accuracy()
    │   ├── precision()
    │   ├── recall()
    │   ├── f1()
    │   └── benchmark()
    │
    ├── trinity.visualize
    │   ├── graph()
    │   ├── plot()
    │   ├── render()
    │   └── show()
    │
    ├── trinity.convert
    │   ├── onnx()
    │   ├── tflite()
    │   ├── torch()
    │   └── tensorflow()
    │
    ├── trinity.deploy
    │   ├── desktop()
    │   ├── server()
    │   ├── mobile()
    │   ├── esp32()
    │   └── browser()
    │
    └── trinity.morph
        ├── prune()
        ├── quantize()
        ├── distill()
        ├── compress()
        └── optimize()