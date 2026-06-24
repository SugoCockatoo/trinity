import os

DATA_TYPES = ["image", "text", "audio", "video", "sequence", "database", "stream", "custom"]
MODEL_TYPES = ["linear", "mlp", "cnn", "rnn", "lstm", "transformer", "gnn", "diffusion", "custom"]
OPTIMIZERS = ["adam", "adamw", "sgd", "rmsprop"]
DEVICES = ["cpu", "gpu", "auto"]
CONVERT_TARGETS = ["onnx", "tflite", "torch", "tensorflow", "cpp"]
DEPLOY_TARGETS = ["desktop", "server", "mobile", "raspberry_pi", "esp32"]
MORPH_OPERATIONS = ["prune", "quantize", "distill", "compress", "optimize"]


class Project:
    def __init__(self, name, author=None, version=None, description=None, workspace=None, license=None):
        self.name = name
        self.author = author
        self.version = version
        self.description = description
        self.workspace = workspace
        self.license = license


class Data:
    def __init__(self, source, type, format=None, split=None, shuffle=False, normalize=False, cache=False, batch_size=None):
        self.source = source
        if type not in DATA_TYPES:
            raise ValueError(f"Unsupported data type: {type}")
        self.type = type
        self.format = format
        self.split = split
        self.shuffle = shuffle
        self.normalize = normalize
        self.cache = cache
        self.batch_size = batch_size


class Model:
    def __init__(self, type, mode="create", path=None, input_size=None, output_size=None, hidden_size=None, layers=None, heads=None, dropout=None, activation=None):
        if type not in MODEL_TYPES:
            raise ValueError(f"Unsupported model type: {type}")
        self.type = type
        if mode not in ["create", "load"]:
            raise ValueError(f"Unsupported model mode: {mode}")
        self.mode = mode
        self.path = path
        self.input_size = input_size
        self.output_size = output_size
        self.hidden_size = hidden_size
        self.layers = layers
        self.heads = heads
        self.dropout = dropout
        self.activation = activation


class Train:
    def __init__(self, epochs, batch_size=None, learning_rate=None, optimizer=None, loss=None, device="auto", checkpoint=False, save_every=None):
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        if optimizer and optimizer not in OPTIMIZERS:
            raise ValueError(f"Unsupported optimizer: {optimizer}")
        self.optimizer = optimizer
        self.loss = loss
        if device not in DEVICES:
            raise ValueError(f"Unsupported device: {device}")
        self.device = device
        self.checkpoint = checkpoint
        self.save_every = save_every


class Evaluate:
    def __init__(self, accuracy=False, precision=False, recall=False, f1=False, confusion_matrix=False):
        self.accuracy = accuracy
        self.precision = precision
        self.recall = recall
        self.f1 = f1
        self.confusion_matrix = confusion_matrix


class Visualize:
    def __init__(self, architecture=False, loss=False, metrics=False, weights=False, activations=False, dataset=False):
        self.architecture = architecture
        self.loss = loss
        self.metrics = metrics
        self.weights = weights
        self.activations = activations
        self.dataset = dataset


class Convert:
    def __init__(self, target, quantized=False, optimized=False):
        if target not in CONVERT_TARGETS:
            raise ValueError(f"Unsupported convert target: {target}")
        self.target = target
        self.quantized = quantized
        self.optimized = optimized


class Deploy:
    def __init__(self, target, address=None, port=None):
        if target not in DEPLOY_TARGETS:
            raise ValueError(f"Unsupported deploy target: {target}")
        self.target = target
        self.address = address
        self.port = port


class Morph:
    def __init__(self, operation, ratio=None, target=None, bits=None, teacher_model=None):
        if operation not in MORPH_OPERATIONS:
            raise ValueError(f"Unsupported morph operation: {operation}")
        self.operation = operation
        self.ratio = ratio
        self.target = target
        self.bits = bits
        self.teacher_model = teacher_model


class Trinity:
    def __init__(self, project, data=None, model=None, train=None, evaluate=None, visualize=None, convert=None, deploy=None, morph=None):
        if not isinstance(project, Project):
            raise TypeError("project must be an instance of the Project class")
        self.project = project
        self.data = data
        self.model = model
        self.train = train
        self.evaluate = evaluate
        self.visualize = visualize
        self.convert = convert
        self.deploy = deploy
        self.morph = morph
