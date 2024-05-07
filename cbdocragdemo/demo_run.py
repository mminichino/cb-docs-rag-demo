##
##

from langchain_community.vectorstores import CouchbaseVectorStore
from langchain_openai import OpenAIEmbeddings
import os
import argparse
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from cbcmgr.cb_operation_s import CBOperation
from cbcmgr.exceptions import NotAuthorized


def parse_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-u', '--user', action='store', help="User Name", default="Administrator")
    parser.add_argument('-p', '--password', action='store', help="User Password")
    parser.add_argument('-h', '--host', action='store', help="Cluster Hostname")
    parser.add_argument('-b', '--bucket', action='store', help="Bucket", default="docdemo")
    parser.add_argument('-s', '--scope', action='store', help="Scope", default="data")
    parser.add_argument('-c', '--collection', action='store', help="Collection", default="vectors")
    parser.add_argument('-i', '--index', action='store', help="Index Name", default="docdemo_vector_index")
    parser.add_argument('-K', '--apikey', action='store', help="OpenAI API Key")
    options = parser.parse_args()
    return options


def main():
    options = parse_args()
    if "auth" not in st.session_state:
        st.session_state.auth = False

    st.set_page_config(
        page_title="Chat with docs.couchbase.com",
        page_icon="ð¤",
        layout="centered",
        initial_sidebar_state="auto",
        menu_items=None,
    )

    openai_api_key = options.apikey if options.apikey else os.environ.get("OPENAI_API_KEY")

    if not st.session_state.auth:
        host_name = st.text_input("Couchbase Server Hostname", options.host, autocomplete="on")
        user_name = st.text_input("Username", options.user)
        user_password = st.text_input("Enter password", options.password, type="password")
        open_api_key = st.text_input("Enter OpenAI API Key", openai_api_key, type="password")
        bucket_name = st.text_input("Bucket", options.bucket)
        scope_name = st.text_input("Scope", options.scope)
        collection_name = st.text_input("Collection", options.collection)
        index_name = st.text_input("Index Name", options.index)
        pwd_submit = st.button("Start Chat")

        if pwd_submit:
            try:
                keyspace = f"{bucket_name}.{scope_name}.{collection_name}"
                CBOperation(host_name, user_name, user_password, ssl=True).connect(keyspace)
            except NotAuthorized:
                st.error("Incorrect password")
            else:
                st.session_state.hostname = host_name
                st.session_state.username = user_name
                st.session_state.password = user_password
                st.session_state.bucket = bucket_name
                st.session_state.scope = scope_name
                st.session_state.collection = collection_name
                st.session_state.index = index_name
                st.session_state.key = open_api_key
                st.session_state.auth = True
                st.rerun()

    if st.session_state.auth:
        os.environ["OPENAI_API_KEY"] = st.session_state.key

        keyspace = f"{st.session_state.bucket}.{st.session_state.scope}.{st.session_state.collection}"
        op = CBOperation(st.session_state.hostname, st.session_state.username, st.session_state.password, ssl=True).connect(keyspace)
        cluster = op.cluster

        embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=1536)

        vectorstore = CouchbaseVectorStore(
            cluster,
            st.session_state.bucket,
            st.session_state.scope,
            st.session_state.collection,
            embeddings,
            st.session_state.index,
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

        couchbase_logo = (
            "https://raw.githubusercontent.com/mminichino/cb-docs-rag-demo/main/doc/couchbase.png"
        )
        openai_logo = (
            "https://raw.githubusercontent.com/mminichino/cb-docs-rag-demo/main/doc/openapi.png"
        )

        st.title("Chat with Couchbase Docs")

        with st.sidebar:
            st.write("View the code [here](https://github.com/mminichino/cb-docs-rag-demo/blob/main/cbdocragdemo/demo_run.py)")

            with st.container():
                col1, col2 = st.columns([0.25, 0.75], gap="small")

                col1.write(f"Version:")
                col2.write(op.sw_version)

                col1.write(f"Platform:")
                col2.write(op.os_platform)

                col1.write(f"Index:")
                col2.write(st.session_state.index)

                col1.write(f"Vectors:")
                col2.write(f"{op.search_index_count(st.session_state.index):,}")

        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "Welcome to Couchbase. How can I help you?",
                    "avatar": openai_logo,
                }
            )

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar=message["avatar"]):
                st.markdown(message["content"])

        # React to user input
        if question := st.chat_input("Ask a question"):
            # Display user message in chat message container
            st.chat_message("user").markdown(question)

            # Add user message to chat history
            st.session_state.messages.append(
                {"role": "user", "content": question, "avatar": openai_logo}
            )

            # Add placeholder for streaming the response
            with st.chat_message("assistant", avatar=couchbase_logo):
                message_placeholder = st.empty()

            # stream the response from the RAG
            rag_response = ""
            for chunk in rag_chain.stream(question):
                rag_response += chunk
                message_placeholder.markdown(rag_response + "â")

            message_placeholder.markdown(rag_response)
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": rag_response,
                    "avatar": couchbase_logo,
                }
            )


if __name__ == '__main__':
    main()
