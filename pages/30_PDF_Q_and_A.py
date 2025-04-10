# !pip install streamlit langchain langchain-nvidia-ai-endpoints langchain_community faiss-cpu pypdf

import streamlit as st
from langchain_nvidia_ai_endpoints import ChatNVIDIA, NVIDIAEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
import os, os.path
import nthUtility
from poc_env import *

# My Variables
webTitle = "PDF Q&A"                # Title on Browser
myDocs = "./data/pdfQA"             # Location for PDFs
logo = "images/NthLabs.png"         # 
msgHistory = "messagesPDF"          # This should be unique for each page
vsName = "vsPDF"                    # This should be unique for each Chroma instance

nthUtility.file_structure(myDocs)   # Setup File structure



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

def get_vectorstore():
    loader = PyPDFDirectoryLoader(myDocs)
    documents = loader.load()

    # Chunk the data
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", ";", ",", " ", ""],
    )
    docChunks = text_splitter.split_documents(documents)
    
    # Create VectorDB
    vectorStore = FAISS.from_documents(docChunks, embedding=embedding)
    return vectorStore

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
    retriever_chain = get_context_retriever_chain(getattr(st.session_state, vsName))
    conversation_rag_chain = get_conversational_rag_chain(retriever_chain)
    response = conversation_rag_chain.invoke({
        "chat_history": getattr(st.session_state, msgHistory),
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
    with st.chat_message('human'):
        st.markdown(userInput)
    getattr(st.session_state, msgHistory).append({"role": "human", "content": userInput})
    with st.chat_message('assistant'):
        response = get_response(userInput)
        st.write(response)
    getattr(st.session_state, msgHistory).append({"role": "assistant", "content": response})

#-------------------------------------------------------------
# Streamlit Stuff

st.set_page_config(page_title=webTitle)
st.image(logo, width=200)
st.divider()

# Sidebar
st.sidebar.subheader("List of Files in Knowledgebase:")
for file in os.listdir(myDocs):
    st.sidebar.markdown(file)
st.sidebar.divider()

uploaded_files = st.sidebar.file_uploader(
    "Upload a file to the KnowledgeBase:", 
    type=['pdf'], 
    accept_multiple_files=True)
    
if uploaded_files:
    for uploaded_file in uploaded_files:
        st.success(f"File {uploaded_file.name} uploaded successfully!")
        with open(os.path.join(myDocs, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.read())

# Session State
if str(vsName) not in st.session_state:
        if len(os.listdir(myDocs)) >= 1:
            setattr(st.session_state, vsName, get_vectorstore())
        else:
            st.write("It looks like there are no files in your knowledgebase. Please upload some PDFs before proceeding.")
            
if str(msgHistory) not in st.session_state:
    setattr(st.session_state, msgHistory, [])

# Conversation
for message in getattr(st.session_state, msgHistory):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    
# Display new Q&A    
userInput = st.chat_input("Ask your question...")
if userInput != None and userInput != "":
    generate_response(userInput)
