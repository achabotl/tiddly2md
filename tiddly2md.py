import argparse
import re
import os
import sys
from typing import Union, List, Dict

import pandas as pd


def good_tag(tag, valid_tags):
    """Returns True if tag contains of the valid tags.

    :param tag: string
    :param valid_tags: list of valid tags
    """
    for each in valid_tags:
        if each in str(tag):
            return True
    return False


def numbered_lists(line: str) -> str:
    list_level = 0
    while line.startswith('#'):
        line = line[1:]
        list_level += 1
    if list_level:
        prefix = " "*(list_level - 1)*2 + "0. "
        line = prefix + line.strip()
    return line


def unnumbered_lists(line: str) -> str:
    list_level = 0
    while line.startswith('*'):
        line = line[1:]
        list_level += 1
    if list_level:
        prefix = " "*(list_level - 1)*2 + "- "
        line = prefix + line.strip()
    return line


def lists(line: str) -> str:
    line = line.strip()
    line = numbered_lists(line)
    line = unnumbered_lists(line)
    return line


def wiki_to_md(text):
    """Convert wiki formatting to markdown formatting.

    :param text: string of text to process

    :return: processed string
    """
    if isinstance(text, float):
        return ""
    fn = []
    new_text = []
    fn_n = 1  # Counter for footnotes
    for line in text.split('\n'):
        # lists (has to be first!)
        line = lists(line)
        # Replace wiki headers with markdown headers
        match = re.match('(!+)(\\s?)[^\\[]', line)
        if match:
            header, spaces = match.groups()
            new_str = '#' * len(header)
            line = re.sub('(!+)(\\s?)([^\\[])', new_str + ' ' + '\\3', line)
        # Underline (doesn't exist in MD)
        line = re.sub("__(.*?)__", "\\1", line)
        # Bold
        line = re.sub("''(.*?)''", "**\\1**", line)
        # Italics
        line = re.sub("//(.*?)//", "_\\1_", line)
        # Remove wiki links
        line = re.sub("\\[\\[(\\w+?)\\]\\]", "\\1", line)
        # Change links to markdown format
        line = re.sub("\\[\\[(.*)\\|(.*)\\]\\]", "[\\1](\\2)", line)
        # Code
        line = re.sub("\\{\\{\\{(.*?)\\}\\}\\}", "`\\1`", line)
        # Footnotes
        match = re.search("```(.*)```", line)
        if match:
            text = match.groups()[0]
            fn.append(text)
            line = re.sub("```(.*)```", '[^{}]'.format(fn_n), line)
            fn_n += 1
        new_text.append(line)

    # Append footnotes
    for i, each in enumerate(fn):
        new_text.append('[^{}]: {}'.format(i+1, each))
    return '\n'.join(new_text)


def sanitize(value):
    """Makes sure filenames are valid by replacing illegal characters

    :param value: string
    """
    value = str(value)
    #value = strdata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = str(re.sub('[^\w\s-]', '', value).strip())
    return value


def list_from_tags(raw: Union[float, str]) -> List[str]:
    if isinstance(raw, float):
        return [""]
    tags = []
    while "[[" in raw:
        parts = raw.split('[[', 1)
        remainder = parts[0]
        parts = parts[1].split(']]', 1)
        remainder += parts[1]
        raw = remainder
        tags.append(parts[0])
    raw = raw.strip()
    while " " in raw:
        parts = raw.split(' ', 1)
        remainder = parts[0]
        parts = parts[1].split(' ', 1)
        if len(parts) > 1:
            remainder += parts[1]
        raw = remainder
        tags.append(parts[0])
    if raw:
        tags.append(raw)
    return tags


def extract_special_tags(tags: List[str]) -> str:
    fm: Dict[str, str] = {"tags": "", "up": ", ".join(tags)}
    langs = ['c','c++','eagle: ulp','html','javascript','nodejs','php','python','Verilog','VHDL']
    for tag in tags:
        if tag in langs:
            fm["programmiersprache"] = tag
        else:
            fm["tags"] += tag + ", "
    if fm["tags"].endswith(", "):
        fm["tags"] = fm["tags"][:-2]
    if fm["tags"] == "":
        fm.pop("tags")
    fm_string = "---\n"
    for key, value in fm.items():
        fm_string += f"{key}: {value}\n"
    fm_string += "---\n\n"
    return fm_string


def add_quotation_marks(tags: List[str]) -> List[str]:
    outlist = []
    for tag in tags:
        if " " in tag:
            outlist.append('"'+tag+'"')
        else:
            outlist.append(tag)
    return outlist


def frontmatter(raw_tags: Union[float, str]) -> str:
    tags = list_from_tags(raw_tags)
    tags = add_quotation_marks(tags)
    return extract_special_tags(tags)


def main(args):

    output_path = args.outdir
    try:
        os.mkdir(output_path)
    except OSError:
        pass

    df = pd.read_csv(args.input_file)
    if args.tags:
        df = df[df.tags.apply(lambda x: good_tag(x, args.tags))]

    for row_id, row in df.iterrows():
        filename = sanitize(row.title)
        filename = '{}.{}'.format(filename, args.ext)
        with open(os.path.join(output_path, filename), 'w') as f:
            try:
                f.write(frontmatter(row.tags))
                f.write(wiki_to_md(row.text))
            except Exception as e:
                print(f"{e} in {row['title']}")
                f.write('')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Convert TiddlyWiki tiddlers exported as CSV to "
                    "individual files.")
    parser.add_argument('--ext', '-e', dest='ext',
                        default='md',
                        help='File extension (defaults to "md")')
    parser.add_argument('--outdir', '-o',
                        default='output',
                        dest='outdir',
                        help='Output folder (defaults to "output")')
    parser.add_argument('--tags', '-t', dest='tags',
                        action='append',
                        help='Valid tag to export, can have multiple')
    parser.add_argument('input_file',
                        help='Exported CSV file')
    args = parser.parse_args()

    sys.exit(main(args))
