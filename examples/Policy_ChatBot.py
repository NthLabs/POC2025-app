# !pip install streamlit langchain langchain-nvidia-ai-endpoints langchain_community pypdf langchain-chroma

import streamlit as st
from langchain_nvidia_ai_endpoints import ChatNVIDIA, NVIDIAEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
import os, os.path
from datetime import datetime
import nthUtility
from poc_env import *


# My Variables
webTitle = "Policy ChatBot"

myDocs = "./data/policy"
vsPath = "./catalog/policy"
logFile = "./logs/policyPrompt.log"
logo = "images/NthLabs.png"

nthUtility.file_structure(myDocs)


# LLMs and Embeddings
llm = ChatNVIDIA(
    base_url=f"http://{llm1Addr}/v1",
    api_key="FAKE",
    model=llm1Model,
    temperature=0.9)

embedding = NVIDIAEmbeddings(
    base_url=f"http://{embedAddr}/v1",
    api_key="FAKE",
    model=embedModel,
    )


#-------------------------------------------------------------
# LangChain Workflow:
# Get VectorStore
# build context retriever chain (from Vectorstore)
# build conversational RAG chain (from retriever chain)
# get response 
#-------------------------------------------------------------
# LangChain Functions


def create_vectorstore():
    st.sidebar.markdown("Creating Vectorstore")
    loader = PyPDFDirectoryLoader(myDocs)
    documents = loader.load()
    st.sidebar.markdown(f"{len(documents)} document pages")

    # Chunk the data
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", ";", ",", " ", ""],
    )
    docChunks = text_splitter.split_documents(documents)
    st.sidebar.markdown(f"{len(docChunks)} chunks of data")
    
    vectorStore = Chroma.from_documents(
        documents=docChunks,
        embedding=embedding,
        persist_directory=vsPath,
    )
    st.sidebar.markdown("VectorStore Created")
    st.session_state.vectorStoreChroma1 = get_vectorstore()


def get_vectorstore():
    if not os.path.exists(vsPath):
        create_vectorstore()
    vectorStore = Chroma(
        embedding_function=embedding,
        persist_directory=vsPath,)
    return vectorStore


def regen_vectorstore():
    vectorStore = get_vectorstore()
    vectorStore.delete_collection()
    create_vectorstore()


# def log_prompt(userInput):
#     id = st.context.headers["Sec-Websocket-Key"]
#     timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
#     with open(logFile, "a") as promptLog:
#         promptLog.write(f"{timestamp},{id},{userInput}\n")


def get_context_retriever_chain(vectorStore):
    retriever = vectorStore.as_retriever(
        search_kwargs={"k": 2})
    prompt = ChatPromptTemplate.from_messages([
      MessagesPlaceholder(variable_name="chat_history"),
      ("user", "{input}"),
      ("user", """Given the above conversation, generate a search query to 
       look up in order to get information relevant to the conversation""")
    ])
    retrieverChain = create_history_aware_retriever(llm, retriever, prompt)
    return retrieverChain

def get_conversational_rag_chain(retrieverChain): 
    prompt = ChatPromptTemplate.from_messages([
      ("system", "Answer the user's questions based on the below context:\n\n{context}"),
      MessagesPlaceholder(variable_name="chat_history"),
      ("user", "{input}"),
    ])
    stuffDocumentsChain = create_stuff_documents_chain(llm,prompt)
    return create_retrieval_chain(retrieverChain, stuffDocumentsChain)
    
def get_response(userInput):
    retriever_chain = get_context_retriever_chain(st.session_state.vectorStoreChroma1)
    conversation_rag_chain = get_conversational_rag_chain(retriever_chain)
    response = conversation_rag_chain.invoke({
        "chat_history": st.session_state.messagesPol,
        "input": userInput
    })
    #return response
    responseString = response['answer']
    for doc in response['context']:
        responseString += '\n\n'
        responseString += doc.metadata['source']
        responseString += ' Page '
        responseString += str(doc.metadata['page'] + 1)
    return responseString
    
def generate_response(userInput):
    #log_prompt(userInput)
    nthUtility.log_prompt(userInput, logFile)
    with st.chat_message('human'):
        st.markdown(userInput)
    st.session_state.messagesPol.append({"role": "human", "content": userInput})
    with st.chat_message('assistant'):
        response = get_response(userInput)
        st.write(response)
    st.session_state.messagesPol.append({"role": "assistant", "content": response})

def clear_knowledgebase():
    for fileName in os.listdir(myDocs):
        filePath = os.path.join(myDocs, fileName)
        try:
            os.unlink(filePath)
        except:
            print("cannot delete")




#-------------------------------------------------------------
# Streamlit Stuff

st.set_page_config(page_title=webTitle)
st.image(logo, width=200)
st.divider()

# Sidebar
#st.sidebar.image("images/NthU.png", use_container_width=True)
st.sidebar.subheader("List of Files in Knowledgebase:")
st.sidebar.subheader(f"({myDocs})")
for file in os.listdir(myDocs):
    st.sidebar.markdown(file)
st.sidebar.divider()

password = st.sidebar.text_input("Password to manage knowledgebase:", type="password")

if password == adminPass:

    uploaded_files = st.sidebar.file_uploader(
        "Upload a file to the KnowledgeBase:", 
        type=['pdf'], 
        accept_multiple_files=True)
        
    if uploaded_files:
        for uploaded_file in uploaded_files:
            st.success(f"File {uploaded_file.name} uploaded successfully!")
            with open(os.path.join(myDocs, uploaded_file.name), "wb") as f:
                f.write(uploaded_file.read())
    
    st.sidebar.button('Remove All Files', on_click=clear_knowledgebase)
    st.sidebar.button('Regenerate VectorStore', on_click=regen_vectorstore)



# Session State
if "vectorStoreChroma1" not in st.session_state:
    if len(os.listdir(myDocs)) >= 1:
        st.session_state.vectorStoreChroma1 = get_vectorstore()
    else:
        st.write("It looks like there are no files in your knowledgebase. Please upload some PDFs before proceeding.")
            

if "messages" not in st.session_state:
    st.session_state.messagesPol = []

# Conversation
for message in st.session_state.messagesPol:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
# Display new Q&A    
userInput = st.chat_input("Ask your question...")
if userInput != None and userInput != "":
    generate_response(userInput)
