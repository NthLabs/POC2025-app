import streamlit as st
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from poc_env import *

# My Variables
webTitle = "Private ChatBot"        # Title on Browser
logo = "images/NthLabs.png"         #
msgHistory = "messagesChat"         # This should be unique for each streamlit page

# LLMs and Embeddings
llm = ChatNVIDIA(
    base_url=f"http://{llm1Addr}/v1",
    api_key="FAKE",
    model=llm1Model,
    temperature=0.9)

# LangChain Functions
def no_rag(userInput):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful ChatBot {context}"),
        MessagesPlaceholder(variable_name="chatHistory"),
        ("user", "{userInput}"),
    ])
    stuffDocumentsChain = create_stuff_documents_chain(llm,prompt)

    response = stuffDocumentsChain.invoke({
        "chatHistory": getattr(st.session_state, msgHistory),
        "userInput": userInput,
        "context": "",
        }) #.content
    return response

def generate_response(userInput):
    with chatBox.chat_message('human'):
        st.markdown(userInput)
    getattr(st.session_state, msgHistory).append({"role": "human", "content": userInput})
    with chatBox.chat_message('assistant'):
        response = no_rag(userInput)
        st.write(response)
    getattr(st.session_state, msgHistory).append({"role": "assistant", "content": response})


#-------------------------------------------------------------
# Streamlit Stuff

st.set_page_config(page_title=webTitle)
st.image(logo, width=200)
st.divider()
chatBox = st.container(height=600)

# Session State
if str(msgHistory) not in st.session_state:
    setattr(st.session_state, msgHistory, [])

# Conversation
for message in getattr(st.session_state, msgHistory):
    with chatBox.chat_message(message["role"]):
        st.markdown(message["content"])
# Display new Q&A    
userInput = st.chat_input("Ask your question...")
if userInput != None and userInput != "":
    with st.spinner('Calculating the response...'):
        generate_response(userInput)

# Sidebar
if st.sidebar.button("Clear Chat History"):
    setattr(st.session_state, msgHistory, [])
    st.rerun()

