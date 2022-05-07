
# digital-dostoevsky-tagger

![Python Version](https://img.shields.io/badge/python-3.8|3.9|3.10-blue?logo=python&logoColor=white)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

The modules in this repository can be used to parse raw text files from the corpus of the Digital Dostoevsky Project and apply basic TEI markup to them.


## Functionality

The markup applied is of three kinds:

* **Structural**  
  `<div1/>`, `<div2/>`, and `<div3/>` tags are applied, as are appropriate `<head/>` tags.  Paragraphs are wrapped in `<p/>` tags.  
  Structural markup is applied by identifying sections that are introduced with roman numerals, and working backwards from there.  
  A skeleton `<teiHeader/>` is added, and some XML processing instructions.

* **Direct Speech**  
  `<said/>` tags are used to wrap utterances.  
  Instances of direct speech are identified using regular expressions to detect typographical conventions, primarily the use of guillemets (`«` and `»`) and emdashes (`—`).  Empty placeholder attributes are added to the `<said/>` tags.

* **Proper Names**  
  Line-by-line lists for orthographic forms for person and place names can be supplied, and occurrences will be marked up with `<persName/>` and `<placeName/>` tags respectively.


## Usage

The modules and CLI require Python >= 3.8.  The only non-stdlib dependencies are `lxml` and `regex` -- install them using `pip install -r requirements.txt` or similar.

```sh
usage: parse_file.py [-h] [-v] [-q] [-o OUTPUT] [--rng-schema RNG_SCHEMA] [--person-names-list PERSON_NAMES_LIST] [--place-names-list PLACE_NAMES_LIST] input_text

Description: CLI for parsing raw text files from the corpus of the Digital Dostoevsky Project and applying basic TEI markup.

positional arguments:
  input_text            Text to process

options:
  -h, --help            show this help message and exit
  -v, --verbose         Increase verbosity
  -q, --quiet           Quiet operation
  -o OUTPUT, --output OUTPUT
                        Output file (default: stdout)
  --rng-schema RNG_SCHEMA
                        RELAX NG schema to validate against (optional)
  --person-names-list PERSON_NAMES_LIST
                        Line-by-line list of person names (optional)
  --place-names-list PLACE_NAMES_LIST
                        Line-by-line list of place names (optional) 
```


## Testing

Tests are available for the direct speech module, in the form of [a bunch of examples with expected transformations](tests/test_direct_speech.py).  Run them using `pytest` (`pip install pytest`) from the project root.
