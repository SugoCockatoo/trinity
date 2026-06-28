import re
import read
# Mapping exact matches for keywords to keep regex simple
KEYWORDS = {
    'Project': 'PROJECT', 'Data': 'DATA', 'Input': 'INPUT', 'Model': 'MODEL',
    'Architecture': 'ARCHITECTURE', 'Train': 'TRAIN', 'Evaluate': 'EVALUATE',
    'Visualize': 'VISUALIZE', 'Export': 'EXPORT', 'Convert': 'CONVERT',
    'Deploy': 'DEPLOY', 'Morph': 'MORPH', 'Libraries': 'LIBRARIES'
}

TOKEN_TYPES = [
    ('FLOAT',        r'\d+\.\d+'),            # Float values like 0.001
    ('INT',          r'\d+'),                 # Integer values like 50
    ('STRING',       r'"[^"\\]*(?:\\.[^"\\]*)*"'), # Quoted text strings
    ('IDENTIFIER',   r'[a-zA-Z_][a-zA-Z0-9_]*'),   # Properties, methods, architecture names
    
    # Structural Syntax
    ('ASSIGN',       r'='),
    ('COLON',        r':'),
    ('DOT',          r'\.'),
    ('LPAREN',       r'\('),
    ('RPAREN',       r'\)'),
    ('LBRACE',       r'\{'),
    ('RBRACE',       r'\}'),
    
    # Whitespace tracking
    ('NEWLINE',      r'\n'),
    ('SKIP',         r'[ \t]+'),
    ('MISMATCH',     r'.'),
]

def tokenize_trinity(code):
    master_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_TYPES)
    tokens = []
    
    for match in re.finditer(master_regex, code):
        kind = match.lastgroup
        value = match.group(kind)
        
        if kind == 'IDENTIFIER':
            # Check if the identifier is actually a reserved keyword
            kind = KEYWORDS.get(value, 'IDENTIFIER')
            tokens.append((kind, value))
        elif kind == 'INT':
            tokens.append(('INT', int(value)))
        elif kind == 'FLOAT':
            tokens.append(('FLOAT', float(value)))
        elif kind == 'STRING':
            tokens.append(('STRING', value.strip('"')))  # Strip quotes for clean text
        elif kind in ['SKIP', 'NEWLINE']:
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f"Unexpected character in Trinity file: '{value}'")
        else:
            tokens.append((kind, value))
            
    return tokens