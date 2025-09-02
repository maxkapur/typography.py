#!/usr/bin/env python
"""Identify ASCII typography that could be better rendered as Unicode."""

import argparse
import difflib
import re
import sys
from io import TextIOWrapper
from pathlib import Path

DIFFER = difflib.Differ()

# Rules to apply: a list of (regular expression, replacement) tuples
RULES: list[tuple[re.Pattern, str]] = []


def compile(expr_sub):
    "Map `(expr, sub)` to `(re.compile(expr), sub)`."
    expr, sub = expr_sub
    return re.compile(expr), sub


# Should use an apostrophe instead of a straight quote
CONTRACTIONS = [
    (r"(\b[a-zA-Z]+n)(')(t\b)", r"\1’\3"),
    (r"(\b[a-zA-Z]+)(')(ve\b)", r"\1’\3"),
    (r"(\b[a-zA-Z]+)(')(s\b)", r"\1’\3"),
    (r"(\b[a-zA-Z]+)(')(d\b)", r"\1’\3"),
    (r"(\b[a-zA-Z]+)(')(ll\b)", r"\1’\3"),
    (r"\bI'm\b", r"I’m"),
    (r"(\b[Mm]a)(')(am\b)", r"\1’\3"),
    (r"\bo'clock\b", r"o’clock"),
]
RULES.extend(map(compile, CONTRACTIONS))

# We have hunspell and friends so this isn't meant to be exhaustive
SPELLING = [
    # Proper codepoint for the 'okina
    (r"\bHawai('?)i\b", r"Hawaiʻi")
]
RULES.extend(map(compile, SPELLING))

PUNCTUATION = [
    # Two or three consecutive hyphens should be em dash
    (r"\b\-\-\-?(\b|\n)", r"—\1"),
    # Numeric range should have en dash. Multiple en dashes are a false positive
    # (probably a date like 2024-12-26).
    (r"(?<![\d\-])(\d+)(\-)(\d+)(?![\-\d])", r"\1–\3"),
    # Non-curly opening quote
    (r"\"\b", r"“"),
    # Non-curly closing quote
    (r"(\b[\.\?,!]?)(\")", r"\1”"),
    # Ellipsis
    (r"\.\.\.", r"…"),
    # Trailing whitespace
    (r"([^ \t]*)([ \t]+)(\n|$)", r"\1\3"),
]
RULES.extend(map(compile, PUNCTUATION))


def apply_count_issues(contents: str) -> tuple[str, int]:
    """Apply all rules to the string.

    Return the updated string and a count of how many issues were found.
    """
    issue_count = 0
    for expr, sub in RULES:
        contents, nsubs = re.subn(expr, sub, contents)
        issue_count += nsubs
    return contents, issue_count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("infiles", nargs="*", help="Input file(s)")
    options = parser.parse_args()

    # True if *any* input file had an issue
    issue_found = False

    # Collect input files and fail early if any don't exist
    infiles = []
    for maybe_file in options.infiles:
        infile = Path(maybe_file)
        if not infile.is_file():
            raise FileNotFoundError(maybe_file)
        infiles.append(infile)

    # Use stdin if no infiles provided
    infiles = infiles or [sys.stdin]

    for infile in infiles:
        match infile:
            case Path() as inpath:
                print(f"{infile}: ", end="")
                with open(inpath, "r") as f:
                    before = f.read()
            case TextIOWrapper() as intext:
                print(f"{intext.name}: ", end="")
                before = intext.read()
            case _:
                raise TypeError(infile)

        after, issue_count = apply_count_issues(before)

        if issue_count == 0:
            print("no issues")
            continue
        elif issue_count == 1:
            print("1 issue found")
        else:
            print(f"{issue_count} issues found")

        # https://www.timsanteford.com/posts/creating-a-git-like-diff-viewer-in-python-using-difflib/
        for line in DIFFER.compare(before.splitlines(), after.splitlines()):
            if line.startswith("-"):
                print(f"\033[31m{line}\033[0m")  # red for removals
            elif line.startswith("+"):
                print(f"\033[32m{line}\033[0m")  # green for additions
            else:
                print(line)

        issue_found = issue_found or issue_count >= 1

    exit(int(issue_found))


if __name__ == "__main__":
    main()
