import streamlit as st
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from poc_env import *

# My Variables
webTitle = "Refine Text"            # Title on Browser
logo = "images/NthLabs.png"         # 
msgHistory = "messagesRefine2"      # This should be unique for each streamlit page

systemPrompt = 'Please provide three alternate examples of the following text'

# LLMs and Embeddings
llm = ChatNVIDIA(
    base_url=f"http://{llm1Addr}/v1",
    api_key="FAKE",
    model=llm1Model,
    temperature=0.9)

# LangChain Functions
def no_rag(userInput):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "{systemPrompt}{context}"),
        ("user", "{userInput}"),
    ])
    stuffDocumentsChain = create_stuff_documents_chain(llm,prompt)

    response = stuffDocumentsChain.invoke({
        "systemPrompt": systemPrompt,
        "userInput": userInput,
        "context": "",
        })
    return response

def generate_response(userInput):
    response = no_rag(userInput)
    st.markdown(response)

#-------------------------------------------------------------
# Streamlit Stuff

st.set_page_config(page_title=webTitle)
st.image(logo, width=200)
st.divider()

with st.form('my_form'):
    userInput = st.text_area('Enter text below and get 3 examples of similar text in return:', 
                        placeholder = 'Type or paste your text here',
                        height = 200)
    submitted = st.form_submit_button('Submit')
    if submitted:
        with st.spinner('Calculating the response...'):
            generate_response(userInput)
