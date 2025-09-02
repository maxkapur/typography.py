#!/usr/bin/env python
"""Identify ASCII typography that could be better rendered as unicode."""

import re
import sys
from pathlib import Path
import subprocess

# Used to show substitutions
DIFF_CMD = (
    "git",
    "--no-pager",
    "diff",
    "--no-index",
    "--color=always",
    "--word-diff",
    "--",
)


# Rules to apply: a list of (regular expression, replacement) tuples
RULES = []


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
    (r"\b\-\-\-?\b", r"—"),
    # Numeric range should have en dash. Multiple en dashes are a false positive
    # (probably a date like 2024-12-26).
    (r"(?<![\d\-])(\d+)(\-)(\d+)(?![\-\d])", r"\1–\3"),
    # Non-curly opening quote
    (r"\"\b", r"“"),
    # Non-curly closing quote
    (r"(\b[\.\?,!]?)(\")", r"\1”"),
    # Trailing whitespace
    (r"(.*)([ \t]+)($)", r"\1\3"),
]
RULES.extend(map(compile, PUNCTUATION))

if __name__ == "__main__":
    # True if *any* input file had an issue
    issue_found = False

    # Collect input files and fail early if any don't exist
    infiles = []
    for maybe_file in sys.argv[1:]:
        infile = Path(maybe_file)
        if not infile.is_file():
            raise FileNotFoundError(maybe_file)
        infiles.append(infile)

    for infile in infiles:
        # Track number of issues in *this* input file
        issue_count = 0

        infile = Path(infile)
        print(f"{str(infile)}: ", end="")

        with open(infile, "r") as f:
            contents = f.read()

        for expr, sub in RULES:
            contents, nsubs = re.subn(expr, sub, contents)
            issue_count += nsubs

        if issue_count == 0:
            print("no issues")
            continue
        elif issue_count == 1:
            print("1 issue found")
        else:
            print(f"{issue_count} issues found")

        cmd = (*DIFF_CMD, str(infile), "-")
        subprocess.run(cmd, input=contents, text=True)

        issue_found = issue_found or issue_count >= 1

    exit(int(issue_found))
