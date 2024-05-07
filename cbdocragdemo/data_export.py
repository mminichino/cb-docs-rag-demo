##
##

import argparse
import cbdocragdemo
from cbcmgr.cb_stream_export import StreamExport

VERSION = cbdocragdemo.__version__


def parse_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-u', '--user', action='store', help="User Name", default="Administrator")
    parser.add_argument('-p', '--password', action='store', help="User Password", default="password")
    parser.add_argument('-h', '--host', action='store', help="Cluster Node Name", default="localhost")
    parser.add_argument('-b', '--bucket', action='store', help="Bucket", default="docdemo")
    parser.add_argument('-s', '--scope', action='store', help="Scope", default="data")
    parser.add_argument('-c', '--collection', action='store', help="Collection", default="vectors")
    parser.add_argument('-f', '--file', action='store', help="Data File")
    options = parser.parse_args()
    return options


def main():
    options = parse_args()
    keyspace = f"{options.bucket}.{options.scope}.{options.collection}"
    file_name = options.file if options.file else f"{options.bucket}-{VERSION}.gz"
    stream = StreamExport(options.host, options.user, options.password, ssl=True, keyspace=keyspace, file_name=file_name)
    stream.stream_out()


if __name__ == '__main__':
    main()
