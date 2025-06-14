#!/usr/bin/env python3
import sys
import re
import unicodedata
import subprocess
import argparse

def dialog(message: str, title: str = "Word Counter") -> None:
    message = message.replace('"', '\\"').replace('\n', '\\n')
    title = title.replace('"', '\\"')
    script = f'display dialog "{message}" with title "{title}" buttons {{"OK"}} default button "OK"'
    subprocess.run(["osascript", "-e", script], check=False)

def notify(message: str, title: str = "Word Counter") -> None:
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(["osascript", "-e", script], check=False)

def get_text(source: str) -> str:
    if source == "clipboard":
        text = subprocess.run(["pbpaste"], stdout=subprocess.PIPE, check=True).stdout.decode("utf-8")
    else:
        text = sys.stdin.read()
        # Automator 経由の選択テキストは末尾に \n が1つ追加されるため、1文字だけ除去
        if text.endswith("\n"):
            text = text[:-1]
    # dialog(f"---\n{text}\n---")　# 入力チェック用
    return text

def preprocess(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    def is_valid_char(ch):
        cat = unicodedata.category(ch)
        return cat[0] in {"L", "N", "P", "S"} or ch in (" ", "\u3000", "\t", "\n")
    return "".join(ch for ch in text if is_valid_char(ch))

def count(text: str) -> tuple[int, int, int]:
    char_count = len(text)
    condensed_char_count = sum(1 for ch in text if unicodedata.category(ch)[0] in {"L", "N", "P", "S"})
    tokens = re.split(r"[ \u3000\t\n]+", text.strip())
    word_count = sum(1 for token in tokens if token and any(unicodedata.category(ch)[0] in {"L", "N"} for ch in token))
    return char_count, condensed_char_count, word_count

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["clipboard", "stdin"], default="clipboard")
    parser.add_argument("--lang", choices=["jp", "en"], default="jp")
    args = parser.parse_args()

    raw_text = get_text(args.source)
    clean_text = preprocess(raw_text)
    c1, c2, w = count(clean_text)

    if args.lang == "jp":
        title = "文字数カウント（クリップボード）" if args.source == "clipboard" else "文字数カウント（選択テキスト）"
        msg = f"{c1} 文字\n{c2} 文字（空白除く）\n{w} 単語"
    else:
        title = "Word Counter (Clipboard)" if args.source == "clipboard" else "Word Counter (Selected Text)"
        msg = f"{c1} chars\n{c2} chars (no spaces)\n{w} words"

    notify(msg, title)

if __name__ == "__main__":
    main()