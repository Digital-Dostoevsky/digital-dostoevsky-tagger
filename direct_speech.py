import re


def markup_direct_speech(text):

    text = re.sub(r"(?<!» )— ([^—\n]+)(\s*)", r"<said>\g<1></said>\g<2>", text)
    text = re.sub(r"«[^»]+»", r"<said>\g<0></said>", text)

    # move trainling commas and whitespace outside of utterances
    text = re.sub(r"([\s,]+)</said>", r"</said>\g<1>", text)

    return text
