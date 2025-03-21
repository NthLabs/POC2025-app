import streamlit as st
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from poc_env import *


st.set_page_config(
    page_title="Chat",)
st.image("images/NthLabs.png", width=200)
st.divider()
chatBox = st.container(height=750)

llm = ChatNVIDIA(
    base_url=f"http://{llm1Addr}/v1",
    api_key="FAKE",
    model=llm1Model,
    temperature=0.9)

def no_rag(userInput):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful ChatBot {context}"),
        MessagesPlaceholder(variable_name="chatHistory"),
        ("user", "{userInput}"),
    ])
    stuffDocumentsChain = create_stuff_documents_chain(llm,prompt)

    response = stuffDocumentsChain.invoke({
        "chatHistory": st.session_state.chatMessages3,
        "userInput": userInput,
        "context": "",
        }) #.content
    return response


def generate_response(userInput):
    with chatBox.chat_message('human'):
        st.markdown(userInput)
    st.session_state.chatMessages3.append({"role": "human", "content": userInput})
    with chatBox.chat_message('assistant'):
        response = no_rag(userInput)
        st.write(response)
    st.session_state.chatMessages3.append({"role": "assistant", "content": response})





# Session State
if "chatMessages" not in st.session_state:
    st.session_state.chatMessages3 = []




# Conversation
for message in st.session_state.chatMessages3:
    with chatBox.chat_message(message["role"]):
        st.markdown(message["content"])
# Display new Q&A    
userInput = st.chat_input("Ask your question...")
if userInput != None and userInput != "":
    with st.spinner('Calculating the response...'):
        generate_response(userInput)

# Sidebar
if st.sidebar.button("Clear Chat History"):
    st.session_state.chatMessages3 = []
    st.rerun()

