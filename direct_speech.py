import re


def markup_direct_speech(text):

    text = re.sub(
        r"""
            (?<!»\s)        # ignore emdashes which follow chevrons
            —\s             # the emdash and whitespace (normalizing to a single space)
            ([^—\n]+)       # everything up to another emdash or the end of the line
            (\s*)           # any trainling whitespace which may precede a second emdash
        """,
        r"— <said>\g<1></said>\g<2>",
        text,
        flags=re.VERBOSE,
    )

    # replace bounding chevrons with <said> tags
    text = re.sub(r"«[^»]+»", r"<said>\g<0></said>", text)

    # move trainling commas and whitespace outside of utterances
    text = re.sub(r"([\s,]+)</said>", r"</said>\g<1>", text)

    return text


if __name__ == "__main__":
    import sys

    with open(sys.argv[1], "rt") as _fh:
        text = _fh.read()

    for line in text.splitlines():
        markedup_line = markup_direct_speech(line)
        if line != markedup_line:
            print(line)
            print(markup_direct_speech(line))
            print()
