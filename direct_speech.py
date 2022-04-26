import re

ATTRIBS = ["aloud", "direct", "who", "toWhom"]


def markup_direct_speech(text: str) -> str:
    """
    Markup direct speech in the given text with <said/> tags.
    See tests/test_direct_speech.py for examples.
    """

    # punctuation which can terminate an utterance (or part thereof)
    p = "?!).»"

    # designate two unicode "noncharacters" for use as temporary markers
    tag_open = "\uFFFE"
    tag_close = "\uFFFF"

    # first pass for direct speech offset by an emdash
    text = re.sub(
        rf"""
          (?<![,{p}]\s)       # discount emdashes which follow terminating punctuation
          —\s+                # the emdash and any whitespace
          (.+?)               # lazily capture everything up to...
          (?=[,{p}]\s—|\n|$)  # emdash preceded by a comma, terminating punct., or EOL
          ([{p}])?            # capture trailing terminating punctuation for inclusion
        """,
        # any whitespace folling the emdash is normalized to a single space
        rf"— {tag_open}\g<1>\g<2>{tag_close}",
        text,
        flags=re.VERBOSE,
    )

    # second pass for utterances that resume after an inquit that terminates with a
    #  comma or a period
    text = re.sub(
        rf"""
          (?<!{tag_close})    # discount anything already marked for tagging
          ([,.])\s*           # capture a comma or period that terminates an inquit
          —\s+                # the emdash and any whitespace
          (?!{tag_open})      # discount emdashes which follow terminating punctuation
          (.+?)               # lazily capture everything up to...
          (?=[,{p}]\s—|\n|$)  # emdash preceded by a comma, terminating punct., or EOL
          ([{p}])?            # capture trailing terminating punctuation for inclusion
        """,
        # any whitespace following the comma and emdash are normalized to a single space
        rf"\g<1> — {tag_open}\g<2>\g<3>{tag_close}",
        text,
        flags=re.VERBOSE,
    )

    # replace bounding guillemets with <said> tags
    text = re.sub(r"«[^»\n]+»", rf"{tag_open}\g<0>{tag_close}", text)

    text = text.replace(
        tag_open, "<said {}>".format(" ".join(f'{k}=""' for k in ATTRIBS))
    )

    # replace temporary markers with <said> tags
    text = text.replace(tag_open, "<said>")
    text = text.replace(tag_close, "</said>")
    return text


if __name__ == "__main__":
    # The following code is used for testing and development purposes only.
    import sys

    with open(sys.argv[1], "rt") as _fh:
        text = _fh.read()

    for line in text.splitlines():
        markedup_line = markup_direct_speech(line)
        if line != markedup_line:
            print(line)
            print(markup_direct_speech(line))
            print()
