import logging
import re
from typing_extensions import NotRequired, TypedDict

Section = TypedDict(
    "Section",
    {
        "numeral": str | None,
        "lines": list[str],
        "title": NotRequired[str],
        "subtitle": NotRequired[str],
        "prev_titles": NotRequired[dict[str, str]],
        "section_title": NotRequired[str],
    },
)

SectionAttribs = TypedDict("SectionAttribs", {"type": str, "n": int})


def is_roman_numeral(text: str) -> bool:
    if not text:
        return False
    return all([c in "IVX" for c in text])


def roman_to_arabic(s: str | None) -> int:
    if s is None:
        return -1
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


def parse_sections(text: str) -> list[Section]:
    titles = ["div1", "div2", "chapter_title"]
    first_section = True

    sections: list[Section] = []
    buffer = [""]  # ensure an empty line at the top of the document

    section_numeral = None
    for line in text.splitlines():
        line = line.strip(" \t\n")
        if is_roman_numeral(line):
            sections.append({"numeral": section_numeral, "lines": buffer})
            section_numeral = line
            buffer = []
        else:
            buffer.append(line)
    sections.append({"numeral": section_numeral, "lines": buffer})

    section: Section
    for i, section in enumerate(sections):
        if section["numeral"] is not None:
            prev_section: Section = sections[i - 1]
            integer = roman_to_arabic(section["numeral"])

            if integer == 1:
                prev_titles: list[str] = []

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
                    prev_titles.reverse()
                    # must have a top-level title
                    section["title"] = prev_titles.pop(0)

                    # DUBIOUS: if there's more than one title left, take a subtitle
                    if len(prev_titles) > 1:
                        section["subtitle"], *prev_titles = prev_titles

                    prev_titles.reverse()

                    titles = titles[: len(prev_titles)]

                    titles.reverse()

                section["prev_titles"] = dict(reversed(list(zip(titles, prev_titles))))

            else:
                # sanity check -- consecutive roman numeral sections should have
                #  consecutive roman numerals (unless they are section I)
                if roman_to_arabic(prev_section["numeral"]) != integer - 1:
                    logging.warning(
                        "Section numbering is not correct "
                        f"({prev_section['numeral']=}, {section['numeral']=})"
                        f"\n\t - {section['lines'][1]}..."
                    )

            # pick up section titles for roman-numeraled sections
            # (Brothers Karamazov only)
            for j, line in enumerate(section["lines"]):
                # skip the first line, the last line, and empty lines
                if j == 0 or j == len(section["lines"]) - 1 or not line.strip():
                    continue

                # if we have two conecutive lines with content, give up and move on
                if section["lines"][j + 1].strip():
                    break

                # if we've got a line with blank lines on either side AND
                #  where all the content is upper case, take it as a section title
                if (
                    not section["lines"][j - 1].strip()
                    and not section["lines"][j + 1].strip()
                    and re.sub("<[^<]+?>", "", line).upper()
                    == re.sub("<[^<]+?>", "", line)
                ):
                    section["section_title"] = line.strip()
                    break

    return sections


def markup_sections(sections: list[Section]) -> str:
    first_section = True
    has_chapters = False
    buffer = ["<body>"]
    section_attribs: dict[str, SectionAttribs] = {
        "div1": {"type": "part", "n": 0},
        "div2": {"type": "chapter", "n": 0},
    }

    def get_section_markup(section_type: str, heading_text: str) -> str:
        section_attribs[section_type]["n"] += 1
        attribs = " ".join(
            f'{k}="{v}"' for k, v in section_attribs[section_type].items()
        )
        return f"<{section_type} {attribs}><head>{heading_text}</head>"

    for section in sections:
        if section["numeral"] is None:
            front_matter = "\n".join(section["lines"]).strip()
            if front_matter:
                # <front/> section should be prepended so it goes before <body/>
                buffer = ["<front><p>", front_matter, "</p></front>", ""] + buffer
        else:
            if "title" in section:
                buffer.append(f'<head type="mainTitle">{section["title"]}</head>')
            if "subtitle" in section:
                buffer.append(f'<head type="subTitle">{section["subtitle"]}</head>')

            chapter_title = section.get("prev_titles", {}).pop("chapter_title", None)
            if "prev_titles" in section:
                if first_section:
                    has_chapters = len(section["prev_titles"]) > 1

                if not first_section:
                    if not has_chapters:
                        buffer.append("</div2>\n")
                    buffer.extend(
                        [f"</{key}>" for key in reversed(section["prev_titles"])]
                    )
                first_section = False

                if "div1" in section["prev_titles"]:
                    # restart chapter-level numbering
                    section_attribs["div2"]["n"] = 0

                buffer.extend(
                    [
                        get_section_markup(key, val)
                        for key, val in section["prev_titles"].items()
                    ]
                )

                if not has_chapters:
                    buffer.append("<div2>\n")

                if chapter_title is not None:
                    buffer.append(f'<head type="mainTitle">{chapter_title}</head>')

            integer = roman_to_arabic(section["numeral"])
            buffer.append(f'<div3 type="section" n="{integer}">')
            buffer.append(f"<head>{section['numeral']}</head>")
            if "section_title" in section:
                buffer.append(f"<head>{section['section_title']}</head>")
            buffer.extend(
                f"<p>{line.strip()}</p>" if line.strip() else ""
                for line in section["lines"]
            )
            buffer.append("</div3>\n")

    buffer.append("</div2>\n")
    buffer.append("</div1>\n")
    buffer.append("</body>")
    return "\n".join(buffer)


if __name__ == "__main__":
    # The following code is used for testing and development purposes only.
    import sys

    with open(sys.argv[1], "rt", encoding="utf8") as _fh:
        text = _fh.read()

    sections = parse_sections(text)

    print("<TEI>\n")
    print(markup_sections(sections))
    print("</TEI>")
