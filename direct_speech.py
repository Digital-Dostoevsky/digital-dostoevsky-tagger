import regex as re

ATTRIBS = ["aloud", "direct", "who", "toWhom"]


def markup_direct_speech(text: str) -> str:
    """
    Markup direct speech in the given text with <said/> tags.
    See tests/test_direct_speech.py for examples.
    """

    # punctuation which can terminate an utterance (or part thereof)
    p = "?!).»"

    # designate two unicode "noncharacters" for use as temporary markers
    start = "\uFFFE"
    end = "\uFFFF"

    text_out = []
    for line in text.splitlines():

        # mark text inside bounding straight double quotes
        line = re.sub(r'«?"[^"\n]+"', rf"{start}\g<0>{end}", line)

        line_out = line

        # first pass for direct speech offset by an emdash
        line_out = re.sub(
            rf"""
            (?<!{start})          # onset is not already marked
            (?<!{end}\s)          # or follows immediately from a marked sequence

            (?:(?:                # emdash-offset utterance
                                  # -----------------------

              (?<![,{p}\w]\s)     # emdash does not follow terminating punctuation
              (—\s+)              # capture the emdash and any whitespace
              (.+?)               # lazily capture everything up to...
              (?=[,{p}]\s—|\n|$)  # terminating punctuation, a new emdash, or end of line

            ) | (?:               # guillemet-offset utterance
                                  # --------------------------

              («)                 # capture the guillemet
              ([^«]+?)            # lazily capture everything up to...
              (?=
                                  # an emdash if it's preceded by terminating punctuation
                                  #  that's not itself preceded by a marked sequence
                (?<!"|{end})[,{p}]\s—
                |»(?!{end})       # or a guillemet (unless it closes a marked sequence)
                |\n|$             # or end of line
              )
            ))
            ([{p}])?              # capture any trailing terminating punctuation
            """,
            lambda m: "".join(
                [
                    (m.group(1).strip() + " " if m.group(1) else m.group(3)),
                    start,
                    (m.group(2) or m.group(4)),
                    m.group(5) or "",
                    end,
                ]
            ),
            line_out,
            flags=re.VERBOSE,
        )

        # second pass for utterances offset with emdash and that resume after
        #  an inquit that terminates with a comma or a period
        if (
            # if there's already a marked utterance in this line
            f"— {start}" in line_out
            or re.search(rf"«{start}[^»]+{end}", line_out)
            or re.match(rf"«{start}[^»]+»{end}", line_out)
        ):
            line_out = re.sub(
                rf"""
                                  # onset follows a marked utterance earlier in the line
                (?<={end}[^{end}]+?) 
                (?<!{end})        # onset does not immediately follow a marked utterance

                ([,.])\s*         # capture a comma or period that terminates an inquit
                —\s+              # match the emdash and any whitespace
                (?!{start})       # unless the utterance is already marked
                (.+?)             # lazily capture everything up to...
                (?=
                  [,{p}]\s—       # an emdash preceded by terminating punctuation
                  |»(?!{end})     # or a guillemet (unless it closes a marked sequence)
                  |\n|$           # or end of line
                )
                ([{p}]+)?         # capture any trailing terminating punctuation
                """,
                rf"\g<1> — {start}\g<2>\g<3>{end}",
                line_out,
                flags=re.VERBOSE,
            )

        # post-hoc
        line_out = line_out.replace(f"«{start}", f"{start}«")
        line_out = line_out.replace(f"».{end}", f"»{end}.")

        # replace bounding guillemets with <said> tags
        line_out = re.sub(
            rf"(?<!{start})«.+?(»(?!{end})|\n|$)",
            rf"{start}\g<0>{end}",
            line_out,
        )

        # replace temporary markers with <said> tags
        line_out = line_out.replace(
            start, "<said {}>".format(" ".join(f'{k}=""' for k in ATTRIBS))
        )
        line_out = line_out.replace(end, "</said>")

        text_out.append(line_out)

    return "\n".join(text_out)


if __name__ == "__main__":
    # The following code is used for testing and development purposes only.
    import sys

    with open(sys.argv[1], "rt", encoding="utf8") as _fh:
        text = _fh.read()

    for line in text.splitlines():
        marked_up_line = markup_direct_speech(line)
        if line != marked_up_line:
            print(line)
            print(marked_up_line)
            print()
