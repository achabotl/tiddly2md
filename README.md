# TiddlyWiki converter

Converts a TiddlyWiki to individual markdown files. 

## Requirements

- pandas (for reading the CSV files)

## Instructions

1. Install the [ExportTiddlersPlugin](http://www.tiddlytools.com/#ExportTiddlersPlugin).
2. Export wiki as CSV file.
3. Run `tiddly2md.py` on the CSV file.

	python tiddly2md.py export.csv

See `-h` for options.

	python tiddly2md.py -h
	
## Options worth discussing

You can export only specific tags by using the `-t TAG` option. The tiddlers will be exported if the `TAG` text is part of the tiddler's tags. For example, the option `-t author` would export tiddlers that have the tag "author:name". Multiple values of `-t` options can be used to export multiple tags at once:
	
	python tiddly2md.py -t author -t concept export.csv


