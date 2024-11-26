import os
import sys
import re

class MorseNode:
    def __init__(self, symbol=None):
        self.symbol = symbol
        self.left = None
        self.right = None

def parse_morse_tree(tree_str):
    def tokenize(tree_str):
        tokens = []
        current_token = ""
        for char in tree_str:
            if char in "() ":
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
                if char in "()":
                    tokens.append(char)
            else:
                current_token += char
        if current_token:
            tokens.append(current_token)
        return tokens

    def build_tree(token_list):
        if not token_list:
            return None, token_list
        
        current_token = token_list.pop(0)
        if current_token == "(":
            left_subtree, remaining_tokens = build_tree(token_list)
            node_symbol = remaining_tokens.pop(0)
            right_subtree, remaining_tokens = build_tree(remaining_tokens)
            remaining_tokens.pop(0)  # Remove closing parenthesis
            
            node = MorseNode(node_symbol)
            node.left = left_subtree
            node.right = right_subtree
            return node, remaining_tokens
        elif current_token == "-":
            return None, token_list
        else:
            return MorseNode(current_token), token_list

    tokens = tokenize(tree_str)
    root_node, _ = build_tree(tokens)
    
    if root_node.symbol != "*":
        print("ERROR: Invalid tree file.")
        sys.exit(1)
    return root_node

def encode_message(plaintext, morse_tree):
    def find_morse_code(node, target_char, current_path):
        if not node:
            return None
        if node.symbol == target_char:
            return current_path
        
        dot_path = find_morse_code(node.left, target_char, current_path + ".")
        if dot_path:
            return dot_path
            
        dash_path = find_morse_code(node.right, target_char, current_path + "-")
        if dash_path:
            return dash_path
            
        return None

    morse_words = []
    for word in plaintext.split():
        if word == '':
            continue
            
        morse_chars = []
        for char in word.upper():
            morse_char = find_morse_code(morse_tree, char, "")
            if morse_char:
                morse_chars.append(morse_char)
        morse_words.append(' '.join(morse_chars))
        
    return '  '.join(morse_words)

def decode_message(morse_text, morse_tree):
    def decode_character(node, morse_pattern):
        if not node:
            return '?'
        if not morse_pattern and node != morse_tree:
            return node.symbol
            
        if morse_pattern[0] == "-":
            return decode_character(node.right, morse_pattern[1:])
        elif morse_pattern[0] == ".":
            return decode_character(node.left, morse_pattern[1:])
            
        return '?'

    decoded_words = []
    morse_words = morse_text.split('  ')
    
    for morse_word in morse_words:
        decoded_chars = []
        for morse_char in morse_word.split():
            decoded_chars.append(decode_character(morse_tree, morse_char))
        if decoded_chars:
            decoded_words.append(''.join(decoded_chars))
            
    return ' '.join(decoded_words).replace('*', '?')

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ['-e', '-d']:
        print("USAGE: morse.py [-e or -d] [tree-file]")
        sys.exit(1)

    operation_mode = sys.argv[1]
    tree_filename = sys.argv[2] if len(sys.argv) > 2 else None

    if tree_filename:
        try:
            with open(tree_filename, 'r') as tree_file:
                tree_content = tree_file.read().strip()
                tree_lines = tree_content.splitlines()
                
                if len(tree_lines) != 1:
                    print("ERROR: Invalid tree file.")
                    sys.exit(1)
                    
                tree_str = tree_lines[0]
                if not tree_str or tree_str.count('(') != tree_str.count(')'):
                    print("ERROR: Invalid tree file.")
                    sys.exit(1)
                    
                unique_chars = set(re.findall(r'[A-Z0-9]', tree_str))
                all_chars = re.findall(r'[A-Z0-9]', tree_str)
                if len(unique_chars) != len(all_chars):
                    print("ERROR: Invalid tree file.")
                    sys.exit(1)
                    
                if tree_str[0] != '(' or tree_str[-1] != ')':
                    print("ERROR: Invalid tree file.")
                    sys.exit(1)
                    
                if '*' not in tree_str:
                    print("ERROR: Invalid tree file.")
                    sys.exit(1)
        except Exception:
            print("USAGE: morse.py [-e or -d] [tree-file]")
            sys.exit(1)
    else:
        tree_str = "((((H S V) I (F U -)) E ((L R -) A (P W J))) * (((B D X) N (C K Y)) T ((Z G Q) M O)))"

    morse_tree = parse_morse_tree(tree_str)

    for input_line in sys.stdin:
        input_line = input_line.strip()
        if operation_mode == '-e':
            print(encode_message(input_line, morse_tree))
        else:
            print(decode_message(input_line, morse_tree))

if __name__ == "__main__":
    main()