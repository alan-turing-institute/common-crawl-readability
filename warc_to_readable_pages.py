import argparse
import certifi
from gzipstream import GzipStreamFile
import os
import urllib3
import warc

DEFAULT_MAX_PAGES = 50

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description=__name__)
    parser.add_argument('--input-url', '-i',
        help='Path to read input WARC file from.')
    parser.add_argument('--output-dir', '-o',
        help='Directory to write processed web pages to.')
    parser.add_argument('--max-pages', '-m',
        help='Maximum number of web pages to process from WARC file.')

    args = parser.parse_args()

    if args.max_pages is None:
        args.max_pages = DEFAULT_MAX_PAGES

    # Make sure output directory exists
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # Open a connection pool
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    # Open a streaming connection to the specified URL
    r = http.request('GET', args.input_url, preload_content=False)
    # Wrap the URL filestream in a streamable unzipper
    f = warc.WARCFile(fileobj=GzipStreamFile(r))
    count = 0
    for record in f:
        if record['WARC-Type'] == 'response':
            count = count + 1
            id = record.header["WARC-Record-ID"][10:-1]
            fp = record.payload
            # Open file using WARC Record ID as filenamea
            out_path = os.path.join(args.output_dir, id)
            with open("/Users/moreilly/commoncrawl/temp/{}.txt".format(id), 'w') as fout:
                while True:
                    # Discart Header rows
                    line = fp.readline()
                    # Header rows are separated from page contents by a blank line
                    if line == "\r\n":
                        break
                # Write page contents to file
                fout.write(fp.read())
        if count > args.max_pages:
            break


if __name__ == "__main__":
    main()
