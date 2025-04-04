#!/usr/bin/env python
"""
Pre-commit hook to prevent usage of GPT-4 models in the codebase.
Enforces the use of GPT-3.5-turbo for cost efficiency.
"""

import sys
import re
from pathlib import Path

def check_file_for_gpt4(file_path):
    """Check if a file contains references to GPT-4."""
    # Skip checking this file itself
    if Path(file_path).name == 'check_gpt_usage.py':
        return 0

    gpt4_patterns = [
        r'gpt-4',
        r'gpt4',
        r'GPT-4',
        r'GPT4',
    ]

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    for pattern in gpt4_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            line_number = content[:match.start()].count('\n') + 1
            print(f"{file_path}:{line_number}: Found GPT-4 usage: {match.group()}")
            return 1
    return 0

def main():
    """Main function to check files for GPT-4 usage."""
    exit_code = 0

    for file_path in sys.argv[1:]:
        if Path(file_path).suffix == '.py':
            result = check_file_for_gpt4(file_path)
            if result != 0:
                exit_code = result

    if exit_code != 0:
        print("\nError: GPT-4 usage detected. Please use GPT-3.5-turbo instead.")
        print("This is enforced to maintain cost efficiency.")

    sys.exit(exit_code)

if __name__ == '__main__':
    main()
