import sys
from trinity_engine.read import read_file
from trinity_engine.tokenizer import tokenize_trinity
from trinity_engine.parser import TrinityParser

def compile_trinity(file_path):
    print(f"--- Starting Compilation for {file_path} ---")
    
    #Read
    try:
        source_code = read_file(file_path)
        print("[1/3] File read successfully.")
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' could not be found.")
        return
    
    #Tokenize
    try:
        tokens = tokenize_trinity(source_code)
        print(f"[2/3] Tokenization complete. Generated {len(tokens)} tokens.")
    except RuntimeError as e:
        print(f"Lexer Error: {e}")
        return

    #Parse
    try:
        parser = TrinityParser(tokens)
        ast = parser.parse()
        print("[3/3] Parsing complete. AST successfully generated.")
        print("-" * 40)
        return ast
    except SyntaxError as e:
        print(f"Parser Error: {e}")
        return