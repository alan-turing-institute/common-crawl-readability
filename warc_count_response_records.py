import argparse
import arrow
import certifi
from gzipstream import GzipStreamFile
import os
import subprocess
import urllib3
import warc


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description=__name__)
    parser.add_argument('--source-url', '-u',
        help='Remote URL to read input WARC file from.')
    parser.add_argument('--source-file', '-f',
        help='Local path to read input WARC file from.')

    args = parser.parse_args()
    # Validate argumentsif(args.command in ['setup-pool'] and args.pool_directory == None):
    if not(args.source_file or args.source_url):
        parser.error("--source-file or --source-url argument must be provided.")

    if args.source_file is not None:
        source_string = args.source_file
        cf = open(args.source_file)
    elif args.source_url is not None:
        source_string = args.source_url
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

    start_time = arrow.utcnow()
    for record in f:
        if record['WARC-Type'] == 'response':
            warc_responses = warc_responses + 1
    end_time = arrow.utcnow()
    elapsed_time = end_time - start_time
    print("{} response records in file {} ()".format(warc_responses, source_string,
        elapsed_time))


if __name__ == "__main__":
    main()
