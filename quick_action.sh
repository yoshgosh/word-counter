#!/bin/zsh
lang="jp" # "jp" or "en"
source="clipboard" # "clipboard" or "stdin"
python3 "$HOME/Projects/word-counter/word_counter.py" --lang "$lang" --source "$source"
