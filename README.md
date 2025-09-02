# typography.py

Identify ASCII typography that could be better rendered as unicode. For example,
`this right here---could be better rendered` as an em dash `—`.

This is *not* a spell checker or prose linter; I use it in addition to
[Hunspell](https://hunspell.github.io/) and
[Proselint](https://github.com/amperser/proselint) when I want to be maximally
pedantic. Like those other tools, `typography.py` flags issues eagerly and is
prone to false positives.

## Installation

```shell
pipx install 'https://github.com/maxkapur/typography.py/archive/refs/heads/main.tar.gz'
```

## Usage

```shell
typography some_file.md maybe_another.md
```

Suggested changes will be shown using `git diff`.

## Development

```shell
python -m venv venv
source ./venv/bin/activate  # Or appropriate command for your shell
pip install --upgrade pip
pip install --editable .[dev]
```
