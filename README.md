
# digital-dostoevsky-tagger

The modules in this repository can be used to parse raw text files from the corpus of the Digital Dostoevsky Project and applying basic TEI markup to them.

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
