# Readable Common Crawl
Scripts for processing common crawl web content through Mozilla readability.js

## Usage
`python warc_to_readable_pages.py (-f <path-to-warc.gz> | -u <url-to-warc.gz>) -o <output-directory>`

Constraints:
- URL or local path refers to a gzipped WARC file
- The response contents are extracted from each WARC record in the file and
written to disk as one file per page with response headers stripped
- Output files are named `<WARC-Record-ID>.txt`. The `.txt` extension allows
easy inspection using the default text editor. A `.html` extension was
deliberately avoided due to the likelihood that some pages contain malware and
therefore opening pages in a browser would be a bad idea.
