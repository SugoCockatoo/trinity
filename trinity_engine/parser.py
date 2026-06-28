# parser.py

from nodes import ProgramNode, BlockNode, AssignNode, CallNode

class TrinityParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0  # Our index finger pointing at the current token

    def current_token(self):
        """Looks at the token we are currently pointing to."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return ('EOF', None)

    def match(self, expected_kind):
        """Checks if the current token matches what we expect. 
        If it does, advance our index finger forward. If not, throw an error."""
        kind, value = self.current_token()
        if kind == expected_kind:
            self.pos += 1
            return value
        raise SyntaxError(f"Syntax Error: Expected token type '{expected_kind}', but got '{kind}' with value '{value}' at position {self.pos}")

    def parse(self):
        """The main entry point to parse the whole file."""
        statements = []
        while self.current_token()[0] != 'EOF':
            statements.append(self.parse_statement())
        return ProgramNode(statements)

    def parse_statement(self):
        """Figures out if the next line is a block configuration or a library method call."""
        kind, value = self.current_token()
        
        # If it's one of your primary configuration block keywords:
        if kind in ['PROJECT', 'DATA', 'INPUT', 'MODEL', 'TRAIN', 'EVALUATE', 'VISUALIZE', 'EXPORT', 'CONVERT', 'DEPLOY', 'MORPH']:
            return self.parse_block()
        
        # If it starts with a general identifier (like 'trinity'), it's a library call line:
        elif kind == 'IDENTIFIER':
            return self.parse_library_call()
        
        raise SyntaxError(f"Root level syntax error: Unexpected token '{value}' ({kind})")

    def parse_block(self):
        """Parses a structure like: Train { epochs = 100 }"""
        # 1. Grab the block keyword (e.g., 'Train')
        block_name = self.match(self.current_token()[0])
        
        # 2. Demand an opening brace '{'
        self.match('LBRACE')
        
        # 3. Read every assignment inside the braces until we hit the closing '}'
        assignments = []
        while self.current_token()[0] != 'RBRACE' and self.current_token()[0] != 'EOF':
            assignments.append(self.parse_assignment())
            
        # 4. Demand the closing brace '}'
        self.match('RBRACE')
        return BlockNode(block_name, assignments)

    def parse_assignment(self):
        """Parses an internal parameter line like: epochs = 100"""
        var_name = self.match('IDENTIFIER') # e.g., 'epochs'
        self.match('ASSIGN')               # Must be an '=' sign
        
        val_kind, val_value = self.current_token()
        if val_kind in ['INT', 'FLOAT', 'STRING', 'IDENTIFIER']:
            self.match(val_kind)           # Consume the value literal
            return AssignNode(var_name, val_value)
        
        raise SyntaxError(f"Expected a value (integer, float, string, or name) after '=', but got '{val_value}'")

    def parse_library_call(self):
        """Parses dotted execution paths like: trinity.train.start()"""
        path_segments = [self.match('IDENTIFIER')]
        
        # Loop to swallow up dots and names (e.g., . train . start)
        while self.current_token()[0] == 'DOT':
            self.match('DOT')
            path_segments.append(self.match('IDENTIFIER'))
            
        # Reconstruct the full path string (e.g., "trinity.train.start")
        full_path = ".".join(path_segments)
        
        # Demand function parenthesis ()
        self.match('LPAREN')
        self.match('RPAREN')
        
        return CallNode(full_path)