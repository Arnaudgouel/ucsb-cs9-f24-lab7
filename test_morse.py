#!/usr/bin/env python3
import unittest
import subprocess
import tempfile
import os
import sys
from morse import MorseNode, parse_morse_tree, encode_message, decode_message

class TestMorseCode(unittest.TestCase):
    def setUp(self):
        """Set up test trees and temporary files before each test"""
        # Standard tree
        self.standard_tree = "((((H S V) I (F U -)) E ((L R -) A (P W J))) * (((B D X) N (C K Y)) T ((Z G Q) M O)))"
        
        # Get the directory of the current test file
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.morse_script = os.path.join(self.current_dir, 'morse.py')
        
        # Create temporary files
        # Valid tree file
        self.valid_tree_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.valid_tree_file.write(self.standard_tree + '\n')
        self.valid_tree_file.close()

        # Invalid tree files
        # Duplicate character
        self.duplicate_char_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.duplicate_char_file.write("((A *) A)\n")
        self.duplicate_char_file.close()

        # Multiple lines
        self.multiline_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.multiline_file.write(self.standard_tree + '\n' + self.standard_tree + '\n')
        self.multiline_file.close()

        # No asterisk
        self.no_asterisk_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.no_asterisk_file.write("((A B) C)\n")
        self.no_asterisk_file.close()

        # Parse standard tree for use in tests
        self.morse_tree = parse_morse_tree(self.standard_tree)

    def tearDown(self):
        """Clean up temporary files after each test"""
        for file_path in [self.valid_tree_file.name, self.duplicate_char_file.name, 
                         self.multiline_file.name, self.no_asterisk_file.name]:
            try:
                os.unlink(file_path)
            except:
                pass

    def run_morse_command(self, args, input_text):
        """Helper function to run morse.py with given arguments and input"""
        python_executable = sys.executable if hasattr(sys, 'executable') else 'python3'
        command = [python_executable, self.morse_script] + args
        
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            universal_newlines=True
        )
        stdout, stderr = process.communicate(input_text)
        return stdout, stderr, process.returncode

    def test_command_line_interface(self):
        """Test command line interface"""
        test_cases = [
            # Format: (args, input_text, expected_output)
            (["-e"], "HELLO", ".... . .-.. .-.. ---\n"),
            (["-d"], ".... . .-.. .-.. ---", "HELLO\n"),
            (["-e", self.valid_tree_file.name], "HELLO", ".... . .-.. .-.. ---\n"),
            
            # Multiple words
            (["-e"], "HELLO WORLD", ".... . .-.. .-.. ---  .-- --- .-. .-.. -..\n"),
            (["-d"], ".... . .-.. .-.. ---  .-- --- .-. .-.. -..", "HELLO WORLD\n"),
            
            # Empty input
            (["-e"], "", "\n"),
            (["-d"], "", "\n"),
            
            # Whitespace handling
            (["-e"], "HELLO   WORLD", ".... . .-.. .-.. ---  .-- --- .-. .-.. -..\n"),
            (["-d"], ".... . .-.. .-.. ---    .-- --- .-. .-.. -..", "HELLO WORLD\n"),
        ]
        
        for args, input_text, expected_output in test_cases:
            with self.subTest(args=args, input_text=input_text):
                stdout, stderr, returncode = self.run_morse_command(args, input_text)
                self.assertEqual(returncode, 0, f"Process failed with stderr: {stderr}")
                self.assertEqual(stdout, expected_output)

    def test_error_handling(self):
        """Test error handling"""
        error_test_cases = [
            # Invalid arguments
            ([], "", "USAGE: morse.py [-e or -d] [tree-file]\n"),
            (["-x"], "", "USAGE: morse.py [-e or -d] [tree-file]\n"),
            
            # Invalid tree files
            (["-e", self.duplicate_char_file.name], "HELLO", "ERROR: Invalid tree file.\n"),
            (["-e", self.multiline_file.name], "HELLO", "ERROR: Invalid tree file.\n"),
            (["-e", self.no_asterisk_file.name], "HELLO", "ERROR: Invalid tree file.\n"),
            (["-e", "nonexistent.txt"], "HELLO", "USAGE: morse.py [-e or -d] [tree-file]\n"),
        ]
        
        for args, input_text, expected_output in error_test_cases:
            with self.subTest(args=args, input_text=input_text):
                stdout, stderr, returncode = self.run_morse_command(args, input_text)
                self.assertIn(expected_output, stdout + stderr)

    # ... (rest of the test class remains the same)

def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests()