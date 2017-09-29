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
    parser.add_argument('--source-url', '-u',
        help='Remote URL to read input WARC file from.')
    parser.add_argument('--source-file', '-f',
        help='Local path to read input WARC file from.')
    parser.add_argument('--output-dir', '-o',
        help='Directory to write processed web pages to.')
    parser.add_argument('--max-pages', '-m',
        help='Maximum number of web pages to process from WARC file.')

    args = parser.parse_args()
    # Validate argumentsif(args.command in ['setup-pool'] and args.pool_directory == None):
    if not(args.source_file or args.source_url):
        parser.error("--source-file or --source-url argument must be provided.")

    if args.max_pages is None:
        args.max_pages = DEFAULT_MAX_PAGES

    # Make sure output directory exists
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    if args.source_file is not None:
        cf = open(args.source_file)
    elif args.source_url is not None:
        # Open a connection pool
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        # Open a streaming connection to the specified URL
        cf = http.request('GET', args.source_url, preload_content=False)
    # Wrap the filestream in a streamable unzipper
    f = warc.WARCFile(fileobj=GzipStreamFile(cf))
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
