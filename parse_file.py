#!/usr/bin/env python3

"""
CLI for parsing raw text files from the corpus of the Digital Dostoevsky Project
  and applying basic TEI markup.
"""

import argparse
import logging
import sys
from pathlib import Path

from lxml import etree

from direct_speech import markup_direct_speech
from proper_names import markup_proper_names
from parse_sections import parse_sections, markup_sections


XML_PROCESSING_INSTRUCTIONS = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    """<?xml-model
  href="http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng"
  type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>""",
    """<?xml-model
  href="http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng"
  type="application/xml" schematypens="http://purl.oclc.org/dsdl/schematron"?>""",
]


def create_tei_structure(text: str) -> str:
    """Create TEI structure for the given text."""

    return f"""\
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title></title>
        <author/>
      </titleStmt>
      <editionStmt>
        <edition/>
        <respStmt>
          <resp/>
          <persName/>
        </respStmt>
      </editionStmt>
      <publicationStmt/>
      <sourceDesc/>
    </fileDesc>
  </teiHeader>
  <text>
      {text}
  </text>
</TEI>
"""


def format_tree(elem: etree._Element, indent: str = "  ", level: int = 0) -> None:
    """Pretty-prints and indents a tree beautifully."""
    i = "\n%s" % (level * indent)
    if elem.tag == "{http://www.tei-c.org/ns/1.0}p":
        return
    if elem.tag == "{http://www.tei-c.org/ns/1.0}head":
        return
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = "%s%s" % (i, indent)
        for sub_elem in elem:
            format_tree(sub_elem, indent, level + 1)
            if not sub_elem.tail or not sub_elem.tail.strip():
                sub_elem.tail = i
            if sub_elem.getnext() is not None:
                sub_elem.tail += indent
        if not elem.tail or not elem.tail.strip():
            elem.tail = i


def main() -> None:
    """Command-line entry-point."""

    parser = argparse.ArgumentParser(description="Description: {}".format(__doc__))
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False, help="Increase verbosity"
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", default=False, help="Quiet operation"
    )
    parser.add_argument(
        "-o",
        "--output",
        action="store",
        help="Output file (default: stdout)",
    )
    parser.add_argument(
        "--rng-schema",
        action="store",
        help="RELAX NG schema to validate against (optional)",
    )
    parser.add_argument(
        "--person-names-list",
        action="store",
        help="Line-by-line list of person names (optional)",
    )
    parser.add_argument(
        "--place-names-list",
        action="store",
        help="Line-by-line list of place names (optional)",
    )
    parser.add_argument("input_text", action="store", help="Text to process")

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    log_level = logging.CRITICAL if args.quiet else log_level
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.info("Processing input text: %s", args.input_text)

    with Path(args.input_text).open("r", encoding="utf8") as _fh:
        text = _fh.read()

    text = markup_direct_speech(text)

    if args.person_names_list:
        with Path(args.person_names_list).open("rt", encoding="utf8") as _fh:
            person_names = [line.strip() for line in _fh if line.strip()]
        text = markup_proper_names(text, person_names, "persName")

    if args.place_names_list:
        with Path(args.place_names_list).open("rt", encoding="utf8") as _fh:
            place_names = [line.strip() for line in _fh if line.strip()]
        text = markup_proper_names(text, place_names, "placeName")

    sections = parse_sections(text)
    text = markup_sections(sections)

    output_path = None
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = etree.fromstring(create_tei_structure(text).encode("utf8"))
    format_tree(doc)

    logging.info("Writing processed text to: %s", args.output or "stdout")

    with output_path.open("wt", encoding="utf8") if output_path else sys.stdout as _fh:
        _fh.write("\n".join(XML_PROCESSING_INSTRUCTIONS) + "\n")
        _fh.write(etree.tostring(doc, pretty_print=True, encoding="unicode"))

    if args.rng_schema:
        logging.info("Validating against schema: {}".format(args.rng_schema))
        relaxng_doc = etree.parse(args.rng_schema)
        relaxng = etree.RelaxNG(relaxng_doc)
        if not relaxng.validate(doc):
            for entry in relaxng.error_log:
                # Note: better validation errors are available with something like jing
                if (
                    entry.message == "Invalid attribute aloud for element said"
                    or entry.line in [15, 16]
                ):
                    # these errors are expected, given that dummy values are used
                    # -- only report if debug logging is enabled
                    logging.debug(entry)
                else:
                    logging.warning(entry)


if __name__ == "__main__":
    main()
