##
##

from langchain_community.vectorstores import CouchbaseVectorStore
from langchain_openai import OpenAIEmbeddings
import os
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from cbcmgr.cb_operation_s import CBOperation
from cbcmgr.exceptions import NotAuthorized


def main():
    if "auth" not in st.session_state:
        st.session_state.auth = False

    st.set_page_config(
        page_title="Chat with docs.couchbase.com",
        page_icon="ð¤",
        layout="centered",
        initial_sidebar_state="auto",
        menu_items=None,
    )

    if not st.session_state.auth:
        host_name = st.text_input("Couchbase Server Hostname", "127.0.0.1")
        user_name = st.text_input("Username", "Administrator")
        user_password = st.text_input("Enter password", type="password")
        open_api_key = st.text_input("Enter OpenAI API Key", type="password")
        bucket_name = st.text_input("Bucket", "docdemo")
        scope_name = st.text_input("Scope", "data")
        collection_name = st.text_input("Collection", "vectors")
        index_name = st.text_input("Index Name", "docdemo_vector_index")
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

        # Frontend
        couchbase_logo = (
            "https://raw.githubusercontent.com/mminichino/cb-rag-langchain-demo/main/doc/couchbase.png"
        )
        openai_logo = (
            "https://raw.githubusercontent.com/mminichino/cb-rag-langchain-demo/main/doc/openapi.png"
        )

        st.title("Chat with Couchbase Docs")

        with st.sidebar:
            # View Code
            if st.checkbox("View Code"):
                st.write(
                    "View the code here: [Github](https://github.com/mminichino/cb-rag-langchain-demo/blob/main/cbragdemo/chat_with_pdf.py)"
                )

        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "I'm a chatbot who can chat with Couchbase documentation. How can I help you?",
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