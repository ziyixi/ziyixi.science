import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Dict

import bibtexparser
import click
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from time import strptime

template = r"""---
title: "{title}"
year: {year}
month: {month}
draft: false
authors: {authors}
abstract: {abstract}
publication: {publication}
doi: {doi}
pdf: {pdf}
html: {html}
weight: {weight}
---
"""


def slugify(value: str, allow_unicode: bool = False) -> str:
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode(
            'ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def convert_single(target_dir: Path, idx: int, entry: Dict[str, str]):
    dir = target_dir/slugify(entry["title"])
    dir.mkdir(parents=True, exist_ok=True)
    # bib
    db = BibDatabase()
    db.entries = [entry]
    writer = BibTexWriter()
    bib = writer.write(db)

    authors = [item.strip() for item in entry['author'].split(" and ")]
    authors_str = ""
    for each in authors:
        authors_str += "\n  - "+each

    # port index.md
    entry = defaultdict(str, entry)
    tosave = template.format(
        title=entry["title"],
        year=entry["year"],
        month=entry["month"],
        authors=authors_str,
        abstract=entry["abstract"],
        publication=entry["journal"] or entry["booktitle"],
        doi=entry["doi"] or "",
        pdf=entry["pdf"] or entry["poster"] or entry["slides"],
        html=entry["html"],
        weight=idx+1
    ).replace("{{", "").replace("}}", "").replace("\&", "&")

    # save file
    fname = dir/"index.md"
    with fname.open("w", encoding="utf-8") as f:
        f.write(tosave)

    bibname = dir/"cite.bib"
    with bibname.open("w", encoding="utf-8") as f:
        f.write(bib)


@click.command()
@click.option('--bibfile', type=click.Path(file_okay=True, path_type=Path))
@click.option('--savedir', type=click.Path(dir_okay=True, path_type=Path))
def main(bibfile: Path, savedir: Path):
    with bibfile.open("r") as bibtex_file:
        parser = BibTexParser(common_strings=True)
        bib_database = bibtexparser.load(bibtex_file, parser=parser)

    entries = bib_database.entries
    # sort based on time

    def func(entry):
        year = int(entry["year"])
        month = strptime(entry["month"], '%B').tm_mon
        return (year, month)
    entries.sort(key=func, reverse=True)

    for idx, entry in enumerate(entries):
        convert_single(savedir, idx, entry)


if __name__ == "__main__":
    main()
