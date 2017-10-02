import argparse
import certifi
from gzipstream import GzipStreamFile
import os
import subprocess
import time
import urllib3
import warc


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description=__name__)
    parser.add_argument('--source-url', '-u',
        help='Remote URL to read input WARC file from.')
    parser.add_argument('--source-file', '-f',
        help='Local path to read input WARC file from.')
    parser.add_argument('--output-dir', '-o',
        help='Directory to write processed web pages to.')
    parser.add_argument('--max-pages', '-m', type=int,
        help='Maximum number of web pages to process from WARC file.')

    args = parser.parse_args()
    # Validate argumentsif(args.command in ['setup-pool'] and args.pool_directory == None):
    if not(args.source_file or args.source_url):
        parser.error("--source-file or --source-url argument must be provided.")

    # Make sure output directories exists
    original_pages_dir = os.path.join(args.output_dir, 'original')
    readable_pages_dir = os.path.join(args.output_dir, 'readable')
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    if not os.path.exists(original_pages_dir):
        os.makedirs(original_pages_dir)
    if not os.path.exists(readable_pages_dir):
        os.makedirs(readable_pages_dir)

    if args.source_file is not None:
        cf = open(args.source_file)
    elif args.source_url is not None:
        # Open a connection pool
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        # Open a streaming connection to the specified URL
        cf = http.request('GET', args.source_url, preload_content=False)

    # Wrap the filestream in a streamable unzipper
    f = warc.WARCFile(fileobj=GzipStreamFile(cf))
    warc_records = 0
    warc_responses = 0
    readable_pages = 0
    report_interval = 100

    start_time = time.time()
    for record in f:
        if record['WARC-Type'] == 'response':
            if (args.max_pages and warc_responses > args.max_pages):
                print("Reached maximum WARC responses ({})".format(args.max_pages))
                break
            warc_responses = warc_responses + 1
            try:
                id = record.header["WARC-Record-ID"][10:-1]
                fp = record.payload
                # Open file using WARC Record ID as filename
                original_page_path  = os.path.join(original_pages_dir, "{}.txt".format(id))
                readable_page_path = os.path.join(readable_pages_dir, "{}.txt".format(id))
                with open(original_page_path, 'w') as fout:
                    while True:
                        # Discard Header rows
                        line = fp.readline()
                        # Header rows are separated from page contents by a blank line
                        if line == "\r\n":
                            break
                    # Write page contents to file
                    fout.write(fp.read())
                # Process page with readability script
                subprocess.check_call(['node', 'page_to_readable_page.js',
                    original_page_path, readable_page_path])
                readable_pages = readable_pages + 1
                #  TODO: Persist file to blob storage and remove readable file
            except:
                pass
            # Clean up files created during processing
            try:
                os.remove(original_page_path)
            except:
                pass
            if warc_responses % report_interval == 0:
                print("Processed {} WARC pages ({} readable pages)".format(
                    warc_responses, readable_pages))

    print("Processed {} WARC pages ({} readable pages) in ".format(
        warc_responses, readable_pages, time.time() - start_time))

if __name__ == "__main__":
    main()
