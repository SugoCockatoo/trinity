import sys
from read import read_file
from tokenizer import tokenize_trinity
from parser import TrinityParser

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

if __name__ == "__main__":
    target_file = r"C:\Users\betas\OneDrive\Documentos\project_trinity\trinity_engine\genesis.tri" 
    
    ast_tree = compile_trinity(target_file)
    
    if ast_tree:
        print("\n=== SUCCESS: Final Abstract Syntax Tree ===")
        for statement in ast_tree.statements:
            
            if hasattr(statement, 'name'): 
                print(f"Block: {statement.name}")
                for assignment in statement.assignments:
                    print(f"  ├── Property: {assignment.name} -> Value: {assignment.value}")
            
            # If it's a direct library function call
            elif hasattr(statement, 'path'):
                print(f"Library Call: {statement.path}()")