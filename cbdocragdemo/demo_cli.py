##
##

import os
import argparse
from cbcmgr.cb_operation_s import CBOperation
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import CouchbaseVectorStore
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


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

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=1536)

    vectorstore = CouchbaseVectorStore(
        cluster=cluster,
        bucket_name=options.bucket,
        scope_name=options.scope,
        collection_name=options.collection,
        embedding=embeddings,
        index_name=index_name
    )

    retriever = vectorstore.as_retriever()

    llm = ChatOpenAI(temperature=0, model="gpt-4-1106-preview", streaming=True)

    template = """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. 
           If you don't know the answer, just say that you don't know. Use one or two paragraphs to answer the question.
           Question: {question}
           Context: {context}
           Answer:"""
    chat_prompt = ChatPromptTemplate.from_template(template)

    rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | chat_prompt
            | llm
            | StrOutputParser()
    )

    default = "What is the CLI command to add a node to a cluster"
    prompt = f"Question [enter=\"{default}\"]: "
    question = input(prompt)
    question = question.strip()
    if not question:
        question = default
    print("Answer:")
    for chunk in rag_chain.stream(question):
        print(chunk, end='')
    print("\n")


if __name__ == '__main__':
    main()
