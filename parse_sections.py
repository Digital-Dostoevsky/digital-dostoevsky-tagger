import logging

TITLES = ["title", "subtitle", "part_title", "chapter_title", "maintitle"]


def is_roman_numeral(text):
    if not text:
        return False
    return all([c in "IVX" for c in text])


def roman_to_arabic(s: str) -> int:
    s = s.upper()
    roman = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    num = 0

    for i in range(len(s) - 1):
        if roman[s[i]] < roman[s[i + 1]]:
            num += roman[s[i]] * -1
            continue
        num += roman[s[i]]
    num += roman[s[-1]]

    return num


def parse_sections(text):
    sections = []
    buffer = []
    first_section = True
    has_maintitle = True

    section_numeral = None
    for i, line in enumerate(text.splitlines()):
        line = line.strip(" \t\n")
        if is_roman_numeral(line):
            sections.append({"numeral": section_numeral, "lines": buffer})
            section_numeral = line
            buffer = []
        else:
            buffer.append(line)

    for i, section in enumerate(sections):
        if section["numeral"] is not None:

            prev_section = sections[i - 1]
            integer = roman_to_arabic(section["numeral"])

            if integer == 1:
                prev_titles = []
                titles = iter(reversed(TITLES))

                # iterate lines from the previous section
                #  - bottom up, two at a time
                for current, previous in zip(
                    prev_section["lines"][::-1], prev_section["lines"][-2::-1]
                ):
                    # if the current line is not empty but the one above is
                    #  we have a "title" line of some sort
                    if current.strip() and not previous.strip():
                        # assign it to the next highest title level
                        prev_titles.append(current)
                        prev_section["lines"].remove(current)

                    # if we have two consecutive lines with content, we've
                    #  reached the bottom of the previous section's text
                    if current.strip() and previous.strip():
                        break

                if first_section:
                    first_section = False
                    has_maintitle = len(prev_titles) == 5

                if not has_maintitle:
                    titles = reversed(TITLES[:-1])

                section["prev_titles"] = reversed(
                    dict(zip(titles, prev_titles)).items()
                )
            else:
                # sanity check -- consecutive roman numeral sections should have
                #  consecutive roman numerals (unless they are section I)
                if roman_to_arabic(prev_section["numeral"]) != integer - 1:
                    logging.warning(
                        "Section numbering is not correct "
                        f"({prev_section['numeral']=}, {section['numeral']=})"
                        f"\n\t - {section['lines'][1]}..."
                    )

    return sections


def markup_sections(sections):
    buffer = ["<body>"]
    for section in sections:
        if section["numeral"] is None:
            front_matter = "\n".join(section["lines"]).strip()
            if front_matter:
                # <front/> section should be prepended so it goes before <body/>
                buffer = ["<front>", front_matter, "</front>", ""] + buffer
        else:
            if "prev_titles" in section:
                buffer.extend(
                    [f"<{key}>{val}</{key}>" for key, val in section["prev_titles"]]
                )
            integer = roman_to_arabic(section["numeral"])
            buffer.append(f'<div type="section" n="{integer}">')
            buffer.append(f"<head>{section['numeral']}</head>")
            buffer.extend(
                f"<p>{line.strip()}</p>" if line.strip() else ""
                for line in section["lines"]
            )
            buffer.append("</div>\n")
    buffer.append("</body>")
    return "\n".join(buffer)


if __name__ == "__main__":

    # with open("../Digital-Dostoevsky-corpus/Бесы - Proofed.txt", "rt") as _fh:
    with open("../Digital-Dostoevsky-corpus/Подросток.txt", "rt") as _fh:
        text = _fh.read()

    sections = parse_sections(text)

    print("<TEI>\n")
    print(markup_sections(sections))
    print("</TEI>")
