##
##

import os
import argparse
from cbcmgr.cb_operation_s import CBOperation
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import CouchbaseVectorStore
from langchain_community.document_loaders.sitemap import SitemapLoader


def parse_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-u', '--user', action='store', help="User Name", default="Administrator")
    parser.add_argument('-p', '--password', action='store', help="User Password", default="password")
    parser.add_argument('-h', '--host', action='store', help="Cluster Node Name", default="localhost")
    parser.add_argument('-b', '--bucket', action='store', help="Bucket", default="docdemo")
    parser.add_argument('-s', '--scope', action='store', help="Scope", default="data")
    parser.add_argument('-c', '--collection', action='store', help="Collection", default="vectors")
    parser.add_argument('-i', '--index', action='store', help="Index Name", default="docdemo_vector_index")
    parser.add_argument('-K', '--apikey', action='store', help="OpenAI API Key")
    options = parser.parse_args()
    return options


def main():
    options = parse_args()
    if not options.apikey and 'OPENAI_API_KEY' not in os.environ:
        raise RuntimeError("OpenAI API Key not provided")

    keyspace = f"{options.bucket}.{options.scope}.{options.collection}"
    index_name = options.index
    openai_api_key = options.apikey if options.apikey else os.environ["OPENAI_API_KEY"]
    op = CBOperation(options.host, options.user, options.password, ssl=True).connect(keyspace)

    cluster = op.cluster
    os.environ["OPENAI_API_KEY"] = openai_api_key

    loader = SitemapLoader(web_path="https://docs.couchbase.com/sitemap.xml")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)
    splits = text_splitter.split_documents(loader.load())

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=1536)

    CouchbaseVectorStore.from_documents(
        documents=splits,
        cluster=cluster,
        bucket_name=options.bucket,
        scope_name=options.scope,
        collection_name=options.collection,
        embedding=embeddings,
        index_name=index_name
    )


if __name__ == '__main__':
    main()
